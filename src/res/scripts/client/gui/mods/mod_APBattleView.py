# -*- coding: utf-8 -*-
# type: ignore
"""Simple Label -- the smallest possible in-battle Gameface overlay.

Shows armor/prob/angle text over the battle HUD, for the length of the battle.
Deliberately skips everything a real mod would want (settings, positioning,
re-entrancy guards) to keep the res_map -> ViewModel -> View -> Window ->
battle-lifecycle -> JS pipeline visible with nothing else in the way.

Python 2.7 (BigWorld) runtime. OpenWG GameFace is a hard dependency.
"""

from debug_utils import LOG_CURRENT_EXCEPTION

from frameworks.wulf import (
    ViewModel,
    ViewSettings,
    ViewFlags,
    WindowFlags,
    WindowLayer,
    PositionAnchor,
)
from gui.impl.pub import ViewImpl, WindowImpl
from openwg_gameface import ModDynAccessor

_FAR = 1 << 20  # sentinel outside any real screen -- move() clamps to the true edge

# Must match the "itemID" in mods/configs/res_map/SimpleLabelView.json.
RES_MAP_ITEM_ID = "APBattleView"


# --- the data channel ---------------------------------------------------------


class APBattleVM(ViewModel):
    """Five string properties: the label's text, its color, and its visibility.
    Read-only (JS never writes back). visible is a string, not a bool property
    type, to stay on the one property primitive already proven to work in
    this stack -- see setVisible for the bool->string encoding."""

    def __init__(self):
        super(APBattleVM, self).__init__(properties=5, commands=0)

    def _initialize(self):
        super(APBattleVM, self)._initialize()
        self._addStringProperty("armorText", "")  # index 0
        self._addBoolProperty("armorVisible", False)  # 1
        self._addStringProperty("armorColor", "000000")  # 2

        self._addStringProperty("probText", "")  # index 3
        self._addBoolProperty("probVisible", False)  # 4
        self._addStringProperty("probColor", "000000")  # 5

        self._addStringProperty("angleText", "")  # index 6
        self._addBoolProperty("angleVisible", False)  # 7
        self._addStringProperty("angleColor", "000000")  # 8

    def setArmor(self, text, visible, color):
        self._setString(0, text)
        self._setBool(1, visible)
        self._setString(2, color)

    def setArmorText(self, text):
        self._setString(0, text)

    def setArmorVisible(self, visible):
        self._setBool(1, visible)

    def setArmorColor(self, color):
        self._setString(2, color)

    def setProb(self, text, visible, color):
        self._setString(3, text)
        self._setBool(4, visible)
        self._setString(5, color)

    def setProbText(self, text):
        self._setString(3, text)

    def setProbVisible(self, visible):
        self._setBool(4, visible)

    def setProbColor(self, color):
        self._setString(5, color)

    def setAngle(self, text, visible, color):
        self._setString(6, text)
        self._setBool(7, visible)
        self._setString(8, color)

    def setAngleText(self, text):
        self._setString(6, text)

    def setAngleVisible(self, visible):
        self._setBool(7, visible)

    def setAngleColor(self, color):
        self._setString(8, color)


# --- the page + the window it lives in -----------------------------------------


class APBattleView(ViewImpl):
    """The registered Gameface view. Its root ViewModel IS our APBattleView --
    the JS reads it with a bare ModelObserver(), no nested submodel."""

    _layoutID = ModDynAccessor(RES_MAP_ITEM_ID)  # deferred: -1 until OpenWG resolves it

    def __init__(self):
        super(APBattleView, self).__init__(
            ViewSettings(self._layoutID(), ViewFlags.VIEW, APBattleVM())
        )

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(APBattleView, self)._onLoading(*args, **kwargs)
        # The page just finished loading -- push once so it paints immediately
        # instead of sitting blank until something else triggers a refresh.
        # push(self.viewModel, "", "", "")


class APBattleWindow(WindowImpl):
    """Content-sized (NOT full-screen) so its rectangle can't hit-test across the
    whole HUD, layer WINDOW (not OVERLAY) so it never sits above the modal
    in-battle menu. See battle_view.py in the real mod for the long version.

    Centered on screen by default, offset by (x, y) logical px from that center."""

    def __init__(self, content, x=0, y=0):
        super(APBattleWindow, self).__init__(
            WindowFlags.WINDOW, content=content, layer=WindowLayer.WINDOW
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
        # Self-calibrate: move to a sentinel far off-screen, then read back the
        # clamped position, which equals the movable extent (screenSpace - windowSize).
        self.move(_FAR, _FAR, xAnchor=PositionAnchor.LEFT, yAnchor=PositionAnchor.TOP)
        max_x, max_y = self.position
        self.move(
            max_x / 2 + self._x,
            max_y / 2 + self._y,
            xAnchor=PositionAnchor.LEFT,
            yAnchor=PositionAnchor.TOP,
        )


# --- push -----------------------------------------------------------------------


def update_gameface(
    armor_text=None,
    armor_visible=None,
    armor_color=None,
    prob_text=None,
    prob_visible=None,
    prob_color=None,
    angle_text=None,
    angle_visible=None,
    angle_color=None,
):
    """Public API: call from anywhere (e.g. the armor-pen calc mod) to redraw
    the label with fresh values. No-op if the window isn't open."""
    if _active is None:
        return
    _window, view = _active
    push(
        view.viewModel,
        armor_text,
        armor_visible,
        armor_color,
        prob_text,
        prob_visible,
        prob_color,
        angle_text,
        angle_visible,
        angle_color,
    )


def push(
    view_model,
    armor_text=None,
    armor_visible=None,
    armor_color=None,
    prob_text=None,
    prob_visible=None,
    prob_color=None,
    angle_text=None,
    angle_visible=None,
    angle_color=None,
):
    """Write the label's fields into view_model."""
    if view_model is None:
        return
    with view_model.transaction() as tx:
        if armor_text is not None:
            tx.setArmorText(armor_text)
        if armor_visible is not None:
            tx.setArmorVisible(armor_visible)
        if armor_color is not None:
            tx.setArmorColor(armor_color)

        if prob_text is not None:
            tx.setProbText(prob_text)
        if prob_visible is not None:
            tx.setProbVisible(prob_visible)
        if prob_color is not None:
            tx.setProbColor(prob_color)

        if angle_text is not None:
            tx.setAngleText(angle_text)
        if angle_visible is not None:
            tx.setAngleVisible(angle_visible)
        if angle_color is not None:
            tx.setAngleColor(angle_color)


# --- open/close, tied to the battle lifecycle ------------------------------------

_active = None  # (window, view) while open, else None


def open_window(x=0, y=0):
    """x, y: offset in logical px from screen center (positive = right/down)."""
    global _active
    if _active is not None:
        return
    layout = APBattleView._layoutID()
    if layout is None or layout < 0:
        # res_map not registered yet -- ships fine, just needs the one-time
        # client restart OpenWG triggers the first time it rebuilds res_map.json.
        return
    view = APBattleView()
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


def _install():
    import openwg_gameface  # noqa: F401  -- hard dependency, raises if absent
    from PlayerEvents import g_playerEvents

    # Global arena hooks: persist across battles, unlike per-battle controllers.
    g_playerEvents.onAvatarReady += _on_avatar_ready
    g_playerEvents.onAvatarBecomeNonPlayer += _on_avatar_teardown


try:
    _install()
except Exception:
    LOG_CURRENT_EXCEPTION()
