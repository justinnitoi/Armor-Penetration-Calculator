# -*- coding: utf-8 -*-
from gui.modsSettingsApi import g_modsSettingsApi, templates  # type: ignore

from ap_calculator.gui.ap_config import save_config, update_global_settings
from ap_calculator.gui.ap_constants import (
    AngleLabelSettings,
    ArmorLabelSettings,
    Colorblind,
    Colors,
    ProbLabelSettings,
    update_constants,
)

from . import DISCORD_URL, DONATE_URL, MOD_LINKAGE, VERSION
from ap_calculator.settings_gui.language import tooltip, tr


def _colorSection():
    normal = [
        templates.createColorChoice(
            tr("colors.high_chance.title"),
            "colors.high_chance",
            Colors.HIGH_CHANCE,
            tooltip=tooltip(
                "colors.high_chance.tooltip_header", "colors.high_chance.tooltip_body"
            ),
        ),
        templates.createColorChoice(
            tr("colors.medium_chance.title"),
            "colors.medium_chance",
            Colors.MEDIUM_CHANCE,
            tooltip=tooltip(
                "colors.medium_chance.tooltip_header",
                "colors.medium_chance.tooltip_body",
            ),
        ),
        templates.createColorChoice(
            tr("colors.low_chance.title"),
            "colors.low_chance",
            Colors.LOW_CHANCE,
            tooltip=tooltip(
                "colors.low_chance.tooltip_header", "colors.low_chance.tooltip_body"
            ),
        ),
        templates.createColorChoice(
            tr("colors.ricochet.title"),
            "colors.ricochet",
            Colors.RICOCHET,
            tooltip=tooltip(
                "colors.ricochet.tooltip_header", "colors.ricochet.tooltip_body"
            ),
        ),
    ]
    colorblind = [
        templates.createColorChoice(
            tr("colors.high_chance.title"),
            "colorblind.high_chance",
            Colorblind.HIGH_CHANCE,
            tooltip=tooltip(
                "colors.high_chance.tooltip_header", "colors.high_chance.tooltip_body"
            ),
        ),
        templates.createColorChoice(
            tr("colors.medium_chance.title"),
            "colorblind.medium_chance",
            Colorblind.MEDIUM_CHANCE,
            tooltip=tooltip(
                "colors.medium_chance.tooltip_header",
                "colors.medium_chance.tooltip_body",
            ),
        ),
        templates.createColorChoice(
            tr("colors.low_chance.title"),
            "colorblind.low_chance",
            Colorblind.LOW_CHANCE,
            tooltip=tooltip(
                "colors.low_chance.tooltip_header", "colors.low_chance.tooltip_body"
            ),
        ),
        templates.createColorChoice(
            tr("colors.ricochet.title"),
            "colorblind.ricochet",
            Colorblind.RICOCHET,
            tooltip=tooltip(
                "colors.ricochet.tooltip_header", "colors.ricochet.tooltip_body"
            ),
        ),
    ]

    toggle = templates.createCheckbox(
        tr("colorblind.enabled.title"),
        "colorblind.enabled",
        Colorblind.ENABLED,
        tooltip=tooltip(
            "colorblind.enabled.tooltip_header", "colorblind.enabled.tooltip_body"
        ),
    )

    gradient = templates.createCheckbox(
        tr("colors.gradient.title"),
        "colors.gradient",
        Colors.GRADIENT,
        tooltip=(
            "{{HEADER}}{header}{{/HEADER}}".format(
                header=tr("colors.gradient.tooltip_header")
            )
            + "{{BODY}}{body}<br><br>".format(body=tr("colors.gradient.tooltip_body"))
            + "<img src='img://gui/AP_Calculator_2/tooltips/gradient-high.png' width='220' height='120'>"
            "<img src='img://gui/AP_Calculator_2/tooltips/gradient-medium.png' width='220' height='120'>"
            "<img src='img://gui/AP_Calculator_2/tooltips/gradient-low.png' width='220' height='120'>"
            "{/BODY}"
        ),
    )

    if hasattr(templates, "visibleWhen"):
        normal = [templates.visibleWhen(c, "colorblind.enabled", False) for c in normal]
        colorblind = [
            templates.visibleWhen(c, "colorblind.enabled", True) for c in colorblind
        ]
    # On older API builds without visibleWhen, both sets just show plainly
    # (no gating) — still functional, just not tidy. Acceptable fallback.

    return [toggle, gradient] + normal + colorblind


