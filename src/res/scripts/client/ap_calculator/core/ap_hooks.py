"""Hooks into the stock client's shot-result code and battle lifecycle.

The stock gun_marker_ctrl._CrosshairShotResults methods that color the reticle
are wrapped, never replaced: the stock method always runs first and its result
is returned untouched, then shot_analysis re-walks the same collisions to
compute the overlay's numbers. Any error on the overlay side is logged and
swallowed, so the mod can never make the reticle worse than vanilla.

If the stock class no longer looks the way this code expects (after a client
update), init() logs why and patches nothing.
"""

import inspect

import aih_constants  # type: ignore
from AvatarInputHandler import (  # type: ignore
    AvatarInputHandler,
    gun_marker_ctrl,
)
from items.components import component_constants  # type: ignore
from PlayerEvents import g_playerEvents  # type: ignore

from ap_calculator.debug import log, log_exception
from ap_calculator.gui.ap_gui import gui_state
from ap_calculator.core.ap_math import gaussian_probability, arccos
from ap_calculator.core.shot_analysis import analyze_default, analyze_modern_he

_SHOT_RESULT = aih_constants.SHOT_RESULT
_MARKER_TYPE = aih_constants.GUN_MARKER_TYPE
_SHIELD_FACTOR = component_constants.MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS
# 0.0 at the time of writing; read it rather than assume it stays that way
_ABSORPTION_FACTOR = getattr(component_constants, "MODERN_HE_DAMAGE_ABSORPTION_FACTOR", 0.0)

_SHOT_RESULTS_CLS = gun_marker_ctrl._CrosshairShotResults
_DEFAULT_NAME = "_CrosshairShotResults__shotResultDefault"
_MODERN_HE_NAME = "_CrosshairShotResults__shotResultModernHE"
_SHOT_RESULT_ARGS = [
    "cls", "gunMarker", "collisionsDetails", "fullPiercingPower", "shell", "minPP", "maxPP", "entity"
]
_GET_SHOT_RESULT_ARGS = ["cls", "gunMarker", "excludeTeam", "piercingMultiplier"]
# Class internals shot_analysis reads off the stock class.
_REQUIRED_ATTRS = [
    "_shouldRicochet",
    "_computePenetrationArmor",
    "_SHELL_EXTRA_DATA",
    "_CrosshairShotResults__isDestructibleComponent",
]

# False while the stock crosshair is resolving a marker the overlay should not
# follow (the client marker, when the server reticle is on). See
# _install_marker_filter.
_overlay_allowed = True


def call_update_gui(analysis, avg_pen):
    """Pushes one shot's analysis to the overlay."""
    prob = 0
    if not analysis.ricochet and analysis.hit_body:
        prob = gaussian_probability(avg_pen, analysis.armor)

    gui_state.update_gui(
        int(analysis.armor),
        int(prob),
        analysis.ricochet,
        analysis.hit_body,
        int(arccos(analysis.hit_angle_cos)),
        analysis.hit_track,
    )


def _as_list(collisionsDetails):
    # Both the stock method and the analysis iterate it; make sure a one-shot
    # iterator can't leave the second pass empty.
    if isinstance(collisionsDetails, (list, tuple)):
        return collisionsDetails
    return list(collisionsDetails)


def _make_default_wrapper(original):
    def my_shot_result_default(
        cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity
    ):
        """Wraps stock __shotResultDefault (enemy under reticle, non modern-HE shell)."""
        collisionsDetails = _as_list(collisionsDetails)
        result = original(
            cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity
        )
        if _overlay_allowed:
            try:
                analysis = analyze_default(cls, collisionsDetails, fullPiercingPower, shell, entity)
                call_update_gui(analysis, fullPiercingPower)
            except Exception:
                log_exception("shot analysis (default)")
        return result

    return my_shot_result_default


def _make_modern_he_wrapper(original):
    def my_shot_result_modern_he(
        cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity
    ):
        """Wraps stock __shotResultModernHE (enemy under reticle, modern HE shell)."""
        collisionsDetails = _as_list(collisionsDetails)
        result = original(
            cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity
        )
        if _overlay_allowed:
            try:
                analysis = analyze_modern_he(
                    cls,
                    collisionsDetails,
                    fullPiercingPower,
                    shell,
                    maxPP,
                    entity,
                    _SHIELD_FACTOR,
                    _ABSORPTION_FACTOR,
                )
                call_update_gui(analysis, fullPiercingPower)
            except Exception:
                log_exception("shot analysis (modern HE)")
        return result

    return my_shot_result_modern_he


