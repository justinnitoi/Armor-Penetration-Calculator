from gui.aslainMenu import g_modsSettingsApi, templates  # type: ignore

from APCalculator.APconstants import (
    ArmorLabelSettings,
    PenLabelSettings,
    AngleLabelSettings,
    Colors,
    Colorblind,
    VERSION,
    update_constants,
)
from APCalculator.APconfig import (
    nested,
    flattened,
    save_config,
    DEFAULT_CONFIG,
)

mod_linkage = "pade_armor_calculator_2"
DISCORD_URL = "https://discord.gg/PrzqyneRXv"
DONATE_URL = "https://ko-fi.com/pademinune"


def _colorSection():
    normal = [
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
    ]
    colorblind = [
        templates.createColorChoice(
            "High Pen Chance",
            "colorblind_high_chance",
            Colorblind.HIGH_CHANCE,
            tooltip="{HEADER}High Pen Chance Color{/HEADER}{BODY}Color shown when penetration probability is high (>93%).{/BODY}",
        ),
        templates.createColorChoice(
            "Medium Pen Chance",
            "colorblind_medium_chance",
            Colorblind.MEDIUM_CHANCE,
            tooltip="{HEADER}Medium Pen Chance Color{/HEADER}{BODY}Color shown when penetration probability is medium.{/BODY}",
        ),
        templates.createColorChoice(
            "Low Pen Chance",
            "colorblind_low_chance",
            Colorblind.LOW_CHANCE,
            tooltip="{HEADER}Low Pen Chance Color{/HEADER}{BODY}Color shown when penetration probability is low (<7%).{/BODY}",
        ),
        templates.createColorChoice(
            "Ricochet",
            "colorblind_ricochet",
            Colorblind.RICOCHET,
            tooltip="{HEADER}Ricochet Color{/HEADER}{BODY}Color shown when the shell will ricochet.{/BODY}",
        ),
    ]

    toggle = templates.createCheckbox(
        "Use colorblind colors",
        "colorblind_enabled",
        Colorblind.ENABLED,
        tooltip="{HEADER}Colorblind-friendly palette{/HEADER}{BODY}Swap to a colorblind-safe color scheme, editable below.{/BODY}",
    )

    if hasattr(templates, "visibleWhen"):
        normal = [templates.visibleWhen(c, "colorblind_enabled", False) for c in normal]
        colorblind = [
            templates.visibleWhen(c, "colorblind_enabled", True) for c in colorblind
        ]
    # On older API builds without visibleWhen, both sets just show plainly
    # (no gating) — still functional, just not tidy. Acceptable fallback.

    return [toggle] + normal + colorblind


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
            "prob_label_enabled",
            PenLabelSettings.ENABLED,
            tooltip="{HEADER}Enable Probability Label{/HEADER}{BODY}Show or hide the penetration probability label.{/BODY}",
        ),
        [
            templates.createInput(
                "Prob Label Format",
                "prob_label_format",
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
            templates.createCheckbox(
                "Angle Color is always White",
                "angle_label_white",
                AngleLabelSettings.WHITE,
                tooltip="{HEADER}Angle Color is always White{/HEADER}{BODY}Toggle between having the angle label color always be White, or to mimic the penetration chance color.{/BODY}",
            ),
        ],
    ),
    "column2": [templates.createLabel("<b>— Colors —</b>")]
    + _colorSection()
    + [
        templates.createLabel("<b>— Support —</b>"),
        templates.createRadioButtonGroup(
            "",
            "discord_button",
            [""],
            0,
            button=templates.createButton(text="Discord", width=90, height=25),
        ),
        templates.createRadioButtonGroup(
            "",
            "donate_button",
            [""],
            0,
            button=templates.createButton(text="Donate", width=90, height=25),
        ),
    ],
}


def onButtonClicked(linkage, varName, value):
    if linkage == mod_linkage and varName == "discord_button":
        import BigWorld  # type: ignore

        BigWorld.wg_openWebBrowser(DISCORD_URL)
    if linkage == mod_linkage and varName == "donate_button":
        import BigWorld  # type: ignore

        BigWorld.wg_openWebBrowser(DONATE_URL)


def on_settings_save(linkage, new_settings):
    if linkage == mod_linkage:
        nested_config = nested(new_settings)
        update_constants(nested_config)
        save_config(nested_config)


if hasattr(g_modsSettingsApi, "setModDefaults"):
    flattened_default = flattened(DEFAULT_CONFIG)
    g_modsSettingsApi.setModDefaults(mod_linkage, flattened_default)

g_modsSettingsApi.setModTemplate(
    mod_linkage, template, on_settings_save, buttonHandler=onButtonClicked
)
