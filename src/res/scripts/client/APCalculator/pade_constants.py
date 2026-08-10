from APCalculator.pade_config import user_settings, DEFAULT_CONFIG, is_jailbreak


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


VERSION = "2.0.0"


class Colors(object):
    RED = safe_get_color("red_chance")
    YELLOW = "FFFF00"
    ORANGE = safe_get_color("orange_chance")
    GREEN = safe_get_color("green_chance")
    GREY = "808080"
    WHITE = "FFFFFF"
    PURPLE = safe_get_color("ricochet")

    @classmethod
    def get_color_from_prob(cls, prob):
        if prob <= 7:
            return cls.RED
        elif prob >= 93:
            return cls.GREEN
        else:
            return cls.ORANGE


class ArmorLabelSettings:
    ENABLED = safe_get_setting("armor_label", "enabled")
    LABEL_FORMAT = safe_get_setting("armor_label", "label_format")
    FONT_SIZE = safe_get_setting("armor_label", "font_size")
    X_OFFSET = safe_get_setting("armor_label", "x_offset")
    Y_OFFSET = safe_get_setting("armor_label", "y_offset")


class PenLabelSettings:
    ENABLED = safe_get_setting("pen_label", "enabled")
    LABEL_FORMAT = safe_get_setting("pen_label", "label_format")
    FONT_SIZE = safe_get_setting("pen_label", "font_size")
    X_OFFSET = safe_get_setting("pen_label", "x_offset")
    Y_OFFSET = safe_get_setting("pen_label", "y_offset")


class AngleLabelSettings:
    ENABLED = safe_get_setting("angle_label", "enabled")
    LABEL_FORMAT = safe_get_setting("angle_label", "label_format")
    FONT_SIZE = safe_get_setting("angle_label", "font_size")
    X_OFFSET = safe_get_setting("angle_label", "x_offset")
    Y_OFFSET = safe_get_setting("angle_label", "y_offset")
    DISPLAY_THRESHOLD = safe_get_setting("angle_label", "display_threshold")


class EffPenLabelSettings:
    ENABLED = safe_get_setting("eff_pen_label", "enabled")
    LABEL_FORMAT = safe_get_setting("eff_pen_label", "label_format")
    FONT_SIZE = safe_get_setting("eff_pen_label", "font_size")
    X_OFFSET = safe_get_setting("eff_pen_label", "x_offset")
    Y_OFFSET = safe_get_setting("eff_pen_label", "y_offset")


class KillLabelSettings:
    ENABLED = safe_get_setting("kill_label", "enabled")
    LABEL_FORMAT = safe_get_setting("kill_label", "label_format")
    FONT_SIZE = safe_get_setting("kill_label", "font_size")
    X_OFFSET = safe_get_setting("kill_label", "x_offset")
    Y_OFFSET = safe_get_setting("kill_label", "y_offset")


class GunLabelSettings:
    ENABLED = safe_get_setting("gun_label", "enabled")
    LABEL_FORMAT = safe_get_setting("gun_label", "label_format")
    FONT_SIZE = safe_get_setting("gun_label", "font_size")
    X_OFFSET = safe_get_setting("gun_label", "x_offset")
    Y_OFFSET = safe_get_setting("gun_label", "y_offset")


class ShadowSettings:
    COLOR = safe_get_setting("shadow", "shadow_color")
    ALPHA = safe_get_setting("shadow", "shadow_alpha")
    LENGTH = safe_get_setting("shadow", "shadow_length")
    STRENGTH = safe_get_setting("shadow", "shadow_strength")


class TrackLabelSettings:
    ENABLED = is_jailbreak()
    X_OFFSET = 0
    Y_OFFSET = 0
    IMAGES = [
        ("pademinune_GreenTrack", "img://gui/pademinune/crosshair-32-green.png"),
        ("pademinune_OrangeTrack", "img://gui/pademinune/crosshair-32-orange.png"),
    ]