def _make_get_shot_result_wrapper(original):
    def my_get_shot_result(cls, gunMarker, excludeTeam=0, piercingMultiplier=1):
        """Wraps stock getShotResult. Only called while the reticle is visible."""
        result = original(cls, gunMarker, excludeTeam, piercingMultiplier)
        if result == _SHOT_RESULT.UNDEFINED and _overlay_allowed:
            try:
                if gui_state.is_visible():
                    gui_state.hide_all()
            except Exception:
                log_exception("hiding overlay")
        return result

    return my_get_shot_result


def _argnames(method):
    return inspect.getargspec(method.__func__).args


def _check_compatibility(cls):
    """Returns a list of reasons the stock class doesn't match what this mod
    expects (empty if it does)."""
    problems = []
    for name in _REQUIRED_ATTRS + [_DEFAULT_NAME, _MODERN_HE_NAME, "getShotResult"]:
        if not hasattr(cls, name):
            problems.append("missing {}".format(name))
    if problems:
        return problems
    for name in (_DEFAULT_NAME, _MODERN_HE_NAME):
        if _argnames(getattr(cls, name)) != _SHOT_RESULT_ARGS:
            problems.append("{} signature changed".format(name))
    if _argnames(cls.getShotResult) != _GET_SHOT_RESULT_ARGS:
        problems.append("getShotResult signature changed")
    return problems


def _install_marker_filter():
    """With the server reticle on, the stock crosshair resolves the shot result
    once per marker (client and server) on each update, so the overlay would
    alternate between two results. Follow only the server marker in that case.

    Optional: if the stock plugin moved, log it and keep following every marker."""
    try:
        from gui.Scaleform.daapi.view.battle.shared.crosshair import plugins  # type: ignore
        from gui.battle_control.controllers.crosshair_proxy import (  # type: ignore
            GunMarkersSetInfo,
        )

        plugin_cls = plugins.ShotResultIndicatorPlugin
        name = "_ShotResultIndicatorPlugin__onGunMarkerStateChanged"
        original = getattr(plugin_cls, name).__func__
        markers_info = GunMarkersSetInfo()
    except Exception:
        log_exception("installing the server reticle filter")
        return

    def my_on_gun_marker_state_changed(self, markerType, *args, **kwargs):
        global _overlay_allowed
        try:
            _overlay_allowed = (
                markerType == _MARKER_TYPE.SERVER or not markers_info.isServerMarkerActivated
            )
        except Exception:
            log_exception("server reticle filter")
            _overlay_allowed = True
        try:
            return original(self, markerType, *args, **kwargs)
        finally:
            _overlay_allowed = True

    setattr(plugin_cls, name, my_on_gun_marker_state_changed)


def on_load_match(*args, **kwargs):
    """Called when tank is created"""
    gui_state.create_window()


def on_leave_match(*args, **kwargs):
    """Called when the player leaves a match"""
    gui_state.destroy_window()


original_activate_postmortem = AvatarInputHandler.activatePostmortem


def my_activate_postmortem(self, *args, **kwargs):
    """Called when your vehicle is destroyed"""
    original_activate_postmortem(self, *args, **kwargs)
    try:
        gui_state.hide_all()
    except Exception:
        log_exception("activatePostmortem")


def init():
    cls = _SHOT_RESULTS_CLS
    problems = _check_compatibility(cls)
    if problems:
        log(
            "This game client is incompatible with this mod version; the overlay is "
            "disabled. ({})".format("; ".join(problems))
        )
        return

    cls.getShotResult = classmethod(_make_get_shot_result_wrapper(cls.getShotResult.__func__))
    setattr(cls, _DEFAULT_NAME, classmethod(_make_default_wrapper(getattr(cls, _DEFAULT_NAME).__func__)))
    setattr(
        cls,
        _MODERN_HE_NAME,
        classmethod(_make_modern_he_wrapper(getattr(cls, _MODERN_HE_NAME).__func__)),
    )
    _install_marker_filter()

    g_playerEvents.onAvatarReady += on_load_match
    g_playerEvents.onAvatarBecomeNonPlayer += on_leave_match
    AvatarInputHandler.activatePostmortem = my_activate_postmortem


init()
