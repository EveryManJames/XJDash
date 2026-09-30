"""
HeaderBar - Top bar with title and connection status indicator.
"""

from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Rectangle, Line

from widgets.base_widget import DashWidget


class HeaderBar(DashWidget):
    """Top bar: title on left, connection status dot + text on right."""

    def __init__(self, title='XJDASH', **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 44)
        kwargs.setdefault('padding', [16, 0, 16, 0])
        super().__init__(**kwargs)

        self._title_text = title
        self._connected = False
        self._mock = False

        # Title label (left)
        self.title_label = Label(
            text=title,
            font_size='16sp',
            bold=True,
            halign='left',
            valign='center',
            size_hint_x=0.5,
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        self.add_widget(self.title_label)

        # Status label (right)
        self.status_label = Label(
            text='  CONNECTING...',
            font_size='11sp',
            halign='right',
            valign='center',
            size_hint_x=0.5,
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.add_widget(self.status_label)

        self.bind(size=self._redraw, pos=self._redraw)
        self._watch_skin(self._redraw)
        self._schedule_update(hz=2)

    def _update(self, dt):
        # Data is "live" only if RPM was refreshed recently — a value
        # sitting in the store after the REM dies doesn't count.
        from core.data_manager import STALE_AFTER
        age = self.data_manager.age('RPM')
        connected = age is not None and age < STALE_AFTER

        from kivy.app import App
        app = App.get_running_app()
        mock = bool(app and getattr(app, 'serial_manager', None)
                    and app.serial_manager.use_mock)

        if connected != self._connected or mock != self._mock:
            self._connected = connected
            self._mock = mock
            self._redraw()

    def _redraw(self, *args):
        # Update colors from skin
        self.title_label.color = self._c('primary')

        if self._connected and self._mock:
            self.status_label.text = '  MOCK DATA'
            self.status_label.color = self._c('warning')
        elif self._connected:
            self.status_label.text = '  REM CONNECTED'
            self.status_label.color = self._c('dim')
        else:
            self.status_label.text = '  DISCONNECTED'
            self.status_label.color = self._to_kivy_color((255, 0, 0))

        # Draw background + border
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._c('background'))
            Rectangle(pos=self.pos, size=self.size)
            # Bottom border line
            Color(*self._c('dim', 0.3))
            Line(points=[self.x, self.y, self.right, self.y], width=1)
