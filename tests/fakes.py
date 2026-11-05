"""Hand-written stand-ins for the game client modules the mod imports.

install() puts them in sys.modules so the mod's own modules import outside the
client. They are deliberately minimal: just the names the mod (and the stock
gun_marker_ctrl.py loaded by stock.py) touch, plus recording hooks the tests
assert on. Anything else the stock file imports is served by stock.py's
auto-stub importer.
"""

import collections
import sys
import types


def _module(name, **attrs):
    module = types.ModuleType(name)
    # every fake can act as a package, so `from fake import submodule` reaches
    # stock.py's auto-stub importer instead of failing outright
    module.__path__ = []
    module.__dict__.update(attrs)
    sys.modules[name] = module
    parent_name, _, child = name.rpartition(".")
    if parent_name:
        parent = sys.modules.get(parent_name) or _module(parent_name)
        if not hasattr(parent, "__path__"):
            parent.__path__ = []
        setattr(parent, child, module)
    return module


# --- PlayerEvents -------------------------------------------------------------


class Event(object):
    """BigWorld-style event: handlers added with += and removed with -=."""

    def __init__(self):
        self.handlers = []

    def __iadd__(self, handler):
        self.handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.handlers.remove(handler)
        return self

    def fire(self, *args, **kwargs):
        for handler in list(self.handlers):
            handler(*args, **kwargs)


class _PlayerEvents(object):
    def __init__(self):
        self.onAvatarReady = Event()
        self.onAvatarBecomeNonPlayer = Event()
        self.onAccountShowGUI = Event()


# --- frameworks.wulf / gui.impl ------------------------------------------------


class ViewModel(object):
    """Records every property the mod declares and every value it pushes.
    `values` maps property name -> current value, i.e. what the JS would see."""

    def __init__(self, properties=0, commands=0):
        self.names = []
        self.values = {}
        self.transactions = 0
        self._initialize()

    def _initialize(self):
        pass

    def _addStringProperty(self, name, default):
        self.names.append(name)
        self.values[name] = default

    _addBoolProperty = _addStringProperty

    def _setString(self, index, value):
        self.values[self.names[index]] = value

    _setBool = _setString

    def transaction(self):
        model = self

        class _Tx(object):
            def __enter__(self):
                model.transactions += 1
                return model

            def __exit__(self, *exc):
                return False

        return _Tx()


class ViewSettings(object):
    def __init__(self, layoutID, flags, model):
        self.layoutID = layoutID
        self.model = model


class ViewImpl(object):
    def __init__(self, settings):
        self._settings = settings

    def getViewModel(self):
        return self._settings.model

    def _onLoading(self, *args, **kwargs):
        pass


class WindowImpl(object):
    def __init__(self, flags, content=None, layer=None):
        self.content = content
        self.onSizeChanged = Event()
        self.position = (0, 0)
        self.loaded = False
        self.destroyed = False

    def load(self):
        self.loaded = True

    def destroy(self):
        self.destroyed = True

    def show(self, focus=True):
        pass

    def center(self):
        pass

    def move(self, *args, **kwargs):
        pass


class _ResNode(object):
    """gui.impl.gen.R: every .dyn() step exists and the leaf returns LAYOUT_ID,
    unless MISSING is set, which makes the first step falsy."""

    LAYOUT_ID = 1
    MISSING = False

    def dyn(self, name):
        if _ResNode.MISSING:
            return None
        return self

    def __call__(self):
        return _ResNode.LAYOUT_ID


class _Enum(object):
    def __getattr__(self, name):
        return name


# --- the rest ----------------------------------------------------------------

SHOT_RESULT = type(
    "SHOT_RESULT",
    (object,),
    {"EMPTY": 0, "UNDEFINED": 1, "NOT_PIERCED": 2, "LITTLE_PIERCED": 3, "GREAT_PIERCED": 4},
)
GUN_MARKER_TYPE = type(
    "GUN_MARKER_TYPE", (object,), {"UNDEFINED": 0, "CLIENT": 1, "SERVER": 2, "DUAL_ACC": 3}
)
GUN_MARKER_FLAG = type(
    "GUN_MARKER_FLAG",
    (object,),
    {
        "UNDEFINED": 0,
        "CONTROL_ENABLED": 1,
        "CLIENT_MODE_ENABLED": 2,
        "SERVER_MODE_ENABLED": 4,
        "VIDEO_MODE_ENABLED": 8,
        "ARTY_HIT_ENABLED": 16,
    },
)

