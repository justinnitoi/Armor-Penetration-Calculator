import math
from AvatarInputHandler import gun_marker_ctrl  # type: ignore
from aih_constants import SHOT_RESULT as _SHOT_RESULT  # type: ignore
from PlayerEvents import g_playerEvents  # type: ignore
from AvatarInputHandler import AvatarInputHandler  # type: ignore
from items.components.component_constants import MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS  # type: ignore

from pade_gui import update_gui, hide_labels, GuiState


def log(message):
    print("pademinune's Armor Calc: " + str(message))


def get_gaussian_probability(avg_pen, armor_val):
    min_pen = avg_pen * 0.75
    max_pen = avg_pen * 1.25

    if armor_val <= min_pen:
        return 100.0
    if armor_val >= max_pen:
        return 0.0

    # 12 * (armor_val - avg_pen) / (avg_pen)
    # If 25% is the 3-sigma point:
    # avg_pen * 0.25 = 3 SD.
    standard_deviation = avg_pen / 12

    # z-score
    z = (armor_val - avg_pen) / standard_deviation

    # Cumulative Distribution Function (CDF)
    # P(pen < armor)
    phi = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

    # get area to the right P(pen > armor)
    prob = (1.0 - phi) * 100

    return prob


def call_update_gui(avg_pen, armor_val, ricochet, hit_body, hit_track, hit_angle_cos):
    hit_angle = int(math.degrees(math.acos(hit_angle_cos)))

    prob = 0
    if not ricochet and hit_body:
        prob = get_gaussian_probability(avg_pen, armor_val)

    update_gui(armor_val, prob, ricochet, hit_body, hit_track, hit_angle)


log("Mod is loading")


# functin override
def my_shot_result_default(
    cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity
):
    """
    Override for getShotResultDefault in game code.
    Is only called when looking at an enemy tank with non HE loaded.
    """
    # pademinune armor mod variables
    total_armor_val = 0.0
    ricochet = False
    hit_body = False
    hit_track = False
    min_hit_angle_cos = 1

    # Since we are outside the class, we must use the mangled names
    isDestructible = cls._CrosshairShotResults__isDestructibleComponent
    collectDebug = cls._CrosshairShotResults__collectDebugPiercingData
    sendDebug = cls._CrosshairShotResults__sendDebugInfo

    result = _SHOT_RESULT.NOT_PIERCED
    isJet = False
    jetStartDist = None
    piercingPower = fullPiercingPower
    dispersion = round(piercingPower) * shell.piercingPowerRandomization
    minPiercingPower = round(round(piercingPower) - dispersion)
    maxPiercingPower = round(round(piercingPower) + dispersion)
    ignoredMaterials = set()
    debugPiercingsList = []

    for cDetails in collisionsDetails:
        if not isDestructible(entity, cDetails.compName):
            break

        # Track detection
        # indexes are from client/vehicle_systems/tankStructure.py in source code
        # 0 is chassis, >= 4 are extra track pairs
        if not hit_track and (cDetails.compName == 0 or cDetails.compName >= 4):
            hit_track = True

        if isJet:
            jetDist = cDetails.dist - jetStartDist
            if jetDist > 0.0:
                lossByDist = (
                    1.0 - jetDist * cls._SHELL_EXTRA_DATA[shell.kind].jetLossPPByDist
                )

                # add dissipation amount onto total armor
                lost_pen = max(
                    0, piercingPower * (1 - lossByDist)
                )  # max ensures no negative penetration dropoffs (when models overlap)
                total_armor_val += lost_pen
                # log("heat dropoff: {}mm".format(lost_pen))

                piercingPower *= lossByDist
                minPiercingPower = round(minPiercingPower * lossByDist)
                maxPiercingPower = round(maxPiercingPower * lossByDist)

        if cDetails.matInfo is None:
            result = cls._CRIT_ONLY_SHOT_RESULT
        else:
            matInfo = cDetails.matInfo
            if (cDetails.compName, matInfo.kind) in ignoredMaterials:
                continue
            if matInfo.armor is None:
                result = _SHOT_RESULT.UNDEFINED
                continue

            hitAngleCos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
            piercingPercent = 1000.0

            if not isJet and cls._shouldRicochet(shell, hitAngleCos, matInfo):
                # shell ricochet
                ricochet = True
                min_hit_angle_cos = hitAngleCos
                collectDebug(
                    debugPiercingsList,
                    None,
                    hitAngleCos,
                    minPiercingPower,
                    maxPiercingPower,
                    piercingPercent,
                    matInfo,
                    _SHOT_RESULT.NOT_PIERCED,
                )
                break

            penetrationArmor = cls._computePenetrationArmor(
                shell, hitAngleCos, matInfo
            )
            total_armor_val += penetrationArmor

            if piercingPower > 0.0:
                piercingPercent = (
                    100.0
                    + (penetrationArmor - piercingPower) / fullPiercingPower * 100.0
                )
                piercingPower -= penetrationArmor
                minPiercingPower = round(minPiercingPower - penetrationArmor)
                maxPiercingPower = round(maxPiercingPower - penetrationArmor)

            if matInfo.vehicleDamageFactor:
                # main armor plate
                hit_body = True
                min_hit_angle_cos = hitAngleCos
                if minPP < piercingPercent < maxPP:
                    result = _SHOT_RESULT.LITTLE_PIERCED
                elif piercingPercent <= minPP:
                    result = _SHOT_RESULT.GREAT_PIERCED
                collectDebug(
                    debugPiercingsList,
                    penetrationArmor,
                    hitAngleCos,
                    minPiercingPower,
                    maxPiercingPower,
                    piercingPercent,
                    matInfo,
                    result,
                )
                break
            else:
                # spaced armor
                debugResut = _SHOT_RESULT.NOT_PIERCED
                if minPP < piercingPercent < maxPP:
                    debugResut = _SHOT_RESULT.LITTLE_PIERCED
                elif piercingPercent <= minPP:
                    debugResut = _SHOT_RESULT.GREAT_PIERCED
                if matInfo.extra:
                    if piercingPercent <= maxPP:
                        result = cls._CRIT_ONLY_SHOT_RESULT
                collectDebug(
                    debugPiercingsList,
                    penetrationArmor,
                    hitAngleCos,
                    minPiercingPower,
                    maxPiercingPower,
                    piercingPercent,
                    matInfo,
                    debugResut,
                )

            if matInfo.collideOnceOnly:
                ignoredMaterials.add((cDetails.compName, matInfo.kind))

        # don't break early so that it can compute all the armor
        # if piercingPower <= 0.0:
        #     break

        if cls._SHELL_EXTRA_DATA[shell.kind].jetLossPPByDist > 0.0:
            isJet = True
            mInfo = cDetails.matInfo
            armor = mInfo.armor if mInfo is not None else 0.0
            jetStartDist = cDetails.dist + armor * 0.001

    sendDebug(gunMarker, debugPiercingsList, minPP, maxPP, fullPiercingPower)

    # pademinune armor mod calc
    call_update_gui(
        fullPiercingPower,
        total_armor_val,
        ricochet,
        hit_body,
        hit_track,
        min_hit_angle_cos,
    )

    return result


