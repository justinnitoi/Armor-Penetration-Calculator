import json
import os

DEFAULT_CONFIG = {
    "armor_label": {
        "enabled": True,
        "x_offset": 0,
        "y_offset": 30,
        "font_size": 20,
        "label_format": "{armor}",
    },
    "pen_label": {
        "enabled": True,
        "x_offset": 0,
        "y_offset": 50,
        "font_size": 16,
        "label_format": "{prob}%",
    },
    "angle_label": {
        "enabled": True,
        "x_offset": 30,
        "y_offset": 35,
        "font_size": 16,
        "label_format": "{angle}°",
        "display_threshold": 65,
    },
    "colors": {
        "green_chance": "6BF40D",
        "orange_chance": "FFAD00",
        "red_chance": "E90000",
        "ricochet": "800080",
    },
    "shadow": {
        "shadow_color": "000000",
        "shadow_alpha": 8,
        "shadow_length": 3,
        "shadow_strength": 7,
    },
}

CONFIG_FOLDER = os.path.join("mods", "configs", "pademinune")
CONFIG_PATH = os.path.join(CONFIG_FOLDER, "armor-calculator.json")


def create_config():
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    with open(CONFIG_PATH, "w") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)


def read_config():
    with open(CONFIG_PATH) as file:
        user_config = json.load(file)

    return user_config


def migrate_config(user_config):
    changed = False
    for section, defaults in DEFAULT_CONFIG.items():
        if section not in user_config:
            user_config[section] = defaults
            changed = True
        else:
            for key, value in defaults.items():
                if key not in user_config[section]:
                    user_config[section][key] = value
                    changed = True
    if changed:
        with open(CONFIG_PATH, "w") as f:
            json.dump(user_config, f, indent=4)
    return user_config


def save_flat_config(settings):
    config = {
        "armor_label": {
            "enabled": settings["armor_label_enabled"],
            "x_offset": settings["armor_label_x_offset"],
            "y_offset": settings["armor_label_y_offset"],
            "font_size": settings["armor_label_font_size"],
            "label_format": settings["armor_label_format"],
        },
        "pen_label": {
            "enabled": settings["pen_label_enabled"],
            "x_offset": settings["pen_label_x_offset"],
            "y_offset": settings["pen_label_y_offset"],
            "font_size": settings["pen_label_font_size"],
            "label_format": settings["pen_label_format"],
        },
        "angle_label": {
            "enabled": settings["angle_label_enabled"],
            "x_offset": settings["angle_label_x_offset"],
            "y_offset": settings["angle_label_y_offset"],
            "font_size": settings["angle_label_font_size"],
            "label_format": settings["angle_label_format"],
            "display_threshold": settings["angle_label_display_threshold"],
        },
        "colors": {
            "green_chance": settings["color_green"],
            "orange_chance": settings["color_orange"],
            "red_chance": settings["color_red"],
            "ricochet": settings["color_ricochet"],
        },
        "shadow": {
            "shadow_color": settings["shadow_color"],
            "shadow_alpha": settings["shadow_alpha"],
            "shadow_length": settings["shadow_length"],
            "shadow_strength": settings["shadow_strength"],
        },
    }

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


if not os.path.isfile(CONFIG_PATH):
    create_config()

try:
    user_settings = migrate_config(read_config())
except:
    # if the config is invalid, reset it
    create_config()
    user_settings = read_config()
