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
    """Updates g_user_settings variable"""
    relevant_settings = {k: v for k, v in new_settings.items() if k in DEFAULT_CONFIG}
    global g_user_settings
    g_user_settings.update(relevant_settings)


def save_config():
    """Saves g_user_settings to disk"""
    global g_user_settings
    non_defaults = {k: v for k, v in g_user_settings.items() if v != DEFAULT_CONFIG[k]}

    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    with open(CONFIG_PATH, "w") as fp:
        json.dump(non_defaults, fp, indent=4)


def _to_str(value):
    """json.load returns every string as unicode in Python 2; convert back to str
    so it matches the str defaults and what the rest of the mod expects."""
    if isinstance(value, unicode):  # type: ignore
        return value.encode("utf-8")
    return value


def load_config():
    with open(CONFIG_PATH) as file:
        non_defaults = json.load(file)

    user_config = dict(DEFAULT_CONFIG)

    for key, value in non_defaults.items():
        key, value = _to_str(key), _to_str(value)
        if type(value) != type(DEFAULT_CONFIG[key]):
            raise TypeError("Key: {} does not have the expected type.".format(key))
        user_config[key] = value

    return user_config


JAILBROKEN = is_jailbreak()
if JAILBROKEN:
    log("Mod is jailbroken.")
try:
    g_user_settings = load_config()
except:
    # if the config is invalid, reset it
    g_user_settings = dict(DEFAULT_CONFIG)
    save_config()
