from pade_config import user_settings, DEFAULT_CONFIG, is_jailbreak


def update_constants_flat(flat_config):
    ArmorLabelSettings.ENABLED = flat_config["armor_label_enabled"]
    ArmorLabelSettings.FONT_SIZE = flat_config["armor_label_font_size"]
    ArmorLabelSettings.X_OFFSET = flat_config["armor_label_x_offset"]
    ArmorLabelSettings.Y_OFFSET = flat_config["armor_label_y_offset"]
    ArmorLabelSettings.LABEL_FORMAT = flat_config["armor_label_format"]
    PenLabelSettings.ENABLED = flat_config["pen_label_enabled"]
    PenLabelSettings.FONT_SIZE = flat_config["pen_label_font_size"]
    PenLabelSettings.X_OFFSET = flat_config["pen_label_x_offset"]
    PenLabelSettings.Y_OFFSET = flat_config["pen_label_y_offset"]
    PenLabelSettings.LABEL_FORMAT = flat_config["pen_label_format"]
    AngleLabelSettings.ENABLED = flat_config["angle_label_enabled"]
    AngleLabelSettings.FONT_SIZE = flat_config["angle_label_font_size"]
    AngleLabelSettings.X_OFFSET = flat_config["angle_label_x_offset"]
    AngleLabelSettings.Y_OFFSET = flat_config["angle_label_y_offset"]
    AngleLabelSettings.LABEL_FORMAT = flat_config["angle_label_format"]
    AngleLabelSettings.DISPLAY_THRESHOLD = flat_config["angle_label_display_threshold"]
    EffPenLabelSettings.ENABLED = flat_config["eff_pen_label_enabled"]
    EffPenLabelSettings.FONT_SIZE = flat_config["eff_pen_label_font_size"]
    EffPenLabelSettings.X_OFFSET = flat_config["eff_pen_label_x_offset"]
    EffPenLabelSettings.Y_OFFSET = flat_config["eff_pen_label_y_offset"]
    EffPenLabelSettings.LABEL_FORMAT = flat_config["eff_pen_label_format"]
    KillLabelSettings.ENABLED = flat_config["kill_label_enabled"]
    KillLabelSettings.FONT_SIZE = flat_config["kill_label_font_size"]
    KillLabelSettings.X_OFFSET = flat_config["kill_label_x_offset"]
    KillLabelSettings.Y_OFFSET = flat_config["kill_label_y_offset"]
    KillLabelSettings.LABEL_FORMAT = flat_config["kill_label_format"]
    GunLabelSettings.ENABLED = flat_config["gun_label_enabled"]
    GunLabelSettings.FONT_SIZE = flat_config["gun_label_font_size"]
    GunLabelSettings.X_OFFSET = flat_config["gun_label_x_offset"]
    GunLabelSettings.Y_OFFSET = flat_config["gun_label_y_offset"]
    GunLabelSettings.LABEL_FORMAT = flat_config["gun_label_format"]
    Colors.GREEN = flat_config["color_green"]
    Colors.ORANGE = flat_config["color_orange"]
    Colors.RED = flat_config["color_red"]
    Colors.PURPLE = flat_config["color_ricochet"]
    ShadowSettings.COLOR = flat_config["shadow_color"]
    ShadowSettings.ALPHA = flat_config["shadow_alpha"]
    ShadowSettings.LENGTH = flat_config["shadow_length"]
    ShadowSettings.STRENGTH = flat_config["shadow_strength"]


def safe_get_setting(category, attribute):
    default = DEFAULT_CONFIG[category][attribute]
    if category not in user_settings or attribute not in user_settings[category]:
        return default
    return user_settings[category][attribute]


VERSION = "1.8.3"


def log(message):
    print("[AP Calculator {}] {}".format(VERSION, message))


class Colors(object):
    RED = safe_get_setting("colors", "red_chance")
    YELLOW = "FFFF00"
    ORANGE = safe_get_setting("colors", "orange_chance")
    GREEN = safe_get_setting("colors", "green_chance")
    GREY = "808080"
    PURPLE = safe_get_setting("colors", "ricochet")

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
