from pade_constants import Colors, ArmorLabel, PenLabel, AngleLabel, Shadow
import pade_track
from gambiter import g_guiFlash  # type: ignore
from gambiter.flash import COMPONENT_TYPE, COMPONENT_ALIGN  # type: ignore

ARMOR_ALIAS = "pademinune_ArmorPenLabel"
PROB_ALIAS = "pademinune_ProbabilityLabel"
ANGLE_ALIAS = "pademinune_AngleLabel"


class GuiState:
    armor_visible = False
    prob_visible = False
    angle_visible = False
    _last_armor_text = None  # type: str | None
    _last_prob_text = None  # type: str | None
    _last_angle_text = None  # type: str | None


def log(message):
    print("pademinune's Gui: " + str(message))


def update_armor_label(armor_value, color):
    interior_label = ArmorLabel.LABEL_FORMAT.format(armor=armor_value)
    new_text = "<font size='{font_size}' color='#{color}' face='$FieldFont'>{label_format}</font>".format(
        font_size=ArmorLabel.FONT_SIZE, color=color, label_format=interior_label
    )

    if new_text == GuiState._last_armor_text and GuiState.armor_visible:
        return

    GuiState._last_armor_text = new_text
    GuiState.armor_visible = True
    g_guiFlash.updateComponent(ARMOR_ALIAS, {"text": new_text, "visible": True})


def update_prob_label(prob, color):
    interior_label = PenLabel.LABEL_FORMAT.format(prob=prob)
    new_text = "<font size='{font_size}' color='#{color}' face='$FieldFont'>{label_format}</font>".format(
        font_size=PenLabel.FONT_SIZE, color=color, label_format=interior_label
    )

    if new_text == GuiState._last_prob_text and GuiState.prob_visible:
        return

    GuiState._last_prob_text = new_text
    GuiState.prob_visible = True
    g_guiFlash.updateComponent(PROB_ALIAS, {"text": new_text, "visible": True})


def update_angle_label(angle, color):
    # only show if angle >= 60 deg
    if angle < AngleLabel.DISPLAY_THRESHOLD and GuiState.angle_visible:
        hide_angle_label()
        return
    elif angle < AngleLabel.DISPLAY_THRESHOLD and not GuiState.angle_visible:
        # already not visible
        return
    

    interior_label = AngleLabel.LABEL_FORMAT.format(angle=angle)
    new_text = "<font size='{font_size}' color='#{color}' face='$FieldFont'>{label_format}</font>".format(
        font_size=AngleLabel.FONT_SIZE, color=color, label_format=interior_label
    )

    if new_text == GuiState._last_angle_text and GuiState.angle_visible:
        return

    GuiState._last_angle_text = new_text
    GuiState.angle_visible = True
    g_guiFlash.updateComponent(ANGLE_ALIAS, {"text": new_text, "visible": True})


def hide_armor_label():
    g_guiFlash.updateComponent(ARMOR_ALIAS, {"visible": False})
    GuiState._last_armor_text = None
    GuiState.armor_visible = False

def hide_prob_label():
    g_guiFlash.updateComponent(PROB_ALIAS, {"visible": False})
    GuiState._last_prob_text = None
    GuiState.prob_visible = False

def hide_angle_label():
    g_guiFlash.updateComponent(ANGLE_ALIAS, {"visible": False})
    GuiState._last_angle_text = None
    GuiState.angle_visible = False

def hide_labels():
    if GuiState.armor_visible:
        hide_armor_label()
    if GuiState.prob_visible:
        hide_prob_label()
    if GuiState.angle_visible:
        hide_angle_label()
    if pade_track.TrackState.track_visible:
        pade_track.hide_track_label()


