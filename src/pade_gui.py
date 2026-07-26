from pade_constants import (
    Colors,
    ArmorLabelSettings,
    PenLabelSettings,
    AngleLabelSettings,
    EffPenLabelSettings,
    KillLabelSettings,
    ShadowSettings,
    GunLabelSettings,
    TrackLabelSettings,
)
from gambiter import g_guiFlash  # type: ignore
from gambiter.flash import COMPONENT_TYPE, COMPONENT_ALIGN  # type: ignore


def log(message):
    print("pademinune's Gui: " + str(message))


ARMOR_ALIAS = "pademinune_ArmorLabel"
PEN_ALIAS = "pademinune_PenLabel"
ANGLE_ALIAS = "pademinune_AngleLabel"
EFF_PEN_ALIAS = "pademinune_EffPenLabel"
KILL_ALIAS = "pademinune_KillLabel"
GUN_ALIAS = "pademinune_GunLabel"


class GuiState(object):
    def __init__(self):
        self.armor_label = Label(ARMOR_ALIAS, ArmorLabelSettings)
        self.pen_label = Label(PEN_ALIAS, PenLabelSettings)
        self.angle_label = AngleLabel(ANGLE_ALIAS, AngleLabelSettings)
        self.eff_pen_label = Label(EFF_PEN_ALIAS, EffPenLabelSettings)
        self.kill_label = Label(KILL_ALIAS, KillLabelSettings)
        self.gun_label = GunLabel(GUN_ALIAS, GunLabelSettings)
        self.track_label = TrackLabel(TrackLabelSettings)
        self.labels = [
            self.armor_label,
            self.pen_label,
            self.angle_label,
            self.eff_pen_label,
            self.kill_label,
            self.gun_label,
            self.track_label,
        ]

    def is_visible(self):
        for label in self.labels:
            if label.visible:
                return True
        return False

    def hide_all(self):
        for label in self.labels:
            if label.visible:
                label.hide()

    def update_gui(
        self,
        armor_value,
        prob,
        ricochet,
        hit_body,
        hit_track,
        hit_gun,
        hit_angle,
        avg_pen,
        kill_prob,
    ):
        if ricochet:
            # shell ricochet
            color = Colors.PURPLE
            if self.armor_label.settings.ENABLED:
                self.armor_label.update_gui("-", color)
            if self.pen_label.settings.ENABLED:
                self.pen_label.update_gui(0, color)
            if self.angle_label.settings.ENABLED:
                self.angle_label.update_gui(hit_angle, color)
            if self.eff_pen_label.settings.ENABLED:
                self.eff_pen_label.update_gui(int(avg_pen), color)
            if self.kill_label.settings.ENABLED and self.kill_label.visible:
                self.kill_label.hide()
            if self.gun_label.settings.ENABLED:
                self.gun_label.update_gui(hit_gun, color)
        elif not hit_body:
            # shell only hits spaced armor or tracks
            color = Colors.RED
            self.hide_all()
        else:
            color = Colors.get_color_from_prob(prob)

            if self.armor_label.settings.ENABLED:
                self.armor_label.update_gui(int(armor_value), color)
            if self.pen_label.settings.ENABLED:
                self.pen_label.update_gui(int(prob), color)
            if self.angle_label.settings.ENABLED:
                self.angle_label.update_gui(hit_angle, color)
            if self.eff_pen_label.settings.ENABLED:
                self.eff_pen_label.update_gui(int(avg_pen), color)
            if self.kill_label.settings.ENABLED:
                if kill_prob > 0:
                    self.kill_label.update_gui(
                        kill_prob, Colors.get_color_from_prob(kill_prob)
                    )
                elif self.kill_label.visible:
                    self.kill_label.hide()
            if self.gun_label.settings.ENABLED:
                self.gun_label.update_gui(hit_gun, color)

        if self.track_label.settings.ENABLED:
            if hit_track and (color == Colors.GREEN or color == Colors.ORANGE):
                self.track_label.update_gui(color)
            elif self.track_label.visible:
                self.track_label.hide()

    def update_properties(self):
        for label in self.labels:
            label.update_properties()


