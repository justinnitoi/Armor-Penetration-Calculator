"""Armor analysis of one aimed shot, for the overlay only.

These functions walk the same collision list the stock
gun_marker_ctrl._CrosshairShotResults methods walk, using the stock class's own
helpers (_shouldRicochet, _computePenetrationArmor, ...), but they never decide
the reticle's shot result -- the stock method still does that, unchanged. So a
client update that changes the stock logic can make these numbers drift, but can
never make the reticle wrong.

They differ from stock on purpose in one way: they keep summing armor after the
shell's penetration runs out, so the label shows the full armor crossed rather
than stopping at the plate where stock gives up.

`cls` is the stock _CrosshairShotResults class. No game imports here, so this
module runs offline in the tests with the real stock class loaded from wot-src.
"""

# client/vehicle_systems/tankStructure.py TankPartIndexes: 0 is chassis, 3 is
# gun, >= 4 are extra track pairs. Literals, not imports, so a renumbering
# fails silently -- see CLAUDE.md.
_CHASSIS = 0
_GUN = 3
_FIRST_EXTRA_TRACK = 4


class ShotAnalysis(object):
    """What the overlay needs to know about the shot under the reticle.

    armor: effective armor crossed (mm), including spaced armor, HEAT jet
        distance loss and modern-HE shield cost.
    hit_angle_cos: cosine of the impact angle at the plate that decided the
        shot (the main plate, or the plate the shell ricocheted off)."""

    __slots__ = ("armor", "ricochet", "hit_body", "hit_track", "hit_gun", "hit_angle_cos")

    def __init__(self):
        self.armor = 0.0
        self.ricochet = False
        self.hit_body = False
        self.hit_track = False
        self.hit_gun = False
        self.hit_angle_cos = 1.0


def _is_destructible(cls, entity, comp_name):
    return cls._CrosshairShotResults__isDestructibleComponent(entity, comp_name)


def _note_component(analysis, comp_name):
    if comp_name == _CHASSIS or comp_name >= _FIRST_EXTRA_TRACK:
        analysis.hit_track = True
    elif comp_name == _GUN:
        analysis.hit_gun = True


def analyze_default(cls, collisionsDetails, fullPiercingPower, shell, entity):
    """Mirror of stock __shotResultDefault (AP, APCR, HEAT, legacy HE)."""
    analysis = ShotAnalysis()
    has_pen_loss = cls._SHELL_EXTRA_DATA[shell.kind].hasPenetrationLoss
    piercing_power = fullPiercingPower
    is_jet = False
    jet_start_dist = None
    ignored_materials = set()

    for cDetails in collisionsDetails:
        if not _is_destructible(cls, entity, cDetails.compName):
            break
        _note_component(analysis, cDetails.compName)

        if is_jet:
            jet_dist = cDetails.dist - jet_start_dist
            if jet_dist > 0.0:
                loss_by_dist = 1.0 - jet_dist * shell.type.piercingPowerLossFactorByDistance
                # count penetration lost in the air gap as armor; max() keeps
                # overlapping models from producing negative armor
                analysis.armor += max(0.0, piercing_power * (1.0 - loss_by_dist))
                piercing_power *= loss_by_dist

        matInfo = cDetails.matInfo
        if matInfo is not None:
            if (cDetails.compName, matInfo.kind) in ignored_materials:
                continue
            if matInfo.armor is None:
                continue

            hit_angle_cos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
            if not is_jet and cls._shouldRicochet(shell, hit_angle_cos, matInfo):
                analysis.ricochet = True
                analysis.hit_angle_cos = hit_angle_cos
                break

            penetration_armor = cls._computePenetrationArmor(shell, hit_angle_cos, matInfo)
            analysis.armor += penetration_armor
            if piercing_power > 0.0:
                piercing_power -= penetration_armor

            if matInfo.vehicleDamageFactor:
                # main armor plate: the shot is decided here
                analysis.hit_body = True
                analysis.hit_angle_cos = hit_angle_cos
                break

            if matInfo.collideOnceOnly:
                ignored_materials.add((cDetails.compName, matInfo.kind))

        # unlike stock, no break when piercing_power <= 0: keep summing armor

        if has_pen_loss:
            is_jet = True
            armor = matInfo.armor if matInfo is not None else 0.0
            jet_start_dist = cDetails.dist + (armor or 0.0) * 0.001

    return analysis


def analyze_modern_he(
    cls, collisionsDetails, fullPiercingPower, shell, maxPP, entity, shield_factor, absorption_factor
):
    """Mirror of stock __shotResultModernHE.

    shield_factor / absorption_factor: MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS
    and MODERN_HE_DAMAGE_ABSORPTION_FACTOR from component_constants."""
    analysis = ShotAnalysis()
    piercing_power = fullPiercingPower
    explosion_damage_absorption = 0.0
    ignored_materials = set()

    for cDetails in collisionsDetails:
        if not _is_destructible(cls, entity, cDetails.compName):
            return analysis
        _note_component(analysis, cDetails.compName)

        matInfo = cDetails.matInfo
        if matInfo is None or (cDetails.compName, matInfo.kind) in ignored_materials:
            continue

        hit_angle_cos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
        piercing_percent = 1000.0
        penetration_armor = 0.0
        if fullPiercingPower > 0.0:
            penetration_armor = cls._computePenetrationArmor(shell, hit_angle_cos, matInfo)
            piercing_percent = 100.0 + (penetration_armor - piercing_power) / fullPiercingPower * 100.0

        if matInfo.vehicleDamageFactor:
            # main hull plate
            analysis.hit_body = True
            analysis.hit_angle_cos = hit_angle_cos
            analysis.armor += penetration_armor
            return analysis

        if shell.type.shieldPenetration:
            # a shield costs shield_factor x its nominal armor
            shield_penetration = penetration_armor * shield_factor
            analysis.armor += shield_penetration
            piercing_power -= shield_penetration
            explosion_damage_absorption += penetration_armor * absorption_factor

        if (
            piercing_percent > maxPP
            or not shell.type.shieldPenetration
            or explosion_damage_absorption >= shell.type.maxDamage
        ):
            return analysis

        if matInfo.collideOnceOnly:
            ignored_materials.add((cDetails.compName, matInfo.kind))

    return analysis
