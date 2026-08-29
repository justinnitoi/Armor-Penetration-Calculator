from gui.aslainMenu import g_modsSettingsApi, templates  # type: ignore

from APCalculator.APconstants import (
    ArmorLabelSettings,
    ProbLabelSettings,
    AngleLabelSettings,
    Colors,
    Colorblind,
    update_constants,
)
from APCalculator.APconfig import (
    save_config,
    DEFAULT_CONFIG,
)
from . import DISCORD_URL, DONATE_URL, MOD_LINKAGE, VERSION


def _colorSection():
    normal = [
        templates.createColorChoice(
            "High Pen Chance",
            "colors.high_chance",
            Colors.HIGH_CHANCE,
            tooltip=(
                "{HEADER}High Pen Chance Color{/HEADER}"
                "{BODY}Color shown when penetration probability is high (>93%).{/BODY}"
            ),
        ),
        templates.createColorChoice(
            "Medium Pen Chance",
            "colors.medium_chance",
            Colors.MEDIUM_CHANCE,
            tooltip=(
                "{HEADER}Medium Pen Chance Color{/HEADER}"
                "{BODY}Color shown when penetration probability is medium.{/BODY}"
            ),
        ),
        templates.createColorChoice(
            "Low Pen Chance",
            "colors.low_chance",
            Colors.LOW_CHANCE,
            tooltip=(
                "{HEADER}Low Pen Chance Color{/HEADER}"
                "{BODY}Color shown when penetration probability is low (<7%).{/BODY}"
            ),
        ),
        templates.createColorChoice(
            "Ricochet",
            "colors.ricochet",
            Colors.RICOCHET,
            tooltip=(
                "{HEADER}Ricochet Color{/HEADER}"
                "{BODY}Color shown when the shell will ricochet.{/BODY}"
            ),
        ),
    ]
    colorblind = [
        templates.createColorChoice(
            "High Pen Chance",
            "colorblind.high_chance",
            Colorblind.HIGH_CHANCE,
            tooltip=(
                "{HEADER}High Pen Chance Color{/HEADER}"
                "{BODY}Color shown when penetration probability is high (>93%).{/BODY}"
            ),
        ),
        templates.createColorChoice(
            "Medium Pen Chance",
            "colorblind.medium_chance",
            Colorblind.MEDIUM_CHANCE,
            tooltip=(
                "{HEADER}Medium Pen Chance Color{/HEADER}"
                "{BODY}Color shown when penetration probability is medium.{/BODY}"
            ),
        ),
        templates.createColorChoice(
            "Low Pen Chance",
            "colorblind.low_chance",
            Colorblind.LOW_CHANCE,
            tooltip=(
                "{HEADER}Low Pen Chance Color{/HEADER}"
                "{BODY}Color shown when penetration probability is low (<7%).{/BODY}"
            ),
        ),
        templates.createColorChoice(
            "Ricochet",
            "colorblind.ricochet",
            Colorblind.RICOCHET,
            tooltip=(
                "{HEADER}Ricochet Color{/HEADER}"
                "{BODY}Color shown when the shell will ricochet.{/BODY}"
            ),
        ),
    ]

    toggle = templates.createCheckbox(
        "Use colorblind colors",
        "colorblind.enabled",
        Colorblind.ENABLED,
        tooltip=(
            "{HEADER}Colorblind-friendly palette{/HEADER}"
            "{BODY}Swap to a colorblind-safe color scheme, editable below.{/BODY}"
        ),
    )

    if hasattr(templates, "visibleWhen"):
        normal = [templates.visibleWhen(c, "colorblind.enabled", False) for c in normal]
        colorblind = [
            templates.visibleWhen(c, "colorblind.enabled", True) for c in colorblind
        ]
    # On older API builds without visibleWhen, both sets just show plainly
    # (no gating) — still functional, just not tidy. Acceptable fallback.

    return [toggle] + normal + colorblind