def update_gui(armor_value, prob, ricochet, hit_body, hit_track, hit_angle):

    if ricochet:
        # shell ricochet
        color = Colors.PURPLE
        if ArmorLabel.ENABLED:
            update_armor_label("-", color)
        if PenLabel.ENABLED:
            update_prob_label(0, color)
        if AngleLabel.ENABLED:
            update_angle_label(hit_angle, color)
    elif not hit_body:
        # shell only hits spaced armor or tracks
        color = Colors.RED
        hide_labels()
    else:
        color = Colors.GREY
        if prob <= 7:
            # armor_val is right of z = 1.5
            color = Colors.RED
        elif prob >= 93:
            # armor_val is left of z = -1.5
            color = Colors.GREEN
        else:
            color = Colors.ORANGE

        if ArmorLabel.ENABLED:
            update_armor_label(int(armor_value), color)
        if PenLabel.ENABLED:
            update_prob_label(int(prob), color)
        if AngleLabel.ENABLED:
            update_angle_label(hit_angle, color)
    
    if (
        hit_track
        and (color == Colors.GREEN or color == Colors.ORANGE)
    ):
        pade_track.update_track_label(color)
    elif pade_track.TrackState.track_visible:
        pade_track.hide_track_label()



log("Starting creation of armor and penetration gui components")


def _build_glowfilter():
    return {
        "color": int(Shadow.COLOR, 16),
        "alpha": Shadow.ALPHA / 10.0,
        "blurX": Shadow.LENGTH,
        "blurY": Shadow.LENGTH,
        "strength": Shadow.STRENGTH,
        "quality": 2,
    }


armor_label_properties = {
    "isHtml": True,
    "text": "",
    "glowfilter": _build_glowfilter(),
    "alignX": COMPONENT_ALIGN.CENTER,
    "alignY": COMPONENT_ALIGN.CENTER,
    "x": ArmorLabel.X_OFFSET,
    "y": ArmorLabel.Y_OFFSET,
    "visible": False,
}

probability_label_properties = {
    "isHtml": True,
    "text": "",
    "glowfilter": _build_glowfilter(),
    "alignX": COMPONENT_ALIGN.CENTER,
    "alignY": COMPONENT_ALIGN.CENTER,
    "x": PenLabel.X_OFFSET,
    "y": PenLabel.Y_OFFSET,
    "visible": False,
}

angle_label_properties = {
    "isHtml": True,
    "text": "",
    "glowfilter": _build_glowfilter(),
    "alignX": COMPONENT_ALIGN.CENTER,
    "alignY": COMPONENT_ALIGN.CENTER,
    "x": AngleLabel.X_OFFSET,
    "y": AngleLabel.Y_OFFSET,
    "visible": False,
}

# create the armor value label
g_guiFlash.createComponent(ARMOR_ALIAS, COMPONENT_TYPE.LABEL, armor_label_properties)
# create the probability label
g_guiFlash.createComponent(
    PROB_ALIAS, COMPONENT_TYPE.LABEL, probability_label_properties
)
# create the angle label
g_guiFlash.createComponent(ANGLE_ALIAS, COMPONENT_TYPE.LABEL, angle_label_properties)


def update_label_properties():
    glowfilter = _build_glowfilter()

    armor_props = {
        "x": ArmorLabel.X_OFFSET,
        "y": ArmorLabel.Y_OFFSET,
        "glowfilter": glowfilter,
    }
    if not ArmorLabel.ENABLED:
        armor_props["visible"] = False
        GuiState._last_armor_text = None
        GuiState.armor_visible = False
    g_guiFlash.updateComponent(ARMOR_ALIAS, armor_props)

    pen_props = {
        "x": PenLabel.X_OFFSET,
        "y": PenLabel.Y_OFFSET,
        "glowfilter": glowfilter,
    }
    if not PenLabel.ENABLED:
        pen_props["visible"] = False
        GuiState._last_prob_text = None
        GuiState.prob_visible = False
    g_guiFlash.updateComponent(PROB_ALIAS, pen_props)

    angle_props = {
        "x": AngleLabel.X_OFFSET,
        "y": AngleLabel.Y_OFFSET,
        "glowfilter": glowfilter,
    }
    if not AngleLabel.ENABLED:
        angle_props["visible"] = False
        GuiState._last_angle_text = None
        GuiState.angle_visible = False
    g_guiFlash.updateComponent(ANGLE_ALIAS, angle_props)


log("GUI components have been created!")
