from ap_calculator.ap_constants import (
    AngleLabelSettings,
    ArmorLabelSettings,
    Colors,
    ProbLabelSettings,
    TrackIndicatorSettings,
    get_color_from_prob,
    get_missed_body_color,
    get_ricochet_color,
)
from ap_calculator.ap_gameface_api import close_window, open_window, update_gameface


class GuiState(object):
    def __init__(self):
        self.enabled = False
        self.armor_label = ArmorLabel(ArmorLabelSettings)
        self.prob_label = ProbLabel(ProbLabelSettings)
        self.angle_label = AngleLabel(AngleLabelSettings)
        self.track_indicator = TrackIndicator()
        self.labels = [
            self.armor_label,
            self.prob_label,
            self.angle_label,
        ]

    def is_visible(self):
        for label in self.labels:
            if label.visible:
                return True
        return self.track_indicator.visible

    def hide_labels(self):
        for label in self.labels:
            if label.visible:
                label.hide()

    def hide_all(self):
        self.hide_labels()
        self.track_indicator.hide()

    def destroy_window(self):
        """Clears cache, stops cache updates, and destroys the gameface window."""
        self.hide_all()
        self.enabled = False
        close_window()

    def create_window(self):
        """Creates a new gameface window and resumes cache updates"""
        open_window()
        self.enabled = True

    def update_gui(
        self,
        armor_value,
        prob,
        ricochet,
        hit_body,
        angle,
        hit_track,
    ):
        """Assumes all arguments passed are booleans or integers"""
        if not self.enabled:
            # Don't make any updates to gui or cache
            return

        if ricochet:
            # shell ricochet
            color = get_ricochet_color()
            if self.armor_label.settings.ENABLED:
                self.armor_label.update_gui("-", color)
            if self.prob_label.settings.ENABLED:
                self.prob_label.update_gui(0, color)
            if self.angle_label.settings.ENABLED:
                self.angle_label.update_gui(angle, color)
        elif not hit_body:
            # shell only hits spaced armor or tracks
            color = get_missed_body_color()
            self.hide_labels()
        else:
            color = get_color_from_prob(prob)
            if self.armor_label.settings.ENABLED:
                self.armor_label.update_gui(armor_value, color)
            if self.prob_label.settings.ENABLED:
                self.prob_label.update_gui(prob, color)
            if self.angle_label.settings.ENABLED:
                self.angle_label.update_gui(angle, color)

        if TrackIndicatorSettings.ENABLED:
            if hit_track and color == Colors.HIGH_CHANCE:
                # hit track and green pen chance
                self.track_indicator.show()
            else:
                self.track_indicator.hide()


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

        if self.settings.WHITE:
            color = Colors.WHITE

        state = (value, color)
        if state == self.last_state and self.visible:
            return

        self.last_state = state
        self.visible = True
        interior_text = self.settings.FORMAT.format(value=value)
        # send update to gameface to update the label with interior_text and color
        update_gameface(angle_text=interior_text, angle_visible=True, angle_color=color)


class TrackIndicator(object):
    def __init__(self):
        self.visible = False

    def show(self):
        if not self.visible:
            self.visible = True
            update_gameface(track_visible=True)

    def hide(self):
        if self.visible:
            self.visible = False
            update_gameface(track_visible=False)


gui_state = GuiState()
