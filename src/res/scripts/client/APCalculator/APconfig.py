import json
import os
from APCalculator.debug import log

DEFAULT_CONFIG = {
    "armor_label.enabled": True,
    "prob_label.enabled": True,
    "angle_label.enabled": True,  # angle label
    "angle_label.display_threshold": 70,
    "angle_label.always_white": True,
    "colors.high_chance": "6BF40D",  # colors
    "colors.medium_chance": "FFAD00",
    "colors.low_chance": "E90000",
    "colors.ricochet": "800080",
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
CONFIG_PATH = os.path.join(CONFIG_FOLDER, "AP_Calculator-2.1.0+.json")
JAILBREAK_FLAG_PATH = os.path.join(CONFIG_FOLDER, ".jailbreak")


def is_jailbreak():
    """Returns true iff a `.jailbreak` file is in the config location"""
    return os.path.isfile(JAILBREAK_FLAG_PATH)


def update_global_settings(new_settings):
    """Updates g_user_settings variable"""
    global g_user_settings
    for key, value in new_settings.items():
        if key in DEFAULT_CONFIG:
            g_user_settings[key] = value


def save_config():
    """Saves g_user_settings to disk"""
    global g_user_settings
    non_defaults = {}
    for key, value in g_user_settings.items():
        if key in DEFAULT_CONFIG and DEFAULT_CONFIG[key] != value:
            # check that its not default
            non_defaults[key] = value

    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    with open(CONFIG_PATH, "w") as fp:
        json.dump(non_defaults, fp, indent=4)


def load_config():
    with open(CONFIG_PATH) as file:
        non_defaults = json.load(file)

    user_config = dict(DEFAULT_CONFIG)

    for key, value in non_defaults.items():
        if type(DEFAULT_CONFIG[key]) != type(value):
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
