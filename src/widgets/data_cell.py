"""
DataCell - Single data readout cell with label, value, and unit.
"""

from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line

from widgets.base_widget import DashWidget


class DataCell(DashWidget):
    """Displays a single engine data value with label and unit."""

    def __init__(self, data_key, label_text, unit='', format_str='{:.0f}',
                 warning_threshold=None, critical_threshold=None,
                 warn_below=False, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', [10, 8, 10, 6])
        kwargs.setdefault('spacing', 2)
        super().__init__(**kwargs)

        self.data_key = data_key
        self.format_str = format_str
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.warn_below = warn_below  # True = warn when value drops BELOW threshold
        self._last_value = None

        # Label (top)
        self.name_label = Label(
            text=label_text,
            font_size='11sp',
            halign='left',
            valign='center',
            size_hint_y=0.2,
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))

        # Value (center, large)
        self.value_label = Label(
            text='--',
            font_size='28sp',
            bold=True,
            halign='left',
            valign='center',
            size_hint_y=0.55,
        )
        self.value_label.bind(size=self.value_label.setter('text_size'))

        # Unit (bottom)
        self.unit_label = Label(
            text=unit,
            font_size='11sp',
            halign='left',
            valign='center',
            size_hint_y=0.25,
        )
        self.unit_label.bind(size=self.unit_label.setter('text_size'))

        self.add_widget(self.name_label)
        self.add_widget(self.value_label)
        self.add_widget(self.unit_label)

        self.bind(size=self._redraw_bg, pos=self._redraw_bg)
        self._schedule_update(hz=10)

    def _update(self, dt):
        val = self.data_manager.get(self.data_key)
        if val is None:
            self.value_label.text = '--'
            return

        if val != self._last_value:
            self._last_value = val
            try:
                self.value_label.text = self.format_str.format(val)
            except (ValueError, TypeError):
                self.value_label.text = str(val)

        # Colors every tick so threshold state and skin changes both apply
        color = self._c('primary')
        if self.critical_threshold is not None:
            if (not self.warn_below and val >= self.critical_threshold) or \
               (self.warn_below and val <= self.critical_threshold):
                color = self._c('critical')
            elif self.warning_threshold is not None:
                if (not self.warn_below and val >= self.warning_threshold) or \
                   (self.warn_below and val <= self.warning_threshold):
                    color = self._c('warning')
        elif self.warning_threshold is not None:
            if (not self.warn_below and val >= self.warning_threshold) or \
               (self.warn_below and val <= self.warning_threshold):
                color = self._c('warning')

        self.value_label.color = color
        self.name_label.color = self._c('dim')
        self.unit_label.color = self._c('secondary')

    def _redraw_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._c('inactive', 0.4))
            Rectangle(pos=self.pos, size=self.size)
            Color(*self._c('dim', 0.2))
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 6), width=1)
