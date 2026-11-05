"""Gameface plumbing for the in-battle armor/prob/angle overlay.

GamefaceWindow owns one overlay window and the list of named parameters
(name, default value) that form the whole Python -> JS contract. The rest of
the mod only calls my_window.open_window() / update_params() / close_window();
APBattleVM, APBattleView and APBattleWindow are the Wulf pieces underneath.

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


def _layout_id(mod_name_id):
    """Numeric layoutID of our view, or INVALID_RES_ID if the client didn't load
    the gen_resources declaration (pre-2.4.1 client, or the file isn't deployed).
    Looked up at open time, never cached across runs -- numeric IDs can change
    between client launches."""
    # dyn() at every step: plain attribute access raises AttributeError when a
    # node is missing (possibly even R.mods, if no mod declared anything).
    node = R
    for name in ("mods", mod_name_id, "views", "APBattleView"):
        node = node.dyn(name)
        if not node:
            return INVALID_RES_ID
    return node()


class GamefaceWindow(object):
    """One Gameface overlay window plus a cache of the values last sent to it.

    params: list of (name, default_value) pairs. Each default's type (str or
    bool) fixes that parameter's property type, and its position in the list
    is its property index in APBattleVM. The JS reads them by name.
    name: the res_map itemID the view is registered under."""

    def __init__(self, params, name):
        self.params = params
        self.name = name

        self.param_registry = {}
        self.param_values = None  # None for now because it hasnt been initialized yet

        self._active = None
        self._layoutID = lambda: _layout_id(name)

        for index, (param_name, default_value) in enumerate(self.params):
            param_type = type(default_value)
            self.param_registry[param_name] = [
                index,
                param_type,
                default_value,
            ]

    def open_window(self):
        """Create and load the window, centered on screen, with every parameter
        at its default. No-op if already open, or if OpenWG hasn't resolved
        the res_map entry yet."""
        if self._active is not None:
            return

        layout = self._layoutID()
        if layout is None or layout < 0:
            # res_map not registered yet -- ships fine, just needs the one-time
            # client restart OpenWG triggers the first time it rebuilds res_map.json.
            return
        view = APBattleView(self.params, self._layoutID())
        window = APBattleWindow(view)
        self._active = (window, view)
        self.param_values = {
            param_name: default_value for param_name, default_value in self.params
        }
        window.load()

    def update_params(self, updated_params):
        """Push new values to the window in one transaction.

        updated_params: list of (name, value) pairs. Values equal to the last
        one sent are skipped. Raises TypeError if a value's type doesn't match
        that parameter's default. No-op while the window is closed."""
        if self._active is None:
            return
        _window, view = self._active
        view_model = view.viewModel

        if view_model is None or self.param_values is None:
            return

        payload = []  # list of (index, type, new_value)

        for param_name, new_value in updated_params:
            param_type = self.param_registry[param_name][1]
            if type(new_value) != param_type:
                raise TypeError(
                    "Type of value expected to be {}. Got: {}".format(
                        param_type, type(new_value)
                    )
                )
            elif new_value != self.param_values[param_name]:
                self.param_values[param_name] = new_value
                index = self.param_registry[param_name][0]
                payload.append((index, param_type, new_value))

        if not payload:
            return
        with view_model.transaction() as tx:
            for index, param_type, value in payload:
                tx.set_param(index, param_type, value)

    def close_window(self):
        """Destroy the window and drop the value cache. No-op if not open."""
        if self._active is None:
            return
        window, _view = self._active
        self._active = None
        self.param_values = None
        window.destroy()


# --- the data channel ---------------------------------------------------------


class APBattleVM(ViewModel):
    """Root ViewModel: one string or bool property per (name, default) pair in
    params, added in list order so each property's index is its position in
    the list. Read-only (JS never writes back)."""

    def __init__(self, params):
        self.params = params
        super(APBattleVM, self).__init__(properties=len(params), commands=0)

    def _initialize(self):
        super(APBattleVM, self)._initialize()

        # we will now register these parameters
        for index, (param_name, default_value) in enumerate(self.params):
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

    def set_param(self, index, param_type, value):
        """Write one property by index. Does no type or change checking --
        GamefaceWindow.update_params does that before calling this."""

        if param_type == str:
            self._setString(index, value)
        elif param_type == bool:
            self._setBool(index, value)
        else:
            raise TypeError("Parameter type is unrecognized: {}".format(param_type))


# --- the page + the window it lives in -----------------------------------------


class APBattleView(ViewImpl):
    """The registered Gameface view. Its root ViewModel is an APBattleVM built
    from params -- the JS reads it with a bare ModelObserver(), no nested
    submodel."""

    def __init__(self, params, layout_id):
        super(APBattleView, self).__init__(
            ViewSettings(layout_id, ViewFlags.VIEW, APBattleVM(params))
        )

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(APBattleView, self)._onLoading(*args, **kwargs)


class APBattleWindow(WindowImpl):
    """Content-sized (NOT full-screen) so its rectangle can't hit-test across the
    whole HUD. Shown without focus so it never steals battle input.

    Centered on screen, offset by (x, y) logical px from that center."""

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


ap_window = GamefaceWindow(
    [
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
    ],
    RES_MOD_ID,
)
