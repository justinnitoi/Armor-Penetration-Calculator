"""Shared setup for the tests: call support.setup() at the top of every test
module. It installs the fakes, loads the real stock gun_marker_ctrl.py, keeps
the stock shot-result methods before the mod wraps them, and then imports the
mod (which runs its init() patching, as in the client).

Also builders for the stock objects the shot-result code reads.
"""

import math
import os
import sys
import tempfile
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TESTS_DIR)
CLIENT_SRC = os.path.join(ROOT, "src", "res", "scripts", "client")

if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

import fakes  # noqa: E402
import stock  # noqa: E402

DEFAULT_NAME = "_CrosshairShotResults__shotResultDefault"
MODERN_HE_NAME = "_CrosshairShotResults__shotResultModernHE"

STOCK = None  # the stock gun_marker_ctrl module, or None if unavailable
STOCK_ORIGINALS = {}  # name -> stock function, captured before the mod wraps it
_ready = False


def setup():
    global STOCK, _ready
    if _ready:
        return
    _ready = True
    sys.path.insert(0, CLIENT_SRC)
    # the mod reads and writes its config relative to the working directory
    os.chdir(tempfile.mkdtemp(prefix="ap_calc_tests_"))
    fakes.install()
    STOCK = stock.load()
    if STOCK is None:
        return
    cls = STOCK._CrosshairShotResults
    for name in (DEFAULT_NAME, MODERN_HE_NAME, "getShotResult"):
        STOCK_ORIGINALS[name] = getattr(cls, name).__func__
    import ap_calculator  # noqa: F401  (runs the mod's init() side effects)


def requires_stock(test):
    return unittest.skipIf(
        STOCK is None, "stock gun_marker_ctrl.py unavailable (offline and not cached)"
    )(test)


# --- builders ------------------------------------------------------------------


class Obj(object):
    def __init__(self, **attrs):
        self.__dict__.update(attrs)


_next_kind = [100]


def _new_kind():
    # distinct per plate: stock skips a repeat (compName, kind) pair when
    # collideOnceOnly is set
    _next_kind[0] += 1
    return _next_kind[0]


def mat(
    armor,
    damage_factor=1.0,
    kind=None,
    use_hit_angle=True,
    may_ricochet=True,
    check_caliber_for_ricochet=True,
    check_caliber_for_norm=True,
    collide_once_only=True,
    extra=None,
):
    """A matInfo. damage_factor 0 is spaced armor / tracks / gun; non-zero is a
    main armor plate."""
    return Obj(
        armor=armor,
        vehicleDamageFactor=damage_factor,
        kind=_new_kind() if kind is None else kind,
        useHitAngle=use_hit_angle,
        mayRicochet=may_ricochet,
        checkCaliberForRicochet=check_caliber_for_ricochet,
        checkCaliberForHitAngleNorm=check_caliber_for_norm,
        collideOnceOnly=collide_once_only,
        extra=extra,
    )


def hit(mat_info, angle_deg=0.0, comp=1, dist=10.0):
    """One collision detail. comp: 0 chassis, 1 hull, 2 turret, 3 gun."""
    return Obj(
        compName=comp, dist=dist, hitAngleCos=math.cos(math.radians(angle_deg)), matInfo=mat_info
    )


def shell(
    kind=fakes.SHELL_TYPES.ARMOR_PIERCING,
    caliber=100.0,
    ricochet_deg=70.0,
    normalization_deg=5.0,
    loss_per_m=0.0,
    shield_penetration=False,
    max_damage=0.0,
    mechanics=fakes.SHELL_MECHANICS_TYPE.LEGACY,
):
    return Obj(
        kind=kind,
        caliber=caliber,
        piercingPowerRandomization=0.25,
        armorDamage=(300, 300),
        type=Obj(
            ricochetAngleCos=math.cos(math.radians(ricochet_deg)),
            normalizationAngle=math.radians(normalization_deg),
            piercingPowerLossFactorByDistance=loss_per_m,
            shieldPenetration=shield_penetration,
            maxDamage=max_damage,
            mechanics=mechanics,
        ),
    )


def entity(health=1000, destructible=True):
    if destructible:
        return Obj(health=health)
    # a DestructibleEntity whose components can't be hit
    base = STOCK.DestructibleEntity
    cls = type("FakeDestructible", (base,), {"isDestructibleComponent": lambda self, c: False})
    e = cls()
    e.health = health
    return e


def stock_shot(name, collisions, full_pp, shell_, entity_):
    """Runs the unwrapped stock method. Returns (result, per-plate debug data)."""
    cls = STOCK._CrosshairShotResults
    min_pp, max_pp = cls._computePiercingPowerRandomization(shell_)
    bus = fakes.event_bus()
    del bus.events[:]
    result = STOCK_ORIGINALS[name](cls, None, collisions, full_pp, shell_, min_pp, max_pp, entity_)
    plates = bus.events[-1].ctx["piercingData"] if bus.events else []
    return result, plates


def wrapped_shot(name, collisions, full_pp, shell_, entity_):
    """Runs the method as the client would after the mod wrapped it."""
    cls = STOCK._CrosshairShotResults
    min_pp, max_pp = cls._computePiercingPowerRandomization(shell_)
    return getattr(cls, name)(None, collisions, full_pp, shell_, min_pp, max_pp, entity_)


def overlay_values():
    """What the overlay's JS currently sees (opens the window if needed)."""
    from ap_calculator.gui.ap_gameface_api import ap_window

    return ap_window._active[1].viewModel.values
