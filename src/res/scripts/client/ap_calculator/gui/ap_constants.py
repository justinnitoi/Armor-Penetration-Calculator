# -*- coding: utf-8 -*-
from ap_calculator.gui.ap_config import DEFAULT_CONFIG, JAILBROKEN, g_user_settings


def safe_get_setting(config, category, attribute):
    key = "{}.{}".format(category, attribute)
    try:
        setting = config[key]
    except KeyError:  # take the default
        setting = DEFAULT_CONFIG[key]
    return setting


def update_constants():
    """Updates constants from g_user_settings"""
    config = g_user_settings

    GlobalSettings.MOD_ENABLED = config.get("enabled", True)

    ArmorLabelSettings.ENABLED = safe_get_setting(config, "armor_label", "enabled")

    ProbLabelSettings.ENABLED = safe_get_setting(config, "prob_label", "enabled")

    AngleLabelSettings.ENABLED = safe_get_setting(config, "angle_label", "enabled")
    AngleLabelSettings.DISPLAY_THRESHOLD = safe_get_setting(
        config, "angle_label", "display_threshold"
    )
    AngleLabelSettings.WHITE = safe_get_setting(config, "angle_label", "always_white")

    Colors.HIGH_CHANCE = safe_get_setting(config, "colors", "high_chance")
    Colors.MEDIUM_CHANCE = safe_get_setting(config, "colors", "medium_chance")
    Colors.LOW_CHANCE = safe_get_setting(config, "colors", "low_chance")
    Colors.RICOCHET = safe_get_setting(config, "colors", "ricochet")
    Colors.GRADIENT = safe_get_setting(config, "colors", "gradient")

    Colorblind.ENABLED = safe_get_setting(config, "colorblind", "enabled")
    Colorblind.HIGH_CHANCE = safe_get_setting(config, "colorblind", "high_chance")
    Colorblind.MEDIUM_CHANCE = safe_get_setting(config, "colorblind", "medium_chance")
    Colorblind.LOW_CHANCE = safe_get_setting(config, "colorblind", "low_chance")
    Colorblind.RICOCHET = safe_get_setting(config, "colorblind", "ricochet")


class GlobalSettings:
    MOD_ENABLED = g_user_settings.get("enabled", True)


def get_color_from_prob(prob):
    if not Colorblind.ENABLED:
        return Colors.get_color_from_prob(prob)
    else:
        return Colorblind.get_color_from_prob(prob)


def get_ricochet_color():
    if not Colorblind.ENABLED:
        return Colors.RICOCHET
    else:
        return Colorblind.RICOCHET


def _hex_to_rgb(hex_color):
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "".join(
        "{:02X}".format(max(0, min(255, int(round(channel))))) for channel in rgb
    )


def _lerp_color(color_a, color_b, t):
    t = max(0.0, min(1.0, t))
    rgb_a = _hex_to_rgb(color_a)
    rgb_b = _hex_to_rgb(color_b)
    rgb = tuple(a + (b - a) * t for a, b in zip(rgb_a, rgb_b))
    return _rgb_to_hex(rgb)


# Penetration chance (%) at or below which a shot counts as low chance, and at
# or above which it counts as high chance.
LOW_CHANCE_MAX = 7
HIGH_CHANCE_MIN = 93
_GRADIENT_MIDPOINT = 50


def is_high_chance(prob):
    return prob >= HIGH_CHANCE_MIN


def _get_color_from_prob_gradient(cls, prob):
    if prob <= LOW_CHANCE_MAX:
        return cls.LOW_CHANCE
    elif is_high_chance(prob):
        return cls.HIGH_CHANCE
    elif prob < _GRADIENT_MIDPOINT:
        # red-orange: fades from the low chance color into orange
        t = (prob - LOW_CHANCE_MAX) / float(_GRADIENT_MIDPOINT - LOW_CHANCE_MAX)
        return _lerp_color(cls.LOW_CHANCE, cls.MEDIUM_CHANCE, t)
    else:
        # orange-green: fades from orange into the high chance color
        t = (prob - _GRADIENT_MIDPOINT) / float(HIGH_CHANCE_MIN - _GRADIENT_MIDPOINT)
        return _lerp_color(cls.MEDIUM_CHANCE, cls.HIGH_CHANCE, t)


def _get_color_from_prob_legacy(cls, prob):
    if prob <= LOW_CHANCE_MAX:
        return cls.LOW_CHANCE
    elif is_high_chance(prob):
        return cls.HIGH_CHANCE
    else:
        return cls.MEDIUM_CHANCE


class Colors(object):
    HIGH_CHANCE = safe_get_setting(g_user_settings, "colors", "high_chance")
    MEDIUM_CHANCE = safe_get_setting(g_user_settings, "colors", "medium_chance")
    LOW_CHANCE = safe_get_setting(g_user_settings, "colors", "low_chance")
    RICOCHET = safe_get_setting(g_user_settings, "colors", "ricochet")
    GRADIENT = safe_get_setting(g_user_settings, "colors", "gradient")

    GREEN = "6BF40D"
    ORANGE = "FFAD00"
    RED = "E90000"
    PURPLE = "800080"

    YELLOW = "FFFF00"
    GREY = "808080"
    WHITE = "FFFFFF"

    @classmethod
    def get_color_from_prob(cls, prob):
        if cls.GRADIENT:
            return _get_color_from_prob_gradient(cls, prob)
        else:
            return _get_color_from_prob_legacy(cls, prob)


class Colorblind(object):
    ENABLED = safe_get_setting(g_user_settings, "colorblind", "enabled")
    HIGH_CHANCE = safe_get_setting(g_user_settings, "colorblind", "high_chance")
    MEDIUM_CHANCE = safe_get_setting(g_user_settings, "colorblind", "medium_chance")
    LOW_CHANCE = safe_get_setting(g_user_settings, "colorblind", "low_chance")
    RICOCHET = safe_get_setting(g_user_settings, "colorblind", "ricochet")

    @classmethod
    def get_color_from_prob(cls, prob):
        if Colors.GRADIENT:
            return _get_color_from_prob_gradient(cls, prob)
        else:
            return _get_color_from_prob_legacy(cls, prob)


class ArmorLabelSettings:
    ENABLED = safe_get_setting(g_user_settings, "armor_label", "enabled")
    FORMAT = "{value}"


class ProbLabelSettings:
    ENABLED = safe_get_setting(g_user_settings, "prob_label", "enabled")
    FORMAT = "{value}%"


class AngleLabelSettings:
    ENABLED = safe_get_setting(g_user_settings, "angle_label", "enabled")
    FORMAT = "{value}°"
    DISPLAY_THRESHOLD = safe_get_setting(
        g_user_settings, "angle_label", "display_threshold"
    )
    WHITE = safe_get_setting(g_user_settings, "angle_label", "always_white")


class TrackIndicatorSettings:
    ENABLED = JAILBROKEN or safe_get_setting(
        g_user_settings, "track_indicator", "enabled"
    )
