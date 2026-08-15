import json
import os

DEFAULT_CONFIG = {
    "armor_label": {
        "enabled": True,
        "format": "{value}",
    },
    "prob_label": {
        "enabled": True,
        "format": "{value}%",
    },
    "angle_label": {
        "enabled": True,
        "format": "{value}°",
        "display_threshold": 70,
        "white": True,
    },
    "colors": {
        "high_chance": "6BF40D",
        "medium_chance": "FFAD00",
        "low_chance": "E90000",
        "ricochet": "800080",
    },
}

CONFIG_FOLDER = os.path.join(
    "mods", "configs", "pademinune", "Armor Penetration Calculator 2"
)
CONFIG_PATH = os.path.join(CONFIG_FOLDER, "AP-Calculator-2.json")
JAILBREAK_FLAG_PATH = os.path.join(CONFIG_FOLDER, ".jailbreak")


def is_jailbreak():
    return os.path.isfile(JAILBREAK_FLAG_PATH)


def save_config(config):
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    with open(CONFIG_PATH, "w") as fp:
        json.dump(config, fp, indent=4)


def load_config():
    with open(CONFIG_PATH) as file:
        user_config = json.load(file)

    return user_config


def flattened(config):
    """Takes a nested config and returns the flattened version of it."""
    flattened = {}
    for key, val in config.items():
        for subkey, subval in val.items():
            flattened["{}_{}".format(key, subkey)] = subval
    return flattened


def nested(flat_config):
    """Takes a flat config and returns the nested version of it"""
    config = {
        "armor_label": {
            "enabled": flat_config["armor_label_enabled"],
            "format": flat_config["armor_label_format"],
        },
        "prob_label": {
            "enabled": flat_config["prob_label_enabled"],
            "format": flat_config["prob_label_format"],
        },
        "angle_label": {
            "enabled": flat_config["angle_label_enabled"],
            "format": flat_config["angle_label_format"],
            "display_threshold": flat_config["angle_label_display_threshold"],
            "white": flat_config["angle_label_white"],
        },
        "colors": {
            "high_chance": flat_config["colors_high_chance"],
            "medium_chance": flat_config["colors_medium_chance"],
            "low_chance": flat_config["colors_low_chance"],
            "ricochet": flat_config["colors_ricochet"],
        },
    }
    return config


def save_flat_config(flat_config):
    """Takes a flat config and saves it as a nested config to the drive"""
    config = nested(flat_config)
    save_config(config)


if not os.path.isfile(CONFIG_PATH):
    save_config(DEFAULT_CONFIG)

try:
    user_settings = load_config()
except:
    # if the config is invalid, reset it
    save_config(DEFAULT_CONFIG)
    user_settings = load_config()

if __name__ == "__main__":
    print(json.dumps(flattened(DEFAULT_CONFIG), indent=4))
