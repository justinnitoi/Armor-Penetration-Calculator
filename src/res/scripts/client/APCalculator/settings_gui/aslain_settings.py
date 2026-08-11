from gui.aslainMenu import g_modsSettingsApi, templates  # type: ignore

from APCalculator.APconstants import (
    ArmorLabelSettings,
    PenLabelSettings,
    AngleLabelSettings,
    Colors,
    VERSION,
    update_constants,
)
from APCalculator.APconfig import (
    nested,
    flattened,
    save_config,
    DEFAULT_CONFIG,
)

mod_linkage = "pade_armor_calculator"

template = {
    "modDisplayName": "pademinune's Armor Penetration Calculator 2",
    "enabled": True,
    "column1": [templates.createLabel("<b>— Armor Label —</b>")]
    + templates.createControlsGroup(
        templates.createCheckbox(
            "Enable Armor Label",
            "armor_label_enabled",
            ArmorLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Armor Label{/HEADER}{BODY}Show or hide the effective armor value label.{/BODY}",
        ),
        [
            templates.createInput(
                "Armor Label Format",
                "armor_label_format",
                ArmorLabelSettings.FORMAT,
                tooltip="{HEADER}Armor Label Format{/HEADER}{BODY}The display format of the armor label. '{armor}' will be replaced with the armor value.{/BODY}",
            ),
        ],
    )
    + [templates.createLabel("<b>— Probability Label —</b>")]
    + templates.createControlsGroup(
        templates.createCheckbox(
            "Enable Probability Label",
            "pen_label_enabled",
            PenLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Probability Label{/HEADER}{BODY}Show or hide the penetration probability label.{/BODY}",
        ),
        [
            templates.createInput(
                "Pen Label Format",
                "pen_label_format",
                PenLabelSettings.FORMAT,
                tooltip="{HEADER}Probability Label Format{/HEADER}{BODY}The display format of the probability label. '{prob}' will be replaced with the penetration probability.{/BODY}",
            ),
        ],
    )
    + [templates.createLabel("<b>— Angle Label —</b>")]
    + templates.createControlsGroup(
        templates.createCheckbox(
            "Enable Angle Label",
            "angle_label_enabled",
            AngleLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Angle Label{/HEADER}{BODY}Show or hide the impact angle label.{/BODY}",
        ),
        [
            templates.createInput(
                "Angle Label Format",
                "angle_label_format",
                AngleLabelSettings.FORMAT,
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
        ],
    ),
    "column2": [
        templates.createLabel("<b>— Colors —</b>"),
        templates.createColorChoice(
            "High Pen Chance",
            "colors_high_chance",
            Colors.HIGH_CHANCE,
            tooltip="{HEADER}High Pen Chance Color{/HEADER}{BODY}Color shown when penetration probability is high (>93%).{/BODY}",
        ),
        templates.createColorChoice(
            "Medium Pen Chance",
            "colors_medium_chance",
            Colors.MEDIUM_CHANCE,
            tooltip="{HEADER}Medium Pen Chance Color{/HEADER}{BODY}Color shown when penetration probability is medium.{/BODY}",
        ),
        templates.createColorChoice(
            "Low Pen Chance",
            "colors_low_chance",
            Colors.LOW_CHANCE,
            tooltip="{HEADER}Low Pen Chance Color{/HEADER}{BODY}Color shown when penetration probability is low (<7%).{/BODY}",
        ),
        templates.createColorChoice(
            "Ricochet",
            "colors_ricochet",
            Colors.RICOCHET,
            tooltip="{HEADER}Ricochet Color{/HEADER}{BODY}Color shown when the shell will ricochet.{/BODY}",
        ),
    ],
}


def on_settings_save(linkage, new_settings):
    if linkage == mod_linkage:
        nested_config = nested(new_settings)
        update_constants(nested_config)
        save_config(nested_config)


if hasattr(g_modsSettingsApi, "setModDefaults"):
    flattened_default = flattened(DEFAULT_CONFIG)
    g_modsSettingsApi.setModDefaults(mod_linkage, flattened_default)

g_modsSettingsApi.setModTemplate(mod_linkage, template, on_settings_save, None)
