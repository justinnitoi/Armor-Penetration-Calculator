from APCalculator.APconstants import (
    Colors,
    ArmorLabelSettings,
    PenLabelSettings,
    AngleLabelSettings,
)
from APCalculator.APBattleView import update_gameface


class GuiState(object):
    def __init__(self):
        self.armor_label = ArmorLabel(ArmorLabelSettings)
        self.prob_label = ProbLabel(PenLabelSettings)
        self.angle_label = AngleLabel(AngleLabelSettings)
        # self.eff_pen_label = Label(EFF_PEN_ALIAS, EffPenLabelSettings)
        # self.kill_label = Label(KILL_ALIAS, KillLabelSettings)
        # self.gun_label = GunLabel(GUN_ALIAS, GunLabelSettings)
        # self.track_label = TrackLabel(TrackLabelSettings)
        self.labels = [
            self.armor_label,
            self.prob_label,
            self.angle_label,
            # self.eff_pen_label,
            # self.kill_label,
            # self.gun_label,
            # self.track_label,
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
        angle,
        avg_pen,
        kill_prob,
    ):
        """Assumes all arguments passed are booleans or integers"""
        if ricochet:
            # shell ricochet
            color = Colors.RICOCHET
            if self.armor_label.settings.ENABLED:
                self.armor_label.update_gui("-", color)
            if self.prob_label.settings.ENABLED:
                self.prob_label.update_gui(0, color)
            if self.angle_label.settings.ENABLED:
                self.angle_label.update_gui(angle, color)
            # if self.eff_pen_label.settings.ENABLED:
            #     self.eff_pen_label.update_gui(avg_pen, color)
            # if self.kill_label.settings.ENABLED and self.kill_label.visible:
            #     self.kill_label.hide()
            # if self.gun_label.settings.ENABLED:
            #     self.gun_label.update_gui(hit_gun, color)
        elif not hit_body:
            # shell only hits spaced armor or tracks
            color = Colors.LOW_CHANCE
            self.hide_all()
        else:
            color = Colors.get_color_from_prob(prob)

            if self.armor_label.settings.ENABLED:
                self.armor_label.update_gui(armor_value, color)
            if self.prob_label.settings.ENABLED:
                self.prob_label.update_gui(prob, color)
            if self.angle_label.settings.ENABLED:
                self.angle_label.update_gui(angle, color)
            # if self.eff_pen_label.settings.ENABLED:
            #     self.eff_pen_label.update_gui(avg_pen, color)
            # if self.kill_label.settings.ENABLED:
            #     if kill_prob > 0:
            #         self.kill_label.update_gui(
            #             kill_prob, Colors.get_color_from_prob(kill_prob)
            #         )
            #     elif self.kill_label.visible:
            #         self.kill_label.hide()
            # if self.gun_label.settings.ENABLED:
            #     self.gun_label.update_gui(hit_gun, color)

        # if self.track_label.settings.ENABLED:
        #     if hit_track and (color == Colors.GREEN or color == Colors.ORANGE):
        #         self.track_label.update_gui(color)
        #     elif self.track_label.visible:
        #         self.track_label.hide()


class ArmorLabel(object):
    def __init__(self, settings):
        self.settings = settings
        self.visible = False
        self.last_state = None

    def hide(self):
        if self.visible:
            # send update to gameface to hide label
            update_gameface(armor_visible=False)
            self.visible = False
            self.last_state = None

    def update_gui(self, value, color):
        state = (value, color)
        if state == self.last_state and self.visible:
            return

        self.last_state = state
        self.visible = True
        interior_text = self.settings.FORMAT.format(value=value)
        # send update to gameface to update the label with interior_text and color
        update_gameface(armor_text=interior_text, armor_visible=True, armor_color=color)


class ProbLabel(object):
    def __init__(self, settings):
        self.settings = settings
        self.visible = False
        self.last_state = None

    def hide(self):
        if self.visible:
            # send update to gameface to hide label
            update_gameface(prob_visible=False)
            self.visible = False
            self.last_state = None

    def update_gui(self, value, color):
        state = (value, color)
        if state == self.last_state and self.visible:
            return

        self.last_state = state
        self.visible = True
        interior_text = self.settings.FORMAT.format(value=value)
        # send update to gameface to update the label with interior_text and color
        update_gameface(prob_text=interior_text, prob_visible=True, prob_color=color)


class AngleLabel(object):
    def __init__(self, settings):
        self.settings = settings
        self.visible = False
        self.last_state = None

    def hide(self):
        if self.visible:
            # send update to gameface to hide label
            update_gameface(angle_visible=False)
            self.visible = False
            self.last_state = None

    def update_gui(self, value, color):
        if value < self.settings.DISPLAY_THRESHOLD:
            self.hide()
            return

        color = Colors.WHITE
        state = (value, color)
        if state == self.last_state and self.visible:
            return

        self.last_state = state
        self.visible = True
        interior_text = self.settings.FORMAT.format(value=value)
        # send update to gameface to update the label with interior_text and color
        update_gameface(angle_text=interior_text, angle_visible=True, angle_color=color)


gui_state = GuiState()