class Label(object):
    def __init__(self, alias, settings):
        self.alias = alias
        self.settings = settings
        self.visible = False
        self.last_text = None
        properties = {
            "isHtml": True,
            "text": "",
            "glowfilter": _build_glowfilter(),
            "alignX": COMPONENT_ALIGN.CENTER,
            "alignY": COMPONENT_ALIGN.CENTER,
            "x": settings.X_OFFSET,
            "y": settings.Y_OFFSET,
            "visible": False,
        }
        g_guiFlash.createComponent(alias, COMPONENT_TYPE.LABEL, properties)

    def hide(self):
        if self.visible:
            g_guiFlash.updateComponent(self.alias, {"visible": False})
            self.visible = False
            self.last_text = None

    def update_gui(self, value, color):
        if value is not None:
            interior_text = self.settings.LABEL_FORMAT.format(value=value)
        else:
            interior_text = self.settings.LABEL_FORMAT
        new_text = "<font size='{font_size}' color='#{color}' face='$FieldFont'>{interior_text}</font>".format(
            font_size=self.settings.FONT_SIZE, color=color, interior_text=interior_text
        )

        if new_text == self.last_text and self.visible:
            return

        self.last_text = new_text
        self.visible = True
        g_guiFlash.updateComponent(self.alias, {"text": new_text, "visible": True})

    def update_properties(self):
        new_properties = {
            "x": self.settings.X_OFFSET,
            "y": self.settings.Y_OFFSET,
            "glowfilter": _build_glowfilter(),
        }
        if not self.settings.ENABLED:
            self.hide()
        g_guiFlash.updateComponent(self.alias, new_properties)


class AngleLabel(Label):
    def __init__(self, alias, settings):
        super(AngleLabel, self).__init__(alias, settings)

    def update_gui(self, value, color):
        if value < self.settings.DISPLAY_THRESHOLD:
            self.hide()
            return
        super(AngleLabel, self).update_gui(value, color)


class GunLabel(Label):
    def __init__(self, alias, settings):
        super(GunLabel, self).__init__(alias, settings)

    def update_gui(self, hit_gun, color):
        if not hit_gun and self.visible:
            self.hide()
            return
        elif hit_gun:
            super(GunLabel, self).update_gui(None, color)


class ImageLabel(object):
    def __init__(self, settings):
        self.settings = settings
        self.visible = False
        self.current_state = None
        self.state_aliases = []
        for alias, image_path in settings.IMAGES:
            properties = {
                "image": image_path,
                "alpha": 1,
                "x": settings.X_OFFSET,
                "y": settings.Y_OFFSET,
                "alignX": COMPONENT_ALIGN.CENTER,
                "alignY": COMPONENT_ALIGN.CENTER,
                "visible": False,
            }
            self.state_aliases.append(alias)
            g_guiFlash.createComponent(alias, COMPONENT_TYPE.IMAGE, properties)

    def hide(self):
        if self.visible:
            current_alias = self.state_aliases[self.current_state]
            g_guiFlash.updateComponent(current_alias, {"visible": False})
            self.visible = False
            self.current_state = None

    def update_gui(self, next_state):
        if next_state == self.current_state and self.visible:
            return

        if self.visible:
            old_alias = self.state_aliases[self.current_state]
            g_guiFlash.updateComponent(old_alias, {"visible": False})
        next_alias = self.state_aliases[next_state]
        self.current_state = next_state
        self.visible = True
        g_guiFlash.updateComponent(next_alias, {"visible": True})

    def update_properties(self):
        pass


class TrackLabel(ImageLabel):
    def __init__(self, settings):
        super(TrackLabel, self).__init__(settings)

    def update_gui(self, color):
        if color == Colors.GREEN:
            next_state = 0
        elif color == Colors.ORANGE:
            next_state = 1
        else:
            raise ValueError("Next track state is not green or orange.")
        return super(TrackLabel, self).update_gui(next_state)


def _build_glowfilter():
    return {
        "color": int(ShadowSettings.COLOR, 16),
        "alpha": ShadowSettings.ALPHA / 10.0,
        "blurX": ShadowSettings.LENGTH,
        "blurY": ShadowSettings.LENGTH,
        "strength": ShadowSettings.STRENGTH,
        "quality": 2,
    }


log("Starting creation of armor and penetration gui components")


gui_state = GuiState()


log("GUI components have been created!")