SHELL_TYPES = type(
    "SHELL_TYPES",
    (object,),
    {
        "ARMOR_PIERCING": "ARMOR_PIERCING",
        "ARMOR_PIERCING_CR": "ARMOR_PIERCING_CR",
        "ARMOR_PIERCING_HE": "ARMOR_PIERCING_HE",
        "HOLLOW_CHARGE": "HOLLOW_CHARGE",
        "HIGH_EXPLOSIVE": "HIGH_EXPLOSIVE",
    },
)
SHELL_MECHANICS_TYPE = type("SHELL_MECHANICS_TYPE", (object,), {"LEGACY": "LEGACY", "MODERN": "MODERN"})


GunMarkerState = collections.namedtuple(
    "GunMarkerState", ("gunInstallationIndex", "gunIndex", "position", "direction", "size", "collData")
)


class AvatarInputHandler(object):
    def activatePostmortem(self, *args, **kwargs):
        self.postmortem_activated = True


class _EventBus(object):
    """gui.shared.g_eventBus: keeps every event the stock code sends, so the
    tests can read the stock per-plate debug data (constants.IS_DEVELOPMENT)."""

    def __init__(self):
        self.events = []

    def handleEvent(self, event, scope=None):
        self.events.append(event)


class GunMarkerEvent(object):
    UPDATE_PIERCING_DATA = "UPDATE_PIERCING_DATA"

    def __init__(self, eventType, ctx=None):
        self.eventType = eventType
        self.ctx = ctx


class GunMarkersSetInfo(object):
    """crosshair_proxy.GunMarkersSetInfo; tests flip SERVER_ACTIVE."""

    SERVER_ACTIVE = False

    @property
    def isServerMarkerActivated(self):
        return GunMarkersSetInfo.SERVER_ACTIVE


class ShotResultIndicatorPlugin(object):
    """Shape of the stock crosshair plugin: the one place getShotResult is
    called, once per marker type."""

    resolver = None  # set by tests to the (stock) _CrosshairShotResults class

    def __onGunMarkerStateChanged(self, markerType, gunMarkerState, supportMarkersInfo):
        self.last_result = self.resolver.getShotResult(gunMarkerState, 0, 1)

    def fire(self, markerType, gunMarkerState):
        self.__onGunMarkerStateChanged(markerType, gunMarkerState, ())
        return self.last_result


def _round_py2_style(value):
    import math

    return float(math.floor(value + 0.5)) if value >= 0 else float(math.ceil(value - 0.5))


def install():
    """Registers every fake. Safe to call more than once."""
    if "PlayerEvents" in sys.modules:
        return
    _module("PlayerEvents", g_playerEvents=_PlayerEvents())
    _module("BigWorld", player=lambda: None, wg_openWebBrowser=lambda url: None, time=lambda: 0.0)
    _module("ResMgr", openSection=lambda path: None)
    _module("debug_utils", LOG_CURRENT_EXCEPTION=lambda: None)
    _module("helpers", getClientLanguage=lambda: "en")
    _module(
        "aih_constants",
        SHOT_RESULT=SHOT_RESULT,
        GUN_MARKER_TYPE=GUN_MARKER_TYPE,
        GUN_MARKER_FLAG=GUN_MARKER_FLAG,
        GunMarkerState=GunMarkerState,
    )
    _module(
        "constants",
        SHELL_TYPES=SHELL_TYPES,
        SHELL_MECHANICS_TYPE=SHELL_MECHANICS_TYPE,
        IS_DEVELOPMENT=True,
    )
    _module(
        "items.components.component_constants",
        MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS=3.0,
        MODERN_HE_DAMAGE_ABSORPTION_FACTOR=0.0,
    )
    _module("math_common", round_py2_style=_round_py2_style)
    _module("math_utils", almostZero=lambda value, epsilon=1e-06: abs(value) < epsilon)
    _module("gui.shared", g_eventBus=_EventBus(), EVENT_BUS_SCOPE=_Enum())
    _module("gui.shared.events", GunMarkerEvent=GunMarkerEvent)
    _module(
        "frameworks.wulf",
        PositionAnchor=_Enum(),
        ViewFlags=_Enum(),
        ViewModel=ViewModel,
        ViewSettings=ViewSettings,
        WindowFlags=_Enum(),
        WindowLayer=_Enum(),
    )
    _module("gui.impl.gen", R=_ResNode())
    _module("gui.impl.pub", ViewImpl=ViewImpl, WindowImpl=WindowImpl)
    _module(
        "gui.Scaleform.daapi.view.battle.shared.crosshair.plugins",
        ShotResultIndicatorPlugin=ShotResultIndicatorPlugin,
    )
    _module("gui.battle_control.controllers.crosshair_proxy", GunMarkersSetInfo=GunMarkersSetInfo)
    # AvatarInputHandler.gun_marker_ctrl is added by stock.load()
    _module("AvatarInputHandler", AvatarInputHandler=AvatarInputHandler)


def event_bus():
    return sys.modules["gui.shared"].g_eventBus


def player_events():
    return sys.modules["PlayerEvents"].g_playerEvents
