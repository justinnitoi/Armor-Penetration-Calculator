from APCalculator.APconfig import user_settings, DEFAULT_CONFIG, is_jailbreak

VERSION = "2.0.0"


def safe_get_setting(label, attribute):
    default = DEFAULT_CONFIG[label][attribute]
    if label not in user_settings or attribute not in user_settings[label]:
        return default
    return user_settings[label][attribute]


def update_constants(config):
    ArmorLabelSettings.ENABLED = config["armor_label"]["enabled"]

    ProbLabelSettings.ENABLED = config["prob_label"]["enabled"]

    AngleLabelSettings.ENABLED = config["angle_label"]["enabled"]
    AngleLabelSettings.DISPLAY_THRESHOLD = config["angle_label"]["display_threshold"]
    AngleLabelSettings.WHITE = config["angle_label"]["white"]

    Colors.HIGH_CHANCE = config["colors"]["high_chance"]
    Colors.MEDIUM_CHANCE = config["colors"]["medium_chance"]
    Colors.LOW_CHANCE = config["colors"]["low_chance"]
    Colors.RICOCHET = config["colors"]["ricochet"]

    Colorblind.ENABLED = config["colorblind"]["enabled"]
    Colorblind.HIGH_CHANCE = config["colorblind"]["high_chance"]
    Colorblind.MEDIUM_CHANCE = config["colorblind"]["medium_chance"]
    Colorblind.LOW_CHANCE = config["colorblind"]["low_chance"]
    Colorblind.RICOCHET = config["colorblind"]["ricochet"]


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


def get_low_chance_color():
    if not Colorblind.ENABLED:
        return Colors.LOW_CHANCE
    else:
        return Colorblind.LOW_CHANCE


class Colors(object):
    HIGH_CHANCE = safe_get_setting(label="colors", attribute="high_chance")
    MEDIUM_CHANCE = safe_get_setting(label="colors", attribute="medium_chance")
    LOW_CHANCE = safe_get_setting(label="colors", attribute="low_chance")
    RICOCHET = safe_get_setting(label="colors", attribute="ricochet")

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
    ENABLED = safe_get_setting("colorblind", "enabled")
    HIGH_CHANCE = safe_get_setting("colorblind", "high_chance")
    MEDIUM_CHANCE = safe_get_setting("colorblind", "medium_chance")
    LOW_CHANCE = safe_get_setting("colorblind", "low_chance")
    RICOCHET = safe_get_setting("colorblind", "ricochet")

    @classmethod
    def get_color_from_prob(cls, prob):
        if prob <= 7:
            return cls.LOW_CHANCE
        elif prob >= 93:
            return cls.HIGH_CHANCE
        else:
            return cls.MEDIUM_CHANCE


class ArmorLabelSettings:
    ENABLED = safe_get_setting("armor_label", "enabled")
    FORMAT = "{value}"


class ProbLabelSettings:
    ENABLED = safe_get_setting("prob_label", "enabled")
    FORMAT = "{value}%"


class AngleLabelSettings:
    ENABLED = safe_get_setting("angle_label", "enabled")
    FORMAT = "{value}°"
    DISPLAY_THRESHOLD = safe_get_setting("angle_label", "display_threshold")
    WHITE = safe_get_setting("angle_label", "white")
