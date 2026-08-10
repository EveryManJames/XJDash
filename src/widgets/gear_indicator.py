"""
GearIndicator - AW-4 gear selector display with current gear highlight.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.app import App

from widgets.base_widget import DashWidget


GEARS = ['P', 'R', 'N', '1', '2', '3', 'OD']

# AW-4 solenoid logic: Sol A (ch1), Sol B (ch2)
# 1st: A=OFF, B=ON   2nd: A=ON, B=ON   3rd: A=ON, B=OFF   OD: A=OFF, B=OFF
GEAR_MAP = {
    (False, True): ('1', '1ST'),
    (True, True): ('2', '2ND'),
    (True, False): ('3', '3RD'),
    (False, False): ('OD', 'O/D'),
}


class GearBox(BoxLayout):
    """Single gear indicator box."""

    def __init__(self, gear_text, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (54, 50)
        self.gear_text = gear_text
        self.active = False
        # Skin colors, pushed in by the parent GearIndicator
        self._primary = (1, 0.69, 0, 1)
        self._dim = (0.4, 0.27, 0, 1)

        self.label = Label(
            text=gear_text,
            font_size='20sp',
            bold=True,
            halign='center',
            valign='center',
        )
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.label)
        self.bind(size=self._redraw, pos=self._redraw)

    def set_colors(self, primary, dim):
        self._primary = primary
        self._dim = dim
        self.label.color = primary if self.active else dim
        self._redraw()

    def set_active(self, active):
        self.active = active
        self.label.color = self._primary if active else self._dim
        self._redraw()

    def _redraw(self, *args):
        p = self._primary
        d = self._dim
        self.canvas.before.clear()
        with self.canvas.before:
            if self.active:
                Color(p[0], p[1], p[2], 0.1)
            else:
                Color(0, 0, 0, 0.5)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            if self.active:
                Color(*p)
            else:
                Color(d[0], d[1], d[2], 0.5)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1.5)


class GearIndicator(DashWidget):
    """Full gear indicator with gear boxes and current gear display."""

    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('spacing', 6)
        kwargs.setdefault('padding', [12, 8, 12, 4])
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 200)
        super().__init__(**kwargs)

        self._current_gear = None

        # Gear boxes row
        gear_row = BoxLayout(
            orientation='horizontal',
            spacing=6,
            size_hint_y=None,
            height=54,
        )
        gear_row.add_widget(BoxLayout())  # left spacer

        self._gear_boxes = {}
        for gear in GEARS:
            gb = GearBox(gear)
            self._gear_boxes[gear] = gb
            gear_row.add_widget(gb)

        gear_row.add_widget(BoxLayout())  # right spacer
        self.add_widget(gear_row)

        # Current gear large display
        self.current_label = Label(
            text='--',
            font_size='52sp',
            bold=True,
            halign='center',
            valign='center',
            size_hint_y=0.55,
        )
        self.current_label.bind(size=self.current_label.setter('text_size'))
        self.add_widget(self.current_label)

        # Subtitle
        self.subtitle = Label(
            text='CURRENT GEAR',
            font_size='11sp',
            halign='center',
            valign='top',
            size_hint_y=0.15,
        )
        self.subtitle.bind(size=self.subtitle.setter('text_size'))
        self.add_widget(self.subtitle)

        self._watch_skin(self._apply_skin)
        self._schedule_update(hz=5)

    def _get_relay_controller(self):
        app = App.get_running_app()
        return getattr(app, 'relay_controller', None)

    def _apply_skin(self, *args):
        primary = self._c('primary')
        dim = self._c('dim')
        self.current_label.color = primary
        self.subtitle.color = self._c('dim')
        for gb in self._gear_boxes.values():
            gb.set_colors(primary, dim)

    def _update(self, dt):
        rc = self._get_relay_controller()
        if not rc:
            return

        sol_a = rc.get_cached(1)
        sol_b = rc.get_cached(2)
        key = (sol_a, sol_b)
        gear_short, gear_display = GEAR_MAP.get(key, ('N', 'NEUTRAL'))

        if gear_short != self._current_gear:
            self._current_gear = gear_short
            self.current_label.text = gear_display
            for gear, gb in self._gear_boxes.items():
                gb.set_active(gear == gear_short)
