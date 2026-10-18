import json
import os

from ap_calculator.debug import log

DEFAULT_CONFIG = {
    "enabled": True,
    "armor_label.enabled": True,
    "prob_label.enabled": True,
    "angle_label.enabled": True,  # angle label
    "angle_label.display_threshold": 70,
    "angle_label.always_white": True,
    "colors.high_chance": "6BF40D",  # colors
    "colors.medium_chance": "FFAD00",
    "colors.low_chance": "E90000",
    "colors.ricochet": "800080",
    "colors.gradient": True,
    "colorblind.enabled": False,  # colorblind
    "colorblind.high_chance": "EFEB05",
    "colorblind.medium_chance": "FF8AFF",
    "colorblind.low_chance": "9D00FF",
    "colorblind.ricochet": "9D00FF",
    "track_indicator.enabled": False,
}


CONFIG_FOLDER = os.path.join(
    "mods", "configs", "pademinune", "Armor Penetration Calculator 2"
)
CONFIG_PATH = os.path.join(CONFIG_FOLDER, "config.json")
JAILBREAK_FLAG_PATH = os.path.join(CONFIG_FOLDER, ".jailbreak")


def is_jailbreak():
    """Returns true iff a `.jailbreak` file is in the config location"""
    return os.path.isfile(JAILBREAK_FLAG_PATH)


def update_global_settings(new_settings):
    """Updates g_user_settings from a settings panel's values. Values are
    coerced to their default's type (settings APIs can hand back unicode
    strings or floats, which the overlay would reject)."""
    global g_user_settings
    for key, value in new_settings.items():
        key = _to_str(key)
        if key not in DEFAULT_CONFIG:
            continue
        try:
            g_user_settings[key] = _coerce(key, value)
        except ValueError:
            log("Ignoring invalid value {!r} for setting {!r}.".format(value, key))


# Written into config.json alongside the overrides. Bump it, and migrate in
# load_config(), if a key is ever renamed or changes meaning.
CONFIG_VERSION = 1
_VERSION_KEY = "config_version"


def save_config():
    """Saves g_user_settings to disk"""
    global g_user_settings
    non_defaults = {k: v for k, v in g_user_settings.items() if v != DEFAULT_CONFIG[k]}
    non_defaults[_VERSION_KEY] = CONFIG_VERSION

    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    with open(CONFIG_PATH, "w") as fp:
        json.dump(non_defaults, fp, indent=4, sort_keys=True)


def _to_str(value):
    """json.load returns every string as unicode in Python 2; convert back to str
    so it matches the str defaults and what the rest of the mod expects."""
    if isinstance(value, unicode):  # type: ignore
        return value.encode("utf-8")
    return value


def _coerce(key, value):
    """Returns value as the type of DEFAULT_CONFIG[key]. Raises ValueError if it
    can't be (an int and a float convert to each other; nothing else does)."""
    default = DEFAULT_CONFIG[key]
    value = _to_str(value)
    if type(value) == type(default):
        return value
    # bool is an int subclass; never let one stand in for the other
    if isinstance(default, bool) or isinstance(value, bool):
        raise ValueError(key)
    if isinstance(default, (int, float)) and isinstance(value, (int, float)):
        return type(default)(value)
    raise ValueError(key)


def load_config():
    """Returns (settings, needs_save). A bad or unknown entry is dropped on its
    own (and logged) rather than resetting every setting."""
    with open(CONFIG_PATH) as file:
        saved = json.load(file)
    if not isinstance(saved, dict):
        raise ValueError("config root is not an object")

    user_config = dict(DEFAULT_CONFIG)
    needs_save = saved.get(_VERSION_KEY) != CONFIG_VERSION

    for key, value in saved.items():
        key = _to_str(key)
        if key == _VERSION_KEY:
            continue
        if key not in DEFAULT_CONFIG:
            log("Dropping unknown setting {!r} from config.json.".format(key))
            needs_save = True
            continue
        try:
            user_config[key] = _coerce(key, value)
        except ValueError:
            log("Resetting setting {!r}: {!r} is not a valid value.".format(key, value))
            needs_save = True

    return user_config, needs_save


def _back_up_unreadable_config():
    """Keeps an unreadable config.json as config.json.bak before it's replaced."""
    try:
        backup = CONFIG_PATH + ".bak"
        if os.path.exists(backup):
            os.remove(backup)
        os.rename(CONFIG_PATH, backup)
        log("config.json could not be read; saved it as config.json.bak and reset settings.")
    except OSError:
        pass


JAILBROKEN = is_jailbreak()
if JAILBROKEN:
    log("Mod is jailbroken.")
_needs_save = False
try:
    g_user_settings, _needs_save = load_config()
except IOError:
    # first launch: no config yet
    g_user_settings, _needs_save = dict(DEFAULT_CONFIG), True
except Exception:
    _back_up_unreadable_config()
    g_user_settings, _needs_save = dict(DEFAULT_CONFIG), True
if _needs_save:
    try:
        save_config()
    except Exception:
        log("Could not save config.json.")