def my_shot_result_modern_he(
    cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity
):
    """
    Override for __shotResultModernHE in game code.
    Called when looking at an enemy tank with modern HE loaded.
    """
    # pademinune armor mod variables
    total_armor_val = 0.0
    hit_body = False
    hit_track = False
    min_hit_angle_cos = 1

    # Since we are outside the class, we must use the mangled names
    isDestructible = cls._CrosshairShotResults__isDestructibleComponent
    collectDebug = cls._CrosshairShotResults__collectDebugPiercingData
    sendDebug = cls._CrosshairShotResults__sendDebugInfo

    result = _SHOT_RESULT.NOT_PIERCED
    ignoredMaterials = set()
    piercingPower = fullPiercingPower
    dispersion = round(piercingPower) * shell.piercingPowerRandomization
    minPiercingPower = round(round(piercingPower) - dispersion)
    maxPiercingPower = round(round(piercingPower) + dispersion)
    explosionDamageAbsorption = 0
    debugPiercingsList = []

    try:
        for cDetails in collisionsDetails:
            if not isDestructible(entity, cDetails.compName):
                sendDebug(
                    gunMarker, debugPiercingsList, minPP, maxPP, fullPiercingPower
                )
                call_update_gui(
                    fullPiercingPower,
                    total_armor_val,
                    False,
                    hit_body,
                    hit_track,
                    min_hit_angle_cos,
                )
                return result

            # Track detection
            if not hit_track and (cDetails.compName == 0 or cDetails.compName >= 4):
                hit_track = True

            matInfo = cDetails.matInfo
            if (
                matInfo is not None
                and (cDetails.compName, matInfo.kind) not in ignoredMaterials
            ):
                hitAngleCos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
                piercingPercent = 1000.0
                penetrationArmor = 0

                if fullPiercingPower > 0.0:
                    penetrationArmor = cls._computePenetrationArmor(
                        shell, hitAngleCos, matInfo
                    )
                    piercingPercent = (
                        100.0
                        + (penetrationArmor - piercingPower) / fullPiercingPower * 100.0
                    )

                if matInfo.vehicleDamageFactor:
                    # main hull plate
                    hit_body = True
                    min_hit_angle_cos = hitAngleCos
                    total_armor_val += penetrationArmor
                    piercingPower -= penetrationArmor
                    minPiercingPower = round(minPiercingPower - penetrationArmor)
                    maxPiercingPower = round(maxPiercingPower - penetrationArmor)
                    if piercingPercent <= minPP and explosionDamageAbsorption == 0:
                        result = _SHOT_RESULT.GREAT_PIERCED
                    else:
                        result = _SHOT_RESULT.LITTLE_PIERCED
                    collectDebug(
                        debugPiercingsList,
                        penetrationArmor,
                        hitAngleCos,
                        minPiercingPower,
                        maxPiercingPower,
                        piercingPercent,
                        matInfo,
                        result,
                    )
                    sendDebug(
                        gunMarker, debugPiercingsList, minPP, maxPP, fullPiercingPower
                    )
                    call_update_gui(
                        fullPiercingPower,
                        total_armor_val,
                        False,
                        hit_body,
                        hit_track,
                        min_hit_angle_cos,
                    )
                    return result

                if shell.type.shieldPenetration:
                    shieldPenetration = (
                        penetrationArmor
                        * MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS
                    )
                    # accumulate 3x nominal armor as virtual armor cost
                    total_armor_val += shieldPenetration
                    piercingPower -= shieldPenetration
                    minPiercingPower = round(minPiercingPower - shieldPenetration)
                    maxPiercingPower = round(maxPiercingPower - shieldPenetration)
                    # explosionDamageAbsorption += penetrationArmor * 0.0
                    # # MODERN_HE_DAMAGE_ABSORPTION_FACTOR is 0.0

                if (
                    piercingPercent > maxPP
                    or not shell.type.shieldPenetration
                    or explosionDamageAbsorption >= shell.type.maxDamage
                ):
                    collectDebug(
                        debugPiercingsList,
                        penetrationArmor,
                        hitAngleCos,
                        minPiercingPower,
                        maxPiercingPower,
                        piercingPercent,
                        matInfo,
                        _SHOT_RESULT.NOT_PIERCED,
                    )
                    sendDebug(
                        gunMarker, debugPiercingsList, minPP, maxPP, fullPiercingPower
                    )
                    call_update_gui(
                        fullPiercingPower,
                        total_armor_val,
                        False,
                        hit_body,
                        hit_track,
                        min_hit_angle_cos,
                    )
                    return _SHOT_RESULT.NOT_PIERCED

                if matInfo.extra and piercingPercent <= maxPP:
                    collectDebug(
                        debugPiercingsList,
                        penetrationArmor,
                        hitAngleCos,
                        minPiercingPower,
                        maxPiercingPower,
                        piercingPercent,
                        matInfo,
                        cls._CRIT_ONLY_SHOT_RESULT,
                    )
                    result = cls._CRIT_ONLY_SHOT_RESULT

                if matInfo.collideOnceOnly:
                    ignoredMaterials.add((cDetails.compName, matInfo.kind))

    except Exception as e:
        log("my_shot_result_modern_he error: %s" % str(e))

    sendDebug(gunMarker, debugPiercingsList, minPP, maxPP, fullPiercingPower)
    call_update_gui(
        fullPiercingPower,
        total_armor_val,
        False,
        hit_body,
        hit_track,
        min_hit_angle_cos,
    )
    return result


