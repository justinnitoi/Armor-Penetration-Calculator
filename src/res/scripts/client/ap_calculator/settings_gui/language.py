import json
import os

import ResMgr  # type: ignore
from helpers import getClientLanguage  # type: ignore

from ap_calculator.debug import log

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = (
    "en",
    "uk",
    "ru",
    "de",
    "pl",
    "cs",
    "ro",
    "sk",
    "be",
    "bg",
    "et",
    "hr",
    "hu",
    "lt",
    "lv",
    "sr",
    "zh_cn",
)
ALIASES = {
    "ua": "uk",
}

_RESOURCE_TEMPLATE = "gui/AP_Calculator_2/translations/translations_%s.json"


def _normalize_language(lang):
    try:
        lang = lang.lower().replace("-", "_")
    except Exception:
        return DEFAULT_LANGUAGE

    if lang in SUPPORTED_LANGUAGES:
        return lang

    # normalize regional variants such as uk_UA, de_DE, pl_PL, etc.
    lang = lang.split("_", 1)[0]
    lang = ALIASES.get(lang, lang)
    if lang not in SUPPORTED_LANGUAGES:
        return DEFAULT_LANGUAGE
    return lang


def _client_language():
    try:
        return _normalize_language(getClientLanguage())
    except Exception as e:
        log("Failed to detect client language, falling back to English: {}".format(e))
        return DEFAULT_LANGUAGE


def _decode_json(raw):
    if raw is None:
        return {}

    # WoT runs this mod under Python 2.7, where json.loads accepts byte
    # strings and can decode UTF-8 directly.
    try:
        return json.loads(raw, encoding="UTF-8")
    except TypeError:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return json.loads(raw)


def _load_json(lang):
    path = _RESOURCE_TEMPLATE % lang

    try:
        section = ResMgr.openSection(path)
        if section is not None:
            return _decode_json(section.asBinary)
    except Exception as e:
        log("Failed to load localization resource {}: {}".format(path, e))

    # Development fallback for an unpacked repository tree.
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        res_root = os.path.abspath(os.path.join(here, "..", "..", "..", ".."))
        filename = "translations_%s.json" % lang
        fs_path = os.path.join(
            res_root, "gui", "AP_Calculator_2", "translations", filename
        )
        with open(fs_path, "rb") as stream:
            return _decode_json(stream.read())
    except Exception:
        return {}


_LANGUAGE = _client_language()
_EN = _load_json(DEFAULT_LANGUAGE)
_CURRENT = _EN if _LANGUAGE == DEFAULT_LANGUAGE else _load_json(_LANGUAGE)

if not _CURRENT and _LANGUAGE != DEFAULT_LANGUAGE:
    log(
        "Translations for language {} not found, falling back to English".format(
            _LANGUAGE
        )
    )
    _CURRENT = _EN


def language():
    return _LANGUAGE


def tr(key, **kwargs):
    """Returns localized text for `key`, falling back to English then to `key` itself."""
    value = _CURRENT.get(key, _EN.get(key, key))
    if kwargs:
        try:
            value = value.format(**kwargs)
        except Exception:
            pass
    return value


def tooltip(title_key, body_key):
    return "{{HEADER}}{header}{{/HEADER}}{{BODY}}{body}{{/BODY}}".format(
        header=tr(title_key), body=tr(body_key)
    )
