"""
SolenoidRow - Single solenoid status row (name, status badge, amps).
"""

from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.app import App
from kivy.clock import Clock

from widgets.base_widget import DashWidget


class SolenoidRow(DashWidget):
    """Horizontal row showing one solenoid's state."""

    def __init__(self, channel, name='SOLENOID', **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 44)
        kwargs.setdefault('padding', [12, 6, 12, 6])
        kwargs.setdefault('spacing', 8)
        super().__init__(**kwargs)

        self.channel = channel
        self._is_on = False

        # Name
        self.name_label = Label(
            text=name,
            font_size='13sp',
            halign='left',
            valign='center',
            size_hint_x=0.5,
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))

        # Status badge
        self.status_label = Label(
            text='OFF',
            font_size='11sp',
            bold=True,
            halign='center',
            valign='center',
            size_hint_x=0.3,
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))

        # Amps
        self.amps_label = Label(
            text='0.0A',
            font_size='11sp',
            halign='right',
            valign='center',
            size_hint_x=0.2,
        )
        self.amps_label.bind(size=self.amps_label.setter('text_size'))

        self.add_widget(self.name_label)
        self.add_widget(self.status_label)
        self.add_widget(self.amps_label)

        self.bind(size=self._redraw, pos=self._redraw)
        self._schedule_update(hz=5)

    def _update(self, dt):
        rc = self._get_relay_controller()
        if rc:
            self._is_on = rc.get_cached(self.channel)
        self._apply_state()

    def _get_relay_controller(self):
        app = App.get_running_app()
        return getattr(app, 'relay_controller', None)

    def _apply_state(self):
        if self._is_on:
            self.status_label.text = 'ENGAGED'
            self.status_label.color = self._c('primary')
            self.amps_label.text = '0.8A'
            self.name_label.color = self._c('primary')
        else:
            self.status_label.text = 'OFF'
            self.status_label.color = self._c('dim', 0.5)
            self.amps_label.text = '0.0A'
            self.name_label.color = self._c('dim')
        self.amps_label.color = self._c('dim')
        self._redraw()

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._c('inactive', 0.3))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            Color(*self._c('dim', 0.2))
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1)