original_getShotResult = gun_marker_ctrl._CrosshairShotResults.getShotResult.__func__


def my_get_shot_result(cls, gunMarker, excludeTeam=0, piercingMultiplier=1):
    """Override for original getShotResult. Is only called when reticle is visible."""
    result = original_getShotResult(cls, gunMarker, excludeTeam, piercingMultiplier)
    if result == _SHOT_RESULT.UNDEFINED and (GuiState.armor_visible or GuiState.prob_visible or GuiState.angle_visible):
        # only call hide if the gui is still visible
        hide_labels()
    return result


def on_load_match():
    """Called when the player spawns into a map."""
    hide_labels()

    # log("New match detected: Resetting GUI.")


def on_leave_match():
    """Called when the player leaves a match"""
    hide_labels()

    # log('Player has left the match. Resetting GUI.')


original_activate_postmortem = AvatarInputHandler.activatePostmortem


def my_activate_postmortem(self, *args, **kwargs):
    """Called when your vehicle is destroyed"""
    original_activate_postmortem(self, *args, **kwargs)

    hide_labels()
    # log('Player is dead. Hiding GUI.')


# overriding source code functions

# Called whenever reticle is visible
gun_marker_ctrl._CrosshairShotResults.getShotResult = classmethod(my_get_shot_result)

# Called only when looking at an enemy tank with non HE shell
gun_marker_ctrl._CrosshairShotResults._CrosshairShotResults__shotResultDefault = (
    classmethod(my_shot_result_default)
)

# Called only when looking at an enemy tank with modern HE shell
gun_marker_ctrl._CrosshairShotResults._CrosshairShotResults__shotResultModernHE = (
    classmethod(my_shot_result_modern_he)
)

# Called only once at the start of every match when loading in
g_playerEvents.onAvatarBecomePlayer += on_load_match

# Called once when the player leaves a match
g_playerEvents.onAvatarBecomeNonPlayer += on_leave_match

# Called when your tank is destroyed
AvatarInputHandler.activatePostmortem = my_activate_postmortem

log("Mod has finished loading")
