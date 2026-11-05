import io
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSLATIONS = os.path.join(ROOT, "src", "res", "gui", "AP_Calculator_2", "translations")
LANGUAGE_PY = os.path.join(ROOT, "src", "res", "scripts", "client", "ap_calculator", "settings_gui", "language.py")


def _flatten(data, prefix=""):
    keys = set()
    for key, value in data.items():
        full = prefix + key
        if isinstance(value, dict):
            keys |= _flatten(value, full + ".")
        else:
            keys.add(full)
    return keys


def _load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


class TranslationsTest(unittest.TestCase):
    def test_every_language_has_exactly_the_english_keys(self):
        english = _flatten(_load(os.path.join(TRANSLATIONS, "translations_en.json")))
        for name in sorted(os.listdir(TRANSLATIONS)):
            if not name.endswith(".json"):
                continue
            keys = _flatten(_load(os.path.join(TRANSLATIONS, name)))
            self.assertEqual(sorted(english - keys), [], "{} is missing keys".format(name))
            self.assertEqual(sorted(keys - english), [], "{} has extra keys".format(name))

    def test_every_supported_language_has_a_file(self):
        with io.open(LANGUAGE_PY, encoding="utf-8") as f:
            source = f.read()
        block = re.search(r"SUPPORTED_LANGUAGES = \((.*?)\)", source, re.S).group(1)
        for lang in re.findall(r'"([a-z_]+)"', block):
            path = os.path.join(TRANSLATIONS, "translations_{}.json".format(lang))
            self.assertTrue(os.path.isfile(path), "no translation file for " + lang)


if __name__ == "__main__":
    unittest.main()
