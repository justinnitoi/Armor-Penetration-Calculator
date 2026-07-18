from gui.modsSettingsApi import g_modsSettingsApi, templates  # type: ignore

from pade_constants import (
    ArmorLabelSettings,
    PenLabelSettings,
    AngleLabelSettings,
    EffPenLabelSettings,
    KillLabelSettings,
    GunLabelSettings,
    Colors,
    ShadowSettings,
)
from pade_config import save_flat_config
from pade_gui import gui_state

mod_linkage = "pade_armor_calculator"
modDataVersion = 1

template = {
    "modDisplayName": "pademinune's Armor Penetration Calculator",
    "enabled": True,
    "column1": [
        templates.createLabel("<b>— Armor Label —</b>"),
        templates.createCheckbox(
            "Enable Armor Label",
            "armor_label_enabled",
            ArmorLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Armor Label{/HEADER}{BODY}Show or hide the effective armor value label.{/BODY}",
        ),
        templates.createSlider(
            "Armor Label Font Size",
            "armor_label_font_size",
            ArmorLabelSettings.FONT_SIZE,
            5,
            100,
            1,
            format="{{value}}px",
            tooltip="{HEADER}Armor Label Font Size{/HEADER}{BODY}The size in pixels of the Armor Label.{/BODY}",
        ),
        templates.createNumericStepper(
            "Armor Label Horizontal Offset",
            "armor_label_x_offset",
            ArmorLabelSettings.X_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Armor Label Horizontal Offset{/HEADER}{BODY}The armor label's horizontal offset from the center of the screen. Positive values move it to the right.{/BODY}",
        ),
        templates.createNumericStepper(
            "Armor Label Vertical Offset",
            "armor_label_y_offset",
            ArmorLabelSettings.Y_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Armor Label Vertical Offset{/HEADER}{BODY}The armor label's vertical offset from the center of the screen. Positive values move it down.{/BODY}",
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
        templates.createSlider(
            "Pen Label Font Size",
            "pen_label_font_size",
            PenLabelSettings.FONT_SIZE,
            5,
            100,
            1,
            format="{{value}}px",
            tooltip="{HEADER}Probability Label Font Size{/HEADER}{BODY}The size in pixels of the Penetration Label.{/BODY}",
        ),
        templates.createNumericStepper(
            "Pen Label Horizontal Offset",
            "pen_label_x_offset",
            PenLabelSettings.X_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Probability Label Horizontal Offset{/HEADER}{BODY}The probability label's horizontal offset from the center of the screen. Positive values move it to the right.{/BODY}",
        ),
        templates.createNumericStepper(
            "Pen Label Vertical Offset",
            "pen_label_y_offset",
            PenLabelSettings.Y_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Probability Label Vertical Offset{/HEADER}{BODY}The probability label's vertical offset from the center of the screen. Positive values move it down.{/BODY}",
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
        templates.createSlider(
            "Angle Label Font Size",
            "angle_label_font_size",
            AngleLabelSettings.FONT_SIZE,
            5,
            100,
            1,
            format="{{value}}px",
            tooltip="{HEADER}Angle Label Font Size{/HEADER}{BODY}The size in pixels of the Angle Label.{/BODY}",
        ),
        templates.createNumericStepper(
            "Angle Label Horizontal Offset",
            "angle_label_x_offset",
            AngleLabelSettings.X_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Angle Label Horizontal Offset{/HEADER}{BODY}The angle label's horizontal offset from the center of the screen. Positive values move it to the right.{/BODY}",
        ),
        templates.createNumericStepper(
            "Angle Label Vertical Offset",
            "angle_label_y_offset",
            AngleLabelSettings.Y_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Angle Label Vertical Offset{/HEADER}{BODY}The angle label's vertical offset from the center of the screen. Positive values move it down.{/BODY}",
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
        templates.createLabel("<b>— Effective Penetration Label —</b>"),
        templates.createCheckbox(
            "Enable Effective Pen Label",
            "eff_pen_label_enabled",
            EffPenLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Effective Pen Label{/HEADER}{BODY}Show or hide the shell's effective penetration label.{/BODY}",
        ),
        templates.createSlider(
            "Eff Pen Label Font Size",
            "eff_pen_label_font_size",
            EffPenLabelSettings.FONT_SIZE,
            5,
            100,
            1,
            format="{{value}}px",
            tooltip="{HEADER}Effective Pen Label Font Size{/HEADER}{BODY}The size in pixels of the Effective Penetration Label.{/BODY}",
        ),
        templates.createNumericStepper(
            "Eff Pen Label Horizontal Offset",
            "eff_pen_label_x_offset",
            EffPenLabelSettings.X_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Effective Pen Label Horizontal Offset{/HEADER}{BODY}The effective pen label's horizontal offset from the center of the screen. Positive values move it to the right.{/BODY}",
        ),
        templates.createNumericStepper(
            "Eff Pen Label Vertical Offset",
            "eff_pen_label_y_offset",
            EffPenLabelSettings.Y_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Effective Pen Label Vertical Offset{/HEADER}{BODY}The effective pen label's vertical offset from the center of the screen. Positive values move it down.{/BODY}",
        ),
        templates.createInput(
            "Eff Pen Label Format",
            "eff_pen_label_format",
            EffPenLabelSettings.LABEL_FORMAT,
            tooltip="{HEADER}Effective Pen Label Format{/HEADER}{BODY}The display format of the effective pen label. '{eff_pen}' will be replaced with the shell's effective penetration.{/BODY}",
        ),
    ],
    "column2": [
        templates.createLabel("<b>— Kill Label —</b>"),
        templates.createCheckbox(
            "Enable Kill Label",
            "kill_label_enabled",
            KillLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Kill Label{/HEADER}{BODY}Show or hide the estimated kill chance label.{/BODY}",
        ),
        templates.createSlider(
            "Kill Label Font Size",
            "kill_label_font_size",
            KillLabelSettings.FONT_SIZE,
            5,
            100,
            1,
            format="{{value}}px",
            tooltip="{HEADER}Kill Label Font Size{/HEADER}{BODY}The size in pixels of the Kill Label.{/BODY}",
        ),
        templates.createNumericStepper(
            "Kill Label Horizontal Offset",
            "kill_label_x_offset",
            KillLabelSettings.X_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Kill Label Horizontal Offset{/HEADER}{BODY}The kill label's horizontal offset from the center of the screen. Positive values move it to the right.{/BODY}",
        ),
        templates.createNumericStepper(
            "Kill Label Vertical Offset",
            "kill_label_y_offset",
            KillLabelSettings.Y_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Kill Label Vertical Offset{/HEADER}{BODY}The kill label's vertical offset from the center of the screen. Positive values move it down.{/BODY}",
        ),
        templates.createInput(
            "Kill Label Format",
            "kill_label_format",
            KillLabelSettings.LABEL_FORMAT,
            tooltip="{HEADER}Kill Label Format{/HEADER}{BODY}The display format of the kill label. '{value}' will be replaced with the estimated kill chance.{/BODY}",
        ),
        templates.createEmpty(10),
        templates.createLabel("<b>— Gun Label —</b>"),
        templates.createCheckbox(
            "Enable Gun Label",
            "gun_label_enabled",
            GunLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Gun Label{/HEADER}{BODY}Show or hide the marker indicating the shot would hit the target's gun.{/BODY}",
        ),
        templates.createSlider(
            "Gun Label Font Size",
            "gun_label_font_size",
            GunLabelSettings.FONT_SIZE,
            5,
            100,
            1,
            format="{{value}}px",
            tooltip="{HEADER}Gun Label Font Size{/HEADER}{BODY}The size in pixels of the Gun Label.{/BODY}",
        ),
        templates.createNumericStepper(
            "Gun Label Horizontal Offset",
            "gun_label_x_offset",
            GunLabelSettings.X_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Gun Label Horizontal Offset{/HEADER}{BODY}The gun label's horizontal offset from the center of the screen. Positive values move it to the right.{/BODY}",
        ),
        templates.createNumericStepper(
            "Gun Label Vertical Offset",
            "gun_label_y_offset",
            GunLabelSettings.Y_OFFSET,
            -2000,
            2000,
            1,
            manual=True,
            tooltip="{HEADER}Gun Label Vertical Offset{/HEADER}{BODY}The gun label's vertical offset from the center of the screen. Positive values move it down.{/BODY}",
        ),
        templates.createInput(
            "Gun Label Format",
            "gun_label_format",
            GunLabelSettings.LABEL_FORMAT,
            tooltip="{HEADER}Gun Label Format{/HEADER}{BODY}The marker shown when the shot would hit the target's gun.{/BODY}",
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
        templates.createEmpty(10),
        templates.createLabel("<b>— Shadow —</b>"),
        templates.createColorChoice(
            "Shadow Color",
            "shadow_color",
            ShadowSettings.COLOR,
            tooltip="{HEADER}Shadow Color{/HEADER}{BODY}The color of the text shadow/glow.{/BODY}",
        ),
        templates.createSlider(
            "Shadow Opacity",
            "shadow_alpha",
            ShadowSettings.ALPHA,
            0,
            10,
            1,
            format="{{value}}",
            tooltip="{HEADER}Shadow Opacity{/HEADER}{BODY}The opacity of the text shadow. 0 = transparent, 10 = fully opaque.{/BODY}",
        ),
        templates.createSlider(
            "Shadow Length",
            "shadow_length",
            ShadowSettings.LENGTH,
            0,
            10,
            1,
            format="{{value}}",
            tooltip="{HEADER}Shadow Length{/HEADER}{BODY}The blur radius of the text shadow.{/BODY}",
        ),
        templates.createSlider(
            "Shadow Strength",
            "shadow_strength",
            ShadowSettings.STRENGTH,
            0,
            10,
            1,
            format="{{value}}",
            tooltip="{HEADER}Shadow Strength{/HEADER}{BODY}The sharpness of the text shadow. Higher = sharper outline.{/BODY}",
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
