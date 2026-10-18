import unittest

import support

support.setup()

import fakes  # noqa: E402
from fakes import GUN_MARKER_TYPE, SHOT_RESULT, GunMarkerState  # noqa: E402
from support import entity, hit, mat, shell, wrapped_shot  # noqa: E402


def _ap_hooks():
    from ap_calculator.core import ap_hooks

    return ap_hooks


def _gui_state():
    from ap_calculator.gui.ap_gui import gui_state

    return gui_state


@support.requires_stock
class CompatibilityTest(unittest.TestCase):
    def test_current_stock_class_is_compatible(self):
        # the pinned stock file, before the mod wrapped it
        stock_cls = support.STOCK._CrosshairShotResults

        class Unwrapped(object):
            pass

        for name in dir(stock_cls):
            if not name.startswith("__"):
                setattr(Unwrapped, name, getattr(stock_cls, name))
        for name, func in support.STOCK_ORIGINALS.items():
            setattr(Unwrapped, name, classmethod(func))
        self.assertEqual(_ap_hooks()._check_compatibility(Unwrapped), [])

    def test_missing_internal_is_reported(self):
        class Broken(object):
            @classmethod
            def getShotResult(cls, gunMarker, excludeTeam=0, piercingMultiplier=1):
                pass

        problems = _ap_hooks()._check_compatibility(Broken)
        self.assertIn("missing _shouldRicochet", problems)

    def test_changed_signature_is_reported(self):
        stock_cls = support.STOCK._CrosshairShotResults

        class Changed(object):
            _shouldRicochet = stock_cls._shouldRicochet
            _computePenetrationArmor = stock_cls._computePenetrationArmor
            _SHELL_EXTRA_DATA = stock_cls._SHELL_EXTRA_DATA
            _CrosshairShotResults__isDestructibleComponent = True

            @classmethod
            def _CrosshairShotResults__shotResultDefault(cls, gunMarker, collisionsDetails, newArg):
                pass

            _CrosshairShotResults__shotResultModernHE = classmethod(
                support.STOCK_ORIGINALS[support.MODERN_HE_NAME]
            )
            getShotResult = classmethod(support.STOCK_ORIGINALS["getShotResult"])

        problems = _ap_hooks()._check_compatibility(Changed)
        self.assertEqual(problems, ["_CrosshairShotResults__shotResultDefault signature changed"])


@support.requires_stock
class OverlayLifecycleTest(unittest.TestCase):
    def setUp(self):
        _gui_state().create_window()
        wrapped_shot(support.DEFAULT_NAME, [hit(mat(100))], 200.0, shell(), entity())
        self.assertTrue(support.overlay_values()["armorVisible"])

    def test_no_target_hides_overlay(self):
        cls = support.STOCK._CrosshairShotResults
        no_target = GunMarkerState(0, 0, None, None, 0.0, None)
        self.assertEqual(cls.getShotResult(no_target, 0, 1), SHOT_RESULT.UNDEFINED)
        self.assertFalse(support.overlay_values()["armorVisible"])

    def test_death_hides_overlay(self):
        handler = fakes.AvatarInputHandler()
        handler.activatePostmortem()
        self.assertTrue(handler.postmortem_activated)  # stock still runs
        self.assertFalse(support.overlay_values()["armorVisible"])


class ServerReticleFilterTest(unittest.TestCase):
    """The stock plugin resolves the shot once per marker; with the server
    reticle on, only the server marker may drive the overlay."""

    def setUp(self):
        hooks = _ap_hooks()

        class Spy(object):
            seen = []

            @classmethod
            def getShotResult(cls, gunMarker, excludeTeam=0, piercingMultiplier=1):
                cls.seen.append(hooks._overlay_allowed)
                return SHOT_RESULT.UNDEFINED

        self.spy = Spy
        fakes.ShotResultIndicatorPlugin.resolver = Spy
        self.plugin = fakes.ShotResultIndicatorPlugin()

    def tearDown(self):
        fakes.GunMarkersSetInfo.SERVER_ACTIVE = False

    def test_follows_every_marker_without_server_reticle(self):
        self.plugin.fire(GUN_MARKER_TYPE.CLIENT, None)
        self.plugin.fire(GUN_MARKER_TYPE.SERVER, None)
        self.assertEqual(self.spy.seen, [True, True])

    def test_follows_only_server_marker_with_server_reticle(self):
        fakes.GunMarkersSetInfo.SERVER_ACTIVE = True
        self.plugin.fire(GUN_MARKER_TYPE.CLIENT, None)
        self.plugin.fire(GUN_MARKER_TYPE.SERVER, None)
        self.assertEqual(self.spy.seen, [False, True])
        self.assertTrue(_ap_hooks()._overlay_allowed)  # reset after each call


if __name__ == "__main__":
    unittest.main()
