import json
import os

DEFAULT_CONFIG = {
    "armor_label": {
        "enabled": True,
        "x_offset": 0,
        "y_offset": 30,
        "font_size": 20,
        "label_format": "{value}",
    },
    "pen_label": {
        "enabled": True,
        "x_offset": 0,
        "y_offset": 50,
        "font_size": 16,
        "label_format": "{value}%",
    },
    "angle_label": {
        "enabled": True,
        "x_offset": 30,
        "y_offset": 35,
        "font_size": 16,
        "label_format": "{value}°",
        "display_threshold": 70,
    },
    "eff_pen_label": {
        "enabled": False,
        "x_offset": -50,
        "y_offset": 35,
        "font_size": 16,
        "label_format": "{value}",
    },
    "kill_label": {
        "enabled": False,
        "x_offset": 0,
        "y_offset": 66,
        "font_size": 14,
        "label_format": "† {value}%",
    },
    "gun_label": {
        "enabled": True,
        "x_offset": -26,
        "y_offset": 35,
        "font_size": 16,
        "label_format": "‡",
    },
    "colors": {
        "gradient": True,
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
JAILBREAK_FLAG_PATH = os.path.join(CONFIG_FOLDER, ".jailbreak")


def is_jailbreak():
    return os.path.isfile(JAILBREAK_FLAG_PATH)


def create_config():
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    with open(CONFIG_PATH, "w") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)


def read_config():
    with open(CONFIG_PATH) as file:
        user_config = json.load(file)

    return user_config


def nested(flat_config):
    nested_config = {
        "armor_label": {
            "enabled": flat_config["armor_label_enabled"],
            "x_offset": flat_config["armor_label_x_offset"],
            "y_offset": flat_config["armor_label_y_offset"],
            "font_size": flat_config["armor_label_font_size"],
            "label_format": flat_config["armor_label_format"],
        },
        "pen_label": {
            "enabled": flat_config["pen_label_enabled"],
            "x_offset": flat_config["pen_label_x_offset"],
            "y_offset": flat_config["pen_label_y_offset"],
            "font_size": flat_config["pen_label_font_size"],
            "label_format": flat_config["pen_label_format"],
        },
        "angle_label": {
            "enabled": flat_config["angle_label_enabled"],
            "x_offset": flat_config["angle_label_x_offset"],
            "y_offset": flat_config["angle_label_y_offset"],
            "font_size": flat_config["angle_label_font_size"],
            "label_format": flat_config["angle_label_format"],
            "display_threshold": flat_config["angle_label_display_threshold"],
        },
        "eff_pen_label": {
            "enabled": flat_config["eff_pen_label_enabled"],
            "x_offset": flat_config["eff_pen_label_x_offset"],
            "y_offset": flat_config["eff_pen_label_y_offset"],
            "font_size": flat_config["eff_pen_label_font_size"],
            "label_format": flat_config["eff_pen_label_format"],
        },
        "kill_label": {
            "enabled": flat_config["kill_label_enabled"],
            "x_offset": flat_config["kill_label_x_offset"],
            "y_offset": flat_config["kill_label_y_offset"],
            "font_size": flat_config["kill_label_font_size"],
            "label_format": flat_config["kill_label_format"],
        },
        "gun_label": {
            "enabled": flat_config["gun_label_enabled"],
            "x_offset": flat_config["gun_label_x_offset"],
            "y_offset": flat_config["gun_label_y_offset"],
            "font_size": flat_config["gun_label_font_size"],
            "label_format": flat_config["gun_label_format"],
        },
        "colors": {
            "gradient": flat_config["color_gradient"],
            "green_chance": flat_config["color_green"],
            "orange_chance": flat_config["color_orange"],
            "red_chance": flat_config["color_red"],
            "ricochet": flat_config["color_ricochet"],
        },
        "shadow": {
            "shadow_color": flat_config["shadow_color"],
            "shadow_alpha": flat_config["shadow_alpha"],
            "shadow_length": flat_config["shadow_length"],
            "shadow_strength": flat_config["shadow_strength"],
        },
    }
    return nested_config


LEGACY_LABEL_FORMAT_FIELDS = {
    "armor_label": "armor",
    "pen_label": "prob",
    "angle_label": "angle",
    "eff_pen_label": "eff_pen",
    "kill_label": "kill_prob",
}


def migrate_label_format_placeholders(user_config):
    changed = False
    for section, old_field in LEGACY_LABEL_FORMAT_FIELDS.items():
        label_format = user_config.get(section, {}).get("label_format")
        if not label_format:
            continue
        old_placeholder = "{" + old_field + "}"
        if old_placeholder in label_format:
            user_config[section]["label_format"] = label_format.replace(
                old_placeholder, "{value}"
            )
            changed = True
    return changed


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
    if migrate_label_format_placeholders(user_config):
        changed = True
    if changed:
        with open(CONFIG_PATH, "w") as f:
            json.dump(user_config, f, indent=4)
    return user_config


def save_flat_config(flat_config):
    nested_config = nested(flat_config)

    with open(CONFIG_PATH, "w") as f:
        json.dump(nested_config, f, indent=4)


if not os.path.isfile(CONFIG_PATH):
    create_config()

try:
    user_settings = migrate_config(read_config())
except:
    # if the config is invalid, reset it
    create_config()
    user_settings = read_config()
