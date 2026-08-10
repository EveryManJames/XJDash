"""
BarGauge - Horizontal bar gauge with label, value, and fill track.
"""

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle

from widgets.base_widget import DashWidget


class BarGauge(DashWidget):
    """Horizontal bar with fill proportional to data value."""

    def __init__(self, data_key, label_text, min_val=0, max_val=100,
                 warning_threshold=None, format_str='{:.0f}', unit='',
                 **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 38)
        kwargs.setdefault('padding', [12, 2, 12, 2])
        kwargs.setdefault('spacing', 2)
        super().__init__(**kwargs)

        self.data_key = data_key
        self.min_val = min_val
        self.max_val = max_val
        self.warning_threshold = warning_threshold
        self.format_str = format_str
        self.unit = unit
        self._last_value = None

        # Header row: label left, value right
        header = BoxLayout(orientation='horizontal', size_hint_y=0.45)
        self.label_widget = Label(
            text=label_text, font_size='11sp',
            halign='left', valign='center',
        )
        self.label_widget.bind(size=self.label_widget.setter('text_size'))

        self.value_widget = Label(
            text='--', font_size='11sp',
            halign='right', valign='center',
        )
        self.value_widget.bind(size=self.value_widget.setter('text_size'))

        header.add_widget(self.label_widget)
        header.add_widget(self.value_widget)
        self.add_widget(header)

        # Bar track
        self.track = Widget(size_hint_y=0.55)
        self.track.bind(size=self._redraw_bar, pos=self._redraw_bar)
        self.add_widget(self.track)

        self._fill_pct = 0
        self._schedule_update(hz=10)

    def _update(self, dt):
        val = self.data_manager.get(self.data_key)
        if val is None:
            return

        if val != self._last_value:
            self._last_value = val
            self.value_widget.text = self.format_str.format(val) + self.unit

            # Calculate fill percentage
            pct = (val - self.min_val) / (self.max_val - self.min_val)
            self._fill_pct = max(0, min(1, pct))
            self._redraw_bar()

        self.label_widget.color = self._c('dim')
        self.value_widget.color = self._c('dim')

    def _redraw_bar(self, *args):
        t = self.track
        t.canvas.clear()
        with t.canvas:
            # Track background
            Color(*self._c('inactive', 0.4))
            RoundedRectangle(pos=t.pos, size=t.size, radius=[3])

            # Fill
            fill_w = t.width * self._fill_pct
            if fill_w > 0:
                # Choose color based on warning threshold
                if self.warning_threshold is not None and \
                   self._last_value is not None and \
                   self._last_value >= self.warning_threshold:
                    Color(*self._c('warning'))
                else:
                    Color(*self._c('primary'))
                RoundedRectangle(pos=t.pos, size=(fill_w, t.height), radius=[3])
