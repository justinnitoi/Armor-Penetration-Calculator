from APCalculator.APconfig import g_user_settings, DEFAULT_CONFIG, JAILBROKEN


def safe_get_setting(config, category, attribute):
    key = "{}.{}".format(category, attribute)
    try:
        setting = config[key]
    except KeyError:  # take the default
        setting = DEFAULT_CONFIG[key]
    return setting


def update_constants(config):
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

    Colorblind.ENABLED = safe_get_setting(config, "colorblind", "enabled")
    Colorblind.HIGH_CHANCE = safe_get_setting(config, "colorblind", "high_chance")
    Colorblind.MEDIUM_CHANCE = safe_get_setting(config, "colorblind", "medium_chance")
    Colorblind.LOW_CHANCE = safe_get_setting(config, "colorblind", "low_chance")
    Colorblind.RICOCHET = safe_get_setting(config, "colorblind", "ricochet")


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


def get_missed_body_color():
    if not Colorblind.ENABLED:
        return Colors.LOW_CHANCE
    else:
        return Colorblind.LOW_CHANCE


class Colors(object):
    HIGH_CHANCE = safe_get_setting(g_user_settings, "colors", "high_chance")
    MEDIUM_CHANCE = safe_get_setting(g_user_settings, "colors", "medium_chance")
    LOW_CHANCE = safe_get_setting(g_user_settings, "colors", "low_chance")
    RICOCHET = safe_get_setting(g_user_settings, "colors", "ricochet")

    GREEN = "6BF40D"
    ORANGE = "FFAD00"
    RED = "E90000"
    PURPLE = "800080"

    YELLOW = "FFFF00"
    GREY = "808080"
    WHITE = "FFFFFF"

    @classmethod
    def get_color_from_prob(cls, prob):
        if prob <= 7:
            return cls.LOW_CHANCE
        elif prob >= 93:
            return cls.HIGH_CHANCE
        else:
            return cls.MEDIUM_CHANCE


class Colorblind(object):
    ENABLED = safe_get_setting(g_user_settings, "colorblind", "enabled")
    HIGH_CHANCE = safe_get_setting(g_user_settings, "colorblind", "high_chance")
    MEDIUM_CHANCE = safe_get_setting(g_user_settings, "colorblind", "medium_chance")
    LOW_CHANCE = safe_get_setting(g_user_settings, "colorblind", "low_chance")
    RICOCHET = safe_get_setting(g_user_settings, "colorblind", "ricochet")

    @classmethod
    def get_color_from_prob(cls, prob):
        if prob <= 7:
            return cls.LOW_CHANCE
        elif prob >= 93:
            return cls.HIGH_CHANCE
        else:
            return cls.MEDIUM_CHANCE


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
    ENABLED = JAILBROKEN
