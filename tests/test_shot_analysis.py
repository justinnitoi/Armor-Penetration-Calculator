"""shot_analysis against the real stock shot-result code.

Each case runs the unwrapped stock method on the same collisions, then checks
that the mod's armor/angle/flags agree with the per-plate numbers stock itself
computed (its IS_DEVELOPMENT debug data). If WG changes the stock logic, these
are the tests that fail once WOT_SRC_COMMIT in stock.py is bumped.
"""

import math
import unittest

import support

support.setup()

from fakes import SHELL_MECHANICS_TYPE, SHELL_TYPES, SHOT_RESULT  # noqa: E402
from support import entity, hit, mat, shell, stock_shot, wrapped_shot  # noqa: E402

DEFAULT = support.DEFAULT_NAME
MODERN_HE = support.MODERN_HE_NAME


def _analyze_default(collisions, full_pp, shell_, entity_):
    from ap_calculator.core.shot_analysis import analyze_default

    return analyze_default(support.STOCK._CrosshairShotResults, collisions, full_pp, shell_, entity_)


def _analyze_modern_he(collisions, full_pp, shell_, entity_):
    from ap_calculator.core.shot_analysis import analyze_modern_he

    cls = support.STOCK._CrosshairShotResults
    _min_pp, max_pp = cls._computePiercingPowerRandomization(shell_)
    return analyze_modern_he(cls, collisions, full_pp, shell_, max_pp, entity_, 3.0, 0.0)


def _plate_sum(plates):
    return sum(p["penetrationArmor"] or 0.0 for p in plates)


def _angle(analysis):
    return math.degrees(math.acos(analysis.hit_angle_cos))


@support.requires_stock
class DefaultShellTest(unittest.TestCase):
    def check_matches_stock(self, collisions, full_pp, shell_):
        e = entity()
        _result, plates = stock_shot(DEFAULT, collisions, full_pp, shell_, e)
        analysis = _analyze_default(collisions, full_pp, shell_, e)
        self.assertAlmostEqual(analysis.armor, _plate_sum(plates), places=6)
        return analysis, plates

    def test_single_plate_uses_stock_normalization(self):
        collisions = [hit(mat(100), angle_deg=30)]
        analysis, plates = self.check_matches_stock(collisions, 200.0, shell())
        # AP normalizes by 5 degrees
        self.assertAlmostEqual(analysis.armor, 100 / math.cos(math.radians(25)), places=6)
        self.assertTrue(analysis.hit_body)
        self.assertFalse(analysis.ricochet)
        self.assertAlmostEqual(_angle(analysis), 30.0, places=6)

    def test_spaced_then_main_plate_sums_both(self):
        collisions = [hit(mat(20, damage_factor=0), dist=10.0), hit(mat(80), dist=10.5)]
        analysis, plates = self.check_matches_stock(collisions, 200.0, shell())
        self.assertEqual(len(plates), 2)
        self.assertTrue(analysis.hit_body)

    def test_ricochet(self):
        collisions = [hit(mat(50), angle_deg=75)]
        e = entity()
        result, plates = stock_shot(DEFAULT, collisions, 200.0, shell(), e)
        analysis = _analyze_default(collisions, 200.0, shell(), e)
        self.assertEqual(result, SHOT_RESULT.NOT_PIERCED)
        self.assertIsNone(plates[-1]["penetrationArmor"])  # stock's ricochet marker
        self.assertTrue(analysis.ricochet)
        self.assertFalse(analysis.hit_body)
        self.assertAlmostEqual(_angle(analysis), 75.0, places=6)

    def test_overmatch_does_not_ricochet(self):
        # caliber > 3x armor: no ricochet, and normalization is boosted
        collisions = [hit(mat(50), angle_deg=75)]
        analysis, plates = self.check_matches_stock(collisions, 200.0, shell(caliber=155.0))
        self.assertFalse(analysis.ricochet)
        self.assertTrue(analysis.hit_body)

    def test_heat_counts_jet_distance_loss_as_armor(self):
        heat = shell(kind=SHELL_TYPES.HOLLOW_CHARGE, loss_per_m=0.1)
        collisions = [hit(mat(10, damage_factor=0), dist=10.0), hit(mat(100), dist=11.0)]
        e = entity()
        _result, plates = stock_shot(DEFAULT, collisions, 300.0, heat, e)
        analysis = _analyze_default(collisions, 300.0, heat, e)
        gap = 11.0 - (10.0 + 10 * 0.001)
        lost = (300.0 - 10.0) * gap * 0.1
        self.assertAlmostEqual(analysis.armor, _plate_sum(plates) + lost, places=6)

    def test_keeps_summing_after_penetration_runs_out(self):
        # stock stops at the spaced plate (no penetration left); the mod keeps
        # going so the label shows the full armor, at a 0% chance
        collisions = [hit(mat(60, damage_factor=0), dist=10.0), hit(mat(100), dist=10.5)]
        e = entity()
        _result, plates = stock_shot(DEFAULT, collisions, 50.0, shell(), e)
        analysis = _analyze_default(collisions, 50.0, shell(), e)
        self.assertEqual(len(plates), 1)
        self.assertAlmostEqual(analysis.armor, 160.0, places=6)
        self.assertTrue(analysis.hit_body)

    def test_track_only(self):
        collisions = [hit(mat(20, damage_factor=0), comp=0)]
        analysis, _plates = self.check_matches_stock(collisions, 200.0, shell())
        self.assertTrue(analysis.hit_track)
        self.assertFalse(analysis.hit_body)

    def test_gun_mantlet_then_turret(self):
        collisions = [hit(mat(150, damage_factor=0), comp=3), hit(mat(100), comp=2, dist=10.4)]
        analysis, _plates = self.check_matches_stock(collisions, 300.0, shell())
        self.assertTrue(analysis.hit_gun)
        self.assertTrue(analysis.hit_body)

    def test_non_destructible_component_stops(self):
        collisions = [hit(mat(100))]
        e = entity(destructible=False)
        analysis = _analyze_default(collisions, 200.0, shell(), e)
        self.assertEqual(analysis.armor, 0.0)
        self.assertFalse(analysis.hit_body)


