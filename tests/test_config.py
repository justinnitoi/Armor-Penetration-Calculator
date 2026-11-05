import json
import os
import unittest

import support

support.setup()


def _config():
    from ap_calculator.gui import ap_config

    return ap_config


@support.requires_stock
class LoadConfigTest(unittest.TestCase):
    def setUp(self):
        self.cfg = _config()
        if not os.path.isdir(self.cfg.CONFIG_FOLDER):
            os.makedirs(self.cfg.CONFIG_FOLDER)

    def write(self, data):
        with open(self.cfg.CONFIG_PATH, "w") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))

    def test_bad_entries_are_dropped_one_by_one(self):
        self.write(
            {
                "colors.high_chance": "00FF00",
                "removed.in.some.version": True,
                "prob_label.enabled": "yes",
                "config_version": self.cfg.CONFIG_VERSION,
            }
        )
        settings, needs_save = self.cfg.load_config()
        self.assertEqual(settings["colors.high_chance"], "00FF00")
        self.assertIs(type(settings["colors.high_chance"]), str)
        self.assertNotIn("removed.in.some.version", settings)
        self.assertEqual(settings["prob_label.enabled"], self.cfg.DEFAULT_CONFIG["prob_label.enabled"])
        self.assertTrue(needs_save)

    def test_clean_file_needs_no_save(self):
        self.write({"angle_label.display_threshold": 60, "config_version": self.cfg.CONFIG_VERSION})
        settings, needs_save = self.cfg.load_config()
        self.assertEqual(settings["angle_label.display_threshold"], 60)
        self.assertFalse(needs_save)

    def test_old_file_without_version_is_rewritten(self):
        self.write({"angle_label.display_threshold": 60})
        _settings, needs_save = self.cfg.load_config()
        self.assertTrue(needs_save)

    def test_numbers_convert_but_bools_do_not(self):
        self.assertEqual(self.cfg._coerce("angle_label.display_threshold", 65.0), 65)
        self.assertIs(type(self.cfg._coerce("angle_label.display_threshold", 65.0)), int)
        with self.assertRaises(ValueError):
            self.cfg._coerce("angle_label.display_threshold", True)
        with self.assertRaises(ValueError):
            self.cfg._coerce("enabled", 1)

    def test_unparsable_file_raises_for_backup(self):
        self.write("{not json")
        with self.assertRaises(ValueError):
            self.cfg.load_config()
        self.cfg._back_up_unreadable_config()
        self.assertTrue(os.path.isfile(self.cfg.CONFIG_PATH + ".bak"))
        self.assertFalse(os.path.isfile(self.cfg.CONFIG_PATH))

    def test_settings_panel_values_are_coerced(self):
        saved = dict(self.cfg.g_user_settings)
        try:
            self.cfg.update_global_settings({u"colors.ricochet": u"123456", "unknown": 1})
            self.assertIs(type(self.cfg.g_user_settings["colors.ricochet"]), str)
            self.assertNotIn("unknown", self.cfg.g_user_settings)
        finally:
            self.cfg.g_user_settings.clear()
            self.cfg.g_user_settings.update(saved)


if __name__ == "__main__":
    unittest.main()
