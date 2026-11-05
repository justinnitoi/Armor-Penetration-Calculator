import unittest

import support

support.setup()


def _modules():
    from ap_calculator.gui import ap_constants
    from ap_calculator.gui.ap_gui import gui_state

    return ap_constants, gui_state


@support.requires_stock
class TrackIndicatorTest(unittest.TestCase):
    def setUp(self):
        self.constants, self.gui_state = _modules()
        self.saved = (
            self.constants.TrackIndicatorSettings.ENABLED,
            self.constants.Colorblind.ENABLED,
        )
        self.constants.TrackIndicatorSettings.ENABLED = True
        self.gui_state.create_window()

    def tearDown(self):
        (
            self.constants.TrackIndicatorSettings.ENABLED,
            self.constants.Colorblind.ENABLED,
        ) = self.saved

    def show(self, prob, hit_body=True, ricochet=False):
        self.gui_state.update_gui(100, prob, ricochet, hit_body, 10, True)
        return support.overlay_values()["trackVisible"]

    def test_shown_on_high_chance(self):
        self.assertTrue(self.show(95))
        self.assertFalse(self.show(50))

    def test_shown_in_colorblind_mode(self):
        # used to compare against the normal palette's color, so it never showed
        self.constants.Colorblind.ENABLED = True
        self.assertTrue(self.show(95))

    def test_hidden_on_ricochet_or_miss(self):
        self.assertFalse(self.show(95, ricochet=True))
        self.assertFalse(self.show(95, hit_body=False))


@support.requires_stock
class GamefaceWindowTest(unittest.TestCase):
    def setUp(self):
        from ap_calculator.gui.ap_gameface_api import ap_window

        self.window = ap_window
        self.window.open_window()
        self.model = self.window._active[1].viewModel

    def test_unchanged_values_send_nothing(self):
        self.window.update_params([("armorText", "123")])
        before = self.model.transactions
        self.window.update_params([("armorText", "123")])
        self.assertEqual(self.model.transactions, before)

    def test_wrong_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.window.update_params([("armorText", u"123")])


if __name__ == "__main__":
    unittest.main()