template = {
    "modDisplayName": "{title} {version}".format(title=tr("title"), version=VERSION),
    "enabled": True,
    "column1": [
        templates.createLabel("<b>— {} —</b>".format(tr("section.armor_label"))),
        templates.createCheckbox(
            tr("armor_label.title"),
            "armor_label.enabled",
            ArmorLabelSettings.ENABLED,
            tooltip=(
                "{{HEADER}}{header}{{/HEADER}}".format(
                    header=tr("armor_label.tooltip_header")
                )
                + "{{BODY}}{body}<br><br>".format(body=tr("armor_label.tooltip_body"))
                + "<img src='img://gui/AP_Calculator_2/tooltips/full-cropped.png' width='220' height='120'>"
                "<img src='img://gui/AP_Calculator_2/tooltips/no-armor-cropped.png' width='220' height='120'>"
                "{/BODY}"
            ),
        ),
        templates.createLabel("<b>— {} —</b>".format(tr("section.probability_label"))),
        templates.createCheckbox(
            tr("prob_label.title"),
            "prob_label.enabled",
            ProbLabelSettings.ENABLED,
            tooltip=(
                "{{HEADER}}{header}{{/HEADER}}".format(
                    header=tr("prob_label.tooltip_header")
                )
                + "{{BODY}}{body}<br><br>".format(body=tr("prob_label.tooltip_body"))
                + "<img src='img://gui/AP_Calculator_2/tooltips/full-cropped.png' width='220' height='120'>"
                "<img src='img://gui/AP_Calculator_2/tooltips/no-prob-cropped.png' width='220' height='120'>"
                "{/BODY}"
            ),
        ),
        templates.createLabel("<b>— {} —</b>".format(tr("section.angle_label"))),
        templates.createCheckbox(
            tr("angle_label.title"),
            "angle_label.enabled",
            AngleLabelSettings.ENABLED,
            tooltip=(
                "{{HEADER}}{header}{{/HEADER}}".format(
                    header=tr("angle_label.tooltip_header")
                )
                + "{{BODY}}{body}<br><br>".format(body=tr("angle_label.tooltip_body"))
                + "<img src='img://gui/AP_Calculator_2/tooltips/full-angle-cropped.png' width='220' height='120'>"
                "<img src='img://gui/AP_Calculator_2/tooltips/no-angle-cropped.png' width='220' height='120'>"
                "{/BODY}"
            ),
        ),
        templates.createNumericStepper(
            tr("angle_label.display_threshold.title"),
            "angle_label.display_threshold",
            AngleLabelSettings.DISPLAY_THRESHOLD,
            0,
            90,
            1,
            manual=True,
            tooltip=tooltip(
                "angle_label.display_threshold.tooltip_header",
                "angle_label.display_threshold.tooltip_body",
            ),
        ),
        templates.createCheckbox(
            tr("angle_label.always_white.title"),
            "angle_label.always_white",
            AngleLabelSettings.WHITE,
            tooltip=(
                "{{HEADER}}{header}{{/HEADER}}".format(
                    header=tr("angle_label.always_white.tooltip_header")
                )
                + "{{BODY}}{body}<br><br>".format(
                    body=tr("angle_label.always_white.tooltip_body")
                )
                + "<img src='img://gui/AP_Calculator_2/tooltips/full-angle-cropped.png' width='220' height='120'>"
                "<img src='img://gui/AP_Calculator_2/tooltips/angle-colored-cropped.png' width='220' height='120'>"
                "{/BODY}"
            ),
        ),
    ],
    "column2": [templates.createLabel("<b>— {} —</b>".format(tr("section.colors")))]
    + _colorSection()
    + [
        templates.createLabel("<b>— {} —</b>".format(tr("section.support"))),
        templates.createRadioButtonGroup(
            "",
            "discord_button",
            [""],
            0,
            button=templates.createButton(
                text=tr("discord_button.title"), width=90, height=25
            ),
            tooltip=tooltip(
                "discord_button.tooltip_header", "discord_button.tooltip_body"
            ),
        ),
        templates.createRadioButtonGroup(
            "",
            "donate_button",
            [""],
            0,
            button=templates.createButton(
                text=tr("donate_button.title"), width=90, height=25
            ),
            tooltip=tooltip(
                "donate_button.tooltip_header", "donate_button.tooltip_body"
            ),
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
        update_global_settings(new_settings)
        update_constants()
        save_config()


g_modsSettingsApi.setModTemplate(
    MOD_LINKAGE, template, on_settings_save, buttonHandler=onButtonClicked
)
