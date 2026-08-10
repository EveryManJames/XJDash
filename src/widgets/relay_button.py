"""
RelayButton - Touch toggle for a single relay channel.
Uses Canvas-drawn icons from the icon library.
"""

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.graphics import Color, Line, RoundedRectangle

from widgets.base_widget import DashWidget
from widgets.icons import draw_icon


class IconWidget(Widget):
    """Widget that draws a Canvas icon at its center."""

    def __init__(self, icon_name='power', **kwargs):
        kwargs.setdefault('size_hint_y', 0.35)
        super().__init__(**kwargs)
        self.icon_name = icon_name
        self._color = (1, 0.69, 0, 1)
        self.bind(size=self._redraw, pos=self._redraw)

    def set_icon(self, name):
        self.icon_name = name
        self._redraw()

    def set_color(self, color):
        self._color = color
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*self._color)
            cx = self.x + self.width / 2
            cy = self.y + self.height / 2
            icon_size = min(self.width, self.height) * 0.7
            draw_icon(self.icon_name, cx, cy, icon_size)


class RelayButton(ButtonBehavior, DashWidget):
    """Large touch-friendly relay toggle button with Canvas icon."""

    def __init__(self, channel, icon_name='power', name='RELAY',
                 info='MANUAL', **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', [12, 10, 12, 8])
        kwargs.setdefault('spacing', 4)
        super().__init__(**kwargs)

        self.channel = channel
        self._is_on = False
        self._info_text = info
        self._icon_name = icon_name

        # Canvas-drawn icon
        self.icon_widget = IconWidget(icon_name=icon_name)

        # Name
        self.name_label = Label(
            text=name, font_size='12sp',
            size_hint_y=0.2,
            halign='center', valign='center',
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))

        # State badge
        self.state_label = Label(
            text='OFF', font_size='11sp', bold=True,
            size_hint_y=0.2,
            halign='center', valign='center',
        )
        self.state_label.bind(size=self.state_label.setter('text_size'))

        # Info text
        self.info_label = Label(
            text=info, font_size='9sp',
            size_hint_y=0.25,
            halign='center', valign='center',
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))

        self.add_widget(self.icon_widget)
        self.add_widget(self.name_label)
        self.add_widget(self.state_label)
        self.add_widget(self.info_label)

        self.bind(size=self._redraw, pos=self._redraw)
        self.bind(on_press=self._on_toggle)
        self._schedule_update(hz=5)

    def set_icon(self, icon_name):
        """Change the icon at runtime."""
        self._icon_name = icon_name
        self.icon_widget.set_icon(icon_name)

    def _get_relay_controller(self):
        app = App.get_running_app()
        return getattr(app, 'relay_controller', None)

    def _on_toggle(self, *args):
        rc = self._get_relay_controller()
        if rc:
            rc.toggle(self.channel)

    def _update(self, dt):
        rc = self._get_relay_controller()
        if rc:
            self._is_on = rc.get_relay(self.channel)
        self._redraw()

    def _redraw(self, *args):
        primary = self._c('primary')
        dim = self._c('dim')

        if self._is_on:
            self.state_label.text = 'ON'
            self.state_label.color = primary
            self.name_label.color = primary
            self.icon_widget.set_color(primary)
            self.info_label.color = dim
            border_color = primary
            bg_alpha = 0.08
        else:
            self.state_label.text = 'OFF'
            self.state_label.color = self._c('dim', 0.5)
            self.name_label.color = dim
            self.icon_widget.set_color(dim)
            self.info_label.color = self._c('dim', 0.5)
            border_color = self._c('dim', 0.3)
            bg_alpha = 0.02

        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._c('primary', bg_alpha))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            Color(*border_color)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 10), width=1.5)
