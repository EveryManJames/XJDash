"""
RPMArcGauge - Half-circle arc gauge with needle and digital RPM readout.
"""

import math

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.app import App
from kivy.clock import Clock

from core.data_manager import DataManager


class RPMArcGauge(FloatLayout):
    """Arc gauge drawn with Canvas instructions. Shows RPM 0-6000."""

    RPM_MIN = 0
    RPM_MAX = 6000
    REDLINE = 5000
    # Needle math uses standard math angles: 0 RPM = 180deg (west, CCW from east).
    # Kivy's Line(ellipse=...) instead measures degrees CLOCKWISE FROM NORTH,
    # so the same top semicircle spans -90 (west) to +90 (east) there.
    ARC_START = 180  # math degrees (left)
    ARC_SWEEP = 180  # total sweep degrees
    KIVY_WEST = -90  # arc start in Kivy ellipse degrees
    KIVY_EAST = 90   # arc end in Kivy ellipse degrees

    def __init__(self, **kwargs):
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 220)
        super().__init__(**kwargs)

        self.data_manager = DataManager()
        self._app = None
        self._rpm = 0
        self._last_rpm = -1

        # Digital readout label
        self.rpm_label = Label(
            text='0',
            font_size='56sp',
            bold=True,
            halign='center',
            valign='bottom',
            size_hint=(1, 0.4),
            pos_hint={'center_x': 0.5, 'y': 0.0},
        )
        self.add_widget(self.rpm_label)

        # "RPM x 1000" label
        self.unit_label = Label(
            text='RPM',
            font_size='12sp',
            halign='center',
            valign='top',
            size_hint=(1, 0.15),
            pos_hint={'center_x': 0.5, 'y': 0.0},
        )
        self.add_widget(self.unit_label)

        self.bind(size=self._redraw, pos=self._redraw)
        self._update_event = Clock.schedule_interval(self._update, 1.0 / 15)
        Clock.schedule_once(self._subscribe_skin, 0)

    def _subscribe_skin(self, *args):
        try:
            self.skin.subscribe(self._redraw)
        except Exception:
            pass
        self._redraw()

    @property
    def skin(self):
        if self._app is None:
            self._app = App.get_running_app()
        return self._app.skin_manager

    def _c(self, name, alpha=1.0):
        rgb = self.skin.get_color(name)
        if len(rgb) == 4:
            return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, rgb[3] / 255)
        return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha)

    def _update(self, dt):
        rpm = self.data_manager.get('RPM', 0)
        self._rpm = rpm
        if int(rpm) != self._last_rpm:
            self._last_rpm = int(rpm)
            self.rpm_label.text = str(int(rpm))
            self._redraw()

    def _redraw(self, *args):
        # Colors
        primary = self._c('primary')
        inactive = self._c('inactive')
        critical = self._c('critical')
        dim = self._c('dim')

        self.rpm_label.color = primary
        self.unit_label.color = dim

        # Arc geometry
        cx = self.x + self.width / 2
        cy = self.y + self.height * 0.35
        radius = min(self.width * 0.42, self.height * 0.65)
        arc_width = 10

        # RPM to angle. Math convention (needle): 0 RPM = 180 deg (left),
        # 6000 RPM = 0 deg (right). Kivy ellipse convention (arcs): 0 RPM =
        # -90 (west), 6000 RPM = +90 (east), measured clockwise from north.
        rpm_pct = max(0, min(1, self._rpm / self.RPM_MAX))
        value_angle = self.ARC_START - (rpm_pct * self.ARC_SWEEP)
        value_kivy = self.KIVY_WEST + (rpm_pct * self.ARC_SWEEP)
        redline_kivy = self.KIVY_WEST + ((self.REDLINE / self.RPM_MAX) * self.ARC_SWEEP)

        self.canvas.before.clear()
        with self.canvas.before:
            # Background arc (full sweep)
            Color(*inactive)
            Line(
                ellipse=(cx - radius, cy - radius, radius * 2, radius * 2,
                         self.KIVY_WEST, self.KIVY_EAST),
                width=arc_width,
                cap='round',
            )

            # Redline zone (background, dim)
            Color(*critical[:3], 0.15)
            Line(
                ellipse=(cx - radius, cy - radius, radius * 2, radius * 2,
                         redline_kivy, self.KIVY_EAST),
                width=arc_width,
                cap='round',
            )

            # Value arc
            if rpm_pct > 0:
                if self._rpm >= self.REDLINE:
                    Color(*critical)
                else:
                    Color(*primary)
                Line(
                    ellipse=(cx - radius, cy - radius, radius * 2, radius * 2,
                             self.KIVY_WEST, value_kivy),
                    width=arc_width,
                    cap='round',
                )

            # Needle line
            angle_rad = math.radians(value_angle)
            needle_len = radius - 15
            nx = cx + needle_len * math.cos(angle_rad)
            ny = cy + needle_len * math.sin(angle_rad)
            Color(*primary)
            Line(points=[cx, cy, nx, ny], width=2, cap='round')

            # Center dot
            dot_r = 5
            Ellipse(pos=(cx - dot_r, cy - dot_r), size=(dot_r * 2, dot_r * 2))

            # Tick labels around arc
            Color(*dim)
            for tick_rpm in range(0, 7000, 1000):
                tick_pct = tick_rpm / self.RPM_MAX
                tick_angle = self.ARC_START - (tick_pct * self.ARC_SWEEP)
                tick_rad = math.radians(tick_angle)
                inner_r = radius + 4
                outer_r = radius + 12
                ix = cx + inner_r * math.cos(tick_rad)
                iy = cy + inner_r * math.sin(tick_rad)
                ox = cx + outer_r * math.cos(tick_rad)
                oy = cy + outer_r * math.sin(tick_rad)
                if tick_rpm >= self.REDLINE:
                    Color(*critical[:3], 0.5)
                else:
                    Color(*dim)
                Line(points=[ix, iy, ox, oy], width=1.5, cap='round')