@support.requires_stock
class ModernHETest(unittest.TestCase):
    def modern_he(self):
        return shell(
            kind=SHELL_TYPES.HIGH_EXPLOSIVE,
            normalization_deg=0.0,
            shield_penetration=True,
            max_damage=500.0,
            mechanics=SHELL_MECHANICS_TYPE.MODERN,
        )

    def test_shield_costs_three_times_its_armor(self):
        he = self.modern_he()
        collisions = [hit(mat(10, damage_factor=0), dist=10.0), hit(mat(40), dist=10.5)]
        e = entity()
        _result, plates = stock_shot(MODERN_HE, collisions, 80.0, he, e)
        analysis = _analyze_modern_he(collisions, 80.0, he, e)
        # stock reports the main plate's plain armor; the shield is 3 x 10
        self.assertAlmostEqual(plates[-1]["penetrationArmor"], 40.0)
        self.assertAlmostEqual(analysis.armor, 3 * 10.0 + 40.0)
        self.assertTrue(analysis.hit_body)

    def test_shield_too_thick_stops(self):
        he = self.modern_he()
        collisions = [hit(mat(100, damage_factor=0), dist=10.0), hit(mat(40), dist=10.5)]
        e = entity()
        result, _plates = stock_shot(MODERN_HE, collisions, 80.0, he, e)
        analysis = _analyze_modern_he(collisions, 80.0, he, e)
        self.assertEqual(result, SHOT_RESULT.NOT_PIERCED)
        self.assertFalse(analysis.hit_body)


@support.requires_stock
class WrapperTest(unittest.TestCase):
    """The wrapped methods must return exactly what stock returns."""

    CASES = [
        ([hit(mat(100), angle_deg=30)], 200.0),
        ([hit(mat(100), angle_deg=30)], 90.0),
        ([hit(mat(50), angle_deg=75)], 200.0),
        ([hit(mat(60, damage_factor=0)), hit(mat(100), dist=10.5)], 50.0),
        ([hit(mat(20, damage_factor=0), comp=0)], 200.0),
        # unconfigured material: stock returns UNDEFINED
        ([hit(mat(None))], 200.0),
    ]

    def test_default_result_is_stock_result(self):
        for collisions, full_pp in self.CASES:
            e = entity()
            expected, _plates = stock_shot(DEFAULT, collisions, full_pp, shell(), e)
            self.assertEqual(wrapped_shot(DEFAULT, collisions, full_pp, shell(), e), expected)

    def test_overlay_error_never_reaches_the_reticle(self):
        from ap_calculator.core import ap_hooks

        original = ap_hooks.call_update_gui

        def boom(*args):
            raise RuntimeError("overlay exploded")

        ap_hooks.call_update_gui = boom
        try:
            collisions = [hit(mat(100), angle_deg=30)]
            expected, _plates = stock_shot(DEFAULT, collisions, 200.0, shell(), entity())
            self.assertEqual(wrapped_shot(DEFAULT, collisions, 200.0, shell(), entity()), expected)
        finally:
            ap_hooks.call_update_gui = original

    def test_generator_collisions_reach_both_passes(self):
        from ap_calculator.gui.ap_gui import gui_state

        gui_state.create_window()
        collisions = [hit(mat(100), angle_deg=0)]
        wrapped_shot(DEFAULT, iter(collisions), 200.0, shell(), entity())
        values = support.overlay_values()
        self.assertEqual(values["armorText"], "100")
        self.assertTrue(values["armorVisible"])


if __name__ == "__main__":
    unittest.main()