template = {
    "modDisplayName": "pademinune's Armor Penetration Calculator {}".format(VERSION),
    "enabled": True,
    "column1": [templates.createLabel("<b>— Labels —</b>")]
    + templates.createControlsGroup(
        templates.createCheckbox(
            "Enable Armor Label",
            "armor_label.enabled",
            ArmorLabelSettings.ENABLED,
            tooltip=(
                "{HEADER}Enable Armor Label{/HEADER}"
                "{BODY}Show or hide the effective armor value label.<br><br>"
                "<img src='img://gui/maps/icons/APCalculator2/full-cropped.png' width='220' height='120'>"
                "<img src='img://gui/maps/icons/APCalculator2/no-armor-cropped.png' width='220' height='120'>"
                "{/BODY}"
            ),
        ),
        [],
    )
    + templates.createControlsGroup(
        templates.createCheckbox(
            "Enable Probability Label",
            "prob_label.enabled",
            ProbLabelSettings.ENABLED,
            tooltip=(
                "{HEADER}Enable Probability Label{/HEADER}{BODY}Show or hide the penetration probability label.<br><br>"
                "<img src='img://gui/maps/icons/APCalculator2/full-cropped.png' width='220' height='120'>"
                "<img src='img://gui/maps/icons/APCalculator2/no-prob-cropped.png' width='220' height='120'>"
                "{/BODY}"
            ),
        ),
        [],
    )
    + templates.createControlsGroup(
        templates.createCheckbox(
            "Enable Angle Label",
            "angle_label.enabled",
            AngleLabelSettings.ENABLED,
            tooltip=(
                "{HEADER}Enable Angle Label{/HEADER}{BODY}Show or hide the impact angle label.<br><br>"
                "<img src='img://gui/maps/icons/APCalculator2/full-angle-cropped.png' width='220' height='120'>"
                "<img src='img://gui/maps/icons/APCalculator2/no-angle-cropped.png' width='220' height='120'>"
                "{/BODY}"
            ),
        ),
        [
            templates.createNumericStepper(
                "Angle Display Threshold",
                "angle_label.display_threshold",
                AngleLabelSettings.DISPLAY_THRESHOLD,
                0,
                90,
                1,
                manual=True,
                tooltip=(
                    "{HEADER}Angle Display Threshold{/HEADER}"
                    "{BODY}The minimum impact angle (in degrees) at which the angle label is shown."
                    " Set to 0 to always show it.{/BODY}"
                ),
            ),
            templates.createCheckbox(
                "Angle Color is always White",
                "angle_label.always_white",
                AngleLabelSettings.WHITE,
                tooltip=(
                    "{HEADER}Angle Color is always White{/HEADER}"
                    "{BODY}Toggle between having the angle label color always be White,"
                    " or to mimic the penetration chance color.<br><br>"
                    "<img src='img://gui/maps/icons/APCalculator2/full-angle-cropped.png' width='220' height='120'>"
                    "<img src='img://gui/maps/icons/APCalculator2/angle-colored-cropped.png' width='220' height='120'>"
                    "{/BODY}"
                ),
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
    if linkage == MOD_LINKAGE and varName == "discord_button":
        import BigWorld  # type: ignore

        BigWorld.wg_openWebBrowser(DISCORD_URL)
    if linkage == MOD_LINKAGE and varName == "donate_button":
        import BigWorld  # type: ignore

        BigWorld.wg_openWebBrowser(DONATE_URL)


def on_settings_save(linkage, new_settings):
    if linkage == MOD_LINKAGE:
        update_constants(new_settings)
        save_config(new_settings)



if hasattr(g_modsSettingsApi, "setModDefaults"):
    g_modsSettingsApi.setModDefaults(MOD_LINKAGE, DEFAULT_CONFIG)

g_modsSettingsApi.setModTemplate(
    MOD_LINKAGE, template, on_settings_save, buttonHandler=onButtonClicked
)
