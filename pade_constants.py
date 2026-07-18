from pade_config import user_settings, DEFAULT_CONFIG


def safe_get_color(color):
    default = DEFAULT_CONFIG.get("colors", "808080").get(color, "808080")
    if "colors" not in user_settings or color not in user_settings["colors"]:
        return default
    return user_settings["colors"][color]


def safe_get_setting(label, attribute):
    default = DEFAULT_CONFIG[label][attribute]
    if label not in user_settings or attribute not in user_settings[label]:
        return default
    return user_settings[label][attribute]


class Colors:
    RED = safe_get_color("red_chance")
    YELLOW = "FFFF00"
    ORANGE = safe_get_color("orange_chance")
    GREEN = safe_get_color("green_chance")
    GREY = "808080"
    PURPLE = safe_get_color("ricochet")


class ArmorLabel:
    ENABLED = safe_get_setting("armor_label", "enabled")
    LABEL_FORMAT = safe_get_setting("armor_label", "label_format")
    FONT_SIZE = safe_get_setting("armor_label", "font_size")
    X_OFFSET = safe_get_setting("armor_label", "x_offset")
    Y_OFFSET = safe_get_setting("armor_label", "y_offset")


class PenLabel:
    ENABLED = safe_get_setting("pen_label", "enabled")
    LABEL_FORMAT = safe_get_setting("pen_label", "label_format")
    FONT_SIZE = safe_get_setting("pen_label", "font_size")
    X_OFFSET = safe_get_setting("pen_label", "x_offset")
    Y_OFFSET = safe_get_setting("pen_label", "y_offset")


class AngleLabel:
    ENABLED = safe_get_setting("angle_label", "enabled")
    LABEL_FORMAT = safe_get_setting("angle_label", "label_format")
    FONT_SIZE = safe_get_setting("angle_label", "font_size")
    X_OFFSET = safe_get_setting("angle_label", "x_offset")
    Y_OFFSET = safe_get_setting("angle_label", "y_offset")
    DISPLAY_THRESHOLD = safe_get_setting("angle_label", "display_threshold")


class Shadow:
    COLOR = safe_get_setting("shadow", "shadow_color")
    ALPHA = safe_get_setting("shadow", "shadow_alpha")
    LENGTH = safe_get_setting("shadow", "shadow_length")
    STRENGTH = safe_get_setting("shadow", "shadow_strength")
