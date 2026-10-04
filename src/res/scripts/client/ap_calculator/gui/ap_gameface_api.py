"""Simple Label -- the smallest possible in-battle Gameface overlay.

Shows armor/prob/angle text over the battle HUD, for the length of the battle.
Deliberately skips everything a real mod would want (settings, positioning,
re-entrancy guards) to keep the gen_resources -> ViewModel -> View -> Window ->
battle-lifecycle -> JS pipeline visible with nothing else in the way.

Python 2.7 (BigWorld) runtime, WoT 2.4.1+. The view is registered natively by
the client from gui/gen_resources/ap_calculator_2.json -- OpenWG GameFace is
only needed on the JS side (APBattleView.js imports its libs/model.js).
"""

from debug_utils import LOG_CURRENT_EXCEPTION  # type: ignore
from frameworks.wulf import (  # type: ignore
    PositionAnchor,
    ViewFlags,
    ViewModel,
    ViewSettings,
    WindowFlags,
    WindowLayer,
)
from gui.impl.gen import R  # type: ignore
from gui.impl.pub import ViewImpl, WindowImpl  # type: ignore


# Must match the "R.mods.<RES_MOD_ID>.views.APBattleView" id declared in
# gui/gen_resources/ap_calculator_2.json.
RES_MOD_ID = "ap_calculator_2"
INVALID_RES_ID = -1


def _layout_id():
    """Numeric layoutID of our view, or INVALID_RES_ID if the client didn't load
    the gen_resources declaration (pre-2.4.1 client, or the file isn't deployed).
    Looked up at open time, never cached across runs -- numeric IDs can change
    between client launches."""
    # dyn() at every step: plain attribute access raises AttributeError when a
    # node is missing (possibly even R.mods, if no mod declared anything).
    node = R
    for name in ("mods", RES_MOD_ID, "views", "APBattleView"):
        node = node.dyn(name)
        if not node:
            return INVALID_RES_ID
    return node()


# --- the data channel ---------------------------------------------------------


class APBattleVM(ViewModel):
    """Five string properties: the label's text, its color, and its visibility.
    Read-only (JS never writes back). visible is a string, not a bool property
    type, to stay on the one property primitive already proven to work in
    this stack -- see setVisible for the bool->string encoding."""

    def __init__(self):
        super(APBattleVM, self).__init__(properties=10, commands=0)

    def _initialize(self):
        super(APBattleVM, self)._initialize()
        params = [
            ("armorText", ""),
            ("armorVisible", False),
            ("armorColor", "000000"),
            ("probText", ""),
            ("probVisible", False),
            ("probColor", "000000"),
            ("angleText", ""),
            ("angleVisible", False),
            ("angleColor", "000000"),
            ("trackVisible", False),
            ("backgroundEnabled", True),
        ]

        # we will now register these parameters
        self.param_registry = {}
        self.param_values = {}
        for index, (param_name, default_value) in enumerate(params):
            self.param_registry[param_name] = [
                index,
                type(default_value),
                default_value,
            ]
            self.param_values[param_name] = default_value

            param_type = type(default_value)
            if param_type == str:
                self._addStringProperty(param_name, default_value)
            elif param_type == bool:
                self._addBoolProperty(param_name, default_value)
            else:
                raise TypeError(
                    "Parameter type is expected to be str or bool. Got: {}".format(
                        param_type
                    )
                )

    def set_param(self, name, value, use_cache=True):
        """
        Updates parameter named `name`. If use_cache is `True`,
        then no change is sent if the parameter remains the same.
        """
        index = self.param_registry[name][0]
        param_type = self.param_registry[name][1]
        existing_value = self.param_values[name]

        if type(value) != param_type:
            raise TypeError(
                "Type of value expected to be {}. Got: {}".format(param_type, value)
            )

        if use_cache and value == existing_value:
            return

        if param_type == str:
            self._setString(index, value)
        elif param_type == bool:
            self._setBool(index, value)
        else:
            raise TypeError("Parameter type is unrecognized: {}".format(param_type))

        self.param_values[name] = value


# --- the page + the window it lives in -----------------------------------------


class APBattleView(ViewImpl):
    """The registered Gameface view. Its root ViewModel IS our APBattleView --
    the JS reads it with a bare ModelObserver(), no nested submodel."""

    def __init__(self, layout_id):
        super(APBattleView, self).__init__(
            ViewSettings(layout_id, ViewFlags.VIEW, APBattleVM())
        )

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(APBattleView, self)._onLoading(*args, **kwargs)


class APBattleWindow(WindowImpl):
    """Content-sized (NOT full-screen) so its rectangle can't hit-test across the
    whole HUD, layer WINDOW (not OVERLAY) so it never sits above the modal
    in-battle menu. See battle_view.py in the real mod for the long version.

    Centered on screen by default, offset by (x, y) logical px from that center."""

    def __init__(self, content, x=0, y=0):
        super(APBattleWindow, self).__init__(
            WindowFlags.WINDOW, content=content, layer=WindowLayer.HIDDEN_SERVICE_LAYOUT
        )
        self._x = x
        self._y = y
        # windowSize may not be final yet at _onReady (e.g. still waiting on the
        # 256x256 "Size calculation timeout" fallback) -- recenter once it settles.
        self.onSizeChanged += self._center

    def _onReady(self):
        self.show(focus=False)  # never steal battle input/focus
        self._center()

    def _center(self, *args, **kwargs):
        # Native centering (WindowImpl.center -> area.centerPyWindow), the same
        # call WG's own windows use after show(). Then nudge by the offset from
        # the centered top-left corner, if there is one.
        self.center()
        if self._x or self._y:
            cx, cy = self.position
            self.move(
                cx + self._x,
                cy + self._y,
                xAnchor=PositionAnchor.LEFT,
                yAnchor=PositionAnchor.TOP,
            )


# --- push -----------------------------------------------------------------------


def update_gameface(params):
    """Public API: call from anywhere (e.g. the armor-pen calc mod) to redraw
    the label with fresh values. No-op if the window isn't open."""
    if _active is None:
        return
    _window, view = _active
    view_model = view.viewModel

    if view_model is None:
        return
    with view_model.transaction() as tx:
        for param_name, value in params:
            tx.set_param(param_name, value)


# --- open/close, tied to the battle lifecycle ------------------------------------

_active = None  # (window, view) while open, else None


def open_window(x=0, y=0):
    """x, y: offset in logical px from screen center (positive = right/down)."""
    global _active
    if _active is not None:
        return
    layout = _layout_id()
    if layout < 0:
        # gen_resources declaration not loaded -- nothing to open.
        return
    view = APBattleView(layout)
    window = APBattleWindow(view, x=x, y=y)
    _active = (window, view)
    window.load()


def close_window():
    global _active
    if _active is None:
        return
    window, _view = _active
    _active = None
    window.destroy()


def _on_avatar_ready(*args, **kwargs):
    try:
        open_window()
    except Exception:
        LOG_CURRENT_EXCEPTION()


def _on_avatar_teardown(*args, **kwargs):
    try:
        close_window()
    except Exception:
        LOG_CURRENT_EXCEPTION()
