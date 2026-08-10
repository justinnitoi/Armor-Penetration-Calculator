from gui.modsSettingsApi import g_modsSettingsApi, templates  # type: ignore

from APCalculator.pade_constants import (
    ArmorLabelSettings,
    PenLabelSettings,
    AngleLabelSettings,
    EffPenLabelSettings,
    KillLabelSettings,
    GunLabelSettings,
    Colors,
    ShadowSettings,
    VERSION,
)
from APCalculator.pade_config import save_flat_config
from APCalculator.pade_gui import gui_state

mod_linkage = "pade_armor_calculator"
modDataVersion = 1

template = {
    "modDisplayName": "pademinune's Armor Penetration Calculator 2",
    "enabled": True,
    "column1": [
        templates.createLabel("<b>— Armor Label —</b>"),
        templates.createCheckbox(
            "Enable Armor Label",
            "armor_label_enabled",
            ArmorLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Armor Label{/HEADER}{BODY}Show or hide the effective armor value label.{/BODY}",
        ),
        templates.createInput(
            "Armor Label Format",
            "armor_label_format",
            ArmorLabelSettings.LABEL_FORMAT,
            tooltip="{HEADER}Armor Label Format{/HEADER}{BODY}The display format of the armor label. '{armor}' will be replaced with the armor value.{/BODY}",
        ),
        templates.createEmpty(10),
        templates.createLabel("<b>— Probability Label —</b>"),
        templates.createCheckbox(
            "Enable Probability Label",
            "pen_label_enabled",
            PenLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Probability Label{/HEADER}{BODY}Show or hide the penetration probability label.{/BODY}",
        ),
        templates.createInput(
            "Pen Label Format",
            "pen_label_format",
            PenLabelSettings.LABEL_FORMAT,
            tooltip="{HEADER}Probability Label Format{/HEADER}{BODY}The display format of the probability label. '{prob}' will be replaced with the penetration probability.{/BODY}",
        ),
        templates.createEmpty(10),
        templates.createLabel("<b>— Angle Label —</b>"),
        templates.createCheckbox(
            "Enable Angle Label",
            "angle_label_enabled",
            AngleLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Angle Label{/HEADER}{BODY}Show or hide the impact angle label.{/BODY}",
        ),
        templates.createInput(
            "Angle Label Format",
            "angle_label_format",
            AngleLabelSettings.LABEL_FORMAT,
            tooltip="{HEADER}Angle Label Format{/HEADER}{BODY}The display format of the angle label. '{angle}' will be replaced with the impact angle in degrees.{/BODY}",
        ),
        templates.createNumericStepper(
            "Angle Display Threshold",
            "angle_label_display_threshold",
            AngleLabelSettings.DISPLAY_THRESHOLD,
            0,
            90,
            1,
            manual=True,
            tooltip="{HEADER}Angle Display Threshold{/HEADER}{BODY}The minimum impact angle (in degrees) at which the angle label is shown. Set to 0 to always show it.{/BODY}",
        ),
        templates.createEmpty(10),
        templates.createLabel("<b>— Colors —</b>"),
        templates.createColorChoice(
            "High Pen Chance",
            "color_green",
            Colors.GREEN,
            tooltip="{HEADER}High Pen Chance Color{/HEADER}{BODY}Color shown when penetration probability is high (>93%).{/BODY}",
        ),
        templates.createColorChoice(
            "Medium Pen Chance",
            "color_orange",
            Colors.ORANGE,
            tooltip="{HEADER}Medium Pen Chance Color{/HEADER}{BODY}Color shown when penetration probability is medium.{/BODY}",
        ),
        templates.createColorChoice(
            "Low Pen Chance",
            "color_red",
            Colors.RED,
            tooltip="{HEADER}Low Pen Chance Color{/HEADER}{BODY}Color shown when penetration probability is low (<7%).{/BODY}",
        ),
        templates.createColorChoice(
            "Ricochet",
            "color_ricochet",
            Colors.PURPLE,
            tooltip="{HEADER}Ricochet Color{/HEADER}{BODY}Color shown when the shell will ricochet.{/BODY}",
        ),
    ],
}


def on_settings_save(linkage, new_settings):
    if linkage == mod_linkage:
        ArmorLabelSettings.ENABLED = new_settings["armor_label_enabled"]
        ArmorLabelSettings.FONT_SIZE = new_settings["armor_label_font_size"]
        ArmorLabelSettings.X_OFFSET = new_settings["armor_label_x_offset"]
        ArmorLabelSettings.Y_OFFSET = new_settings["armor_label_y_offset"]
        ArmorLabelSettings.LABEL_FORMAT = new_settings["armor_label_format"]
        PenLabelSettings.ENABLED = new_settings["pen_label_enabled"]
        PenLabelSettings.FONT_SIZE = new_settings["pen_label_font_size"]
        PenLabelSettings.X_OFFSET = new_settings["pen_label_x_offset"]
        PenLabelSettings.Y_OFFSET = new_settings["pen_label_y_offset"]
        PenLabelSettings.LABEL_FORMAT = new_settings["pen_label_format"]
        AngleLabelSettings.ENABLED = new_settings["angle_label_enabled"]
        AngleLabelSettings.FONT_SIZE = new_settings["angle_label_font_size"]
        AngleLabelSettings.X_OFFSET = new_settings["angle_label_x_offset"]
        AngleLabelSettings.Y_OFFSET = new_settings["angle_label_y_offset"]
        AngleLabelSettings.LABEL_FORMAT = new_settings["angle_label_format"]
        AngleLabelSettings.DISPLAY_THRESHOLD = new_settings[
            "angle_label_display_threshold"
        ]
        EffPenLabelSettings.ENABLED = new_settings["eff_pen_label_enabled"]
        EffPenLabelSettings.FONT_SIZE = new_settings["eff_pen_label_font_size"]
        EffPenLabelSettings.X_OFFSET = new_settings["eff_pen_label_x_offset"]
        EffPenLabelSettings.Y_OFFSET = new_settings["eff_pen_label_y_offset"]
        EffPenLabelSettings.LABEL_FORMAT = new_settings["eff_pen_label_format"]
        KillLabelSettings.ENABLED = new_settings["kill_label_enabled"]
        KillLabelSettings.FONT_SIZE = new_settings["kill_label_font_size"]
        KillLabelSettings.X_OFFSET = new_settings["kill_label_x_offset"]
        KillLabelSettings.Y_OFFSET = new_settings["kill_label_y_offset"]
        KillLabelSettings.LABEL_FORMAT = new_settings["kill_label_format"]
        GunLabelSettings.ENABLED = new_settings["gun_label_enabled"]
        GunLabelSettings.FONT_SIZE = new_settings["gun_label_font_size"]
        GunLabelSettings.X_OFFSET = new_settings["gun_label_x_offset"]
        GunLabelSettings.Y_OFFSET = new_settings["gun_label_y_offset"]
        GunLabelSettings.LABEL_FORMAT = new_settings["gun_label_format"]
        Colors.GREEN = new_settings["color_green"]
        Colors.ORANGE = new_settings["color_orange"]
        Colors.RED = new_settings["color_red"]
        Colors.PURPLE = new_settings["color_ricochet"]
        ShadowSettings.COLOR = new_settings["shadow_color"]
        ShadowSettings.ALPHA = new_settings["shadow_alpha"]
        ShadowSettings.LENGTH = new_settings["shadow_length"]
        ShadowSettings.STRENGTH = new_settings["shadow_strength"]

        save_flat_config(new_settings)
        gui_state.update_properties()


g_modsSettingsApi.setModTemplate(mod_linkage, template, on_settings_save, None)
