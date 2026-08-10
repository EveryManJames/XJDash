"""
StatusCard - Diagnostic card with title and label/value rows.
"""

from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line

from widgets.base_widget import DashWidget
from core.data_manager import DataManager


# Color name to Kivy color mapping for status values
STATUS_COLORS = {
    'good': (0, 0.8, 0, 1),
    'warn': (1, 0.4, 0, 1),
    'err': (1, 0, 0, 1),
    'default': None,  # use primary from skin
}


class StatusRow(DashWidget):
    """Single row in a status card: label on left, value on right."""

    def __init__(self, label_text, value='--', data_key=None,
                 format_str='{}', color_name='default', **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 24)
        super().__init__(**kwargs)

        self.data_key = data_key
        self.format_str = format_str
        self.color_name = color_name
        self._static_value = value

        self.label_widget = Label(
            text=label_text, font_size='12sp',
            halign='left', valign='center',
            size_hint_x=0.55,
        )
        self.label_widget.bind(size=self.label_widget.setter('text_size'))

        self.value_widget = Label(
            text=value, font_size='12sp', bold=True,
            halign='right', valign='center',
            size_hint_x=0.45,
        )
        self.value_widget.bind(size=self.value_widget.setter('text_size'))

        self.add_widget(self.label_widget)
        self.add_widget(self.value_widget)

        if data_key:
            self._schedule_update(hz=2)
        else:
            from kivy.clock import Clock
            Clock.schedule_once(self._apply_colors, 0)

    def _update(self, dt):
        if self.data_key:
            val = self.data_manager.get(self.data_key)
            if val is not None:
                try:
                    self.value_widget.text = self.format_str.format(val)
                except (ValueError, TypeError):
                    self.value_widget.text = str(val)
        self._apply_colors()

    def _apply_colors(self, *args):
        try:
            self.label_widget.color = self._c('secondary')
            fixed = STATUS_COLORS.get(self.color_name)
            self.value_widget.color = fixed if fixed else self._c('primary')
        except Exception:
            pass


class StatusCard(DashWidget):
    """Card container with title and multiple status rows."""

    def __init__(self, title, rows=None, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('padding', [10, 8, 10, 8])
        kwargs.setdefault('spacing', 2)
        super().__init__(**kwargs)

        self._rows_data = rows or []

        # Title
        title_label = Label(
            text=title,
            font_size='11sp',
            halign='left',
            valign='center',
            size_hint_y=None,
            height=22,
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)

        # Rows
        for row_def in self._rows_data:
            row = StatusRow(
                label_text=row_def.get('label', ''),
                value=row_def.get('value', '--'),
                data_key=row_def.get('data_key'),
                format_str=row_def.get('format', '{}'),
                color_name=row_def.get('color', 'default'),
            )
            self.add_widget(row)

        # Calculate height: title + rows
        row_count = len(self._rows_data)
        self.height = 22 + 8 + (row_count * 26) + 16

        self.bind(size=self._redraw_bg, pos=self._redraw_bg)
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._set_title_color(title_label), 0)

    def _set_title_color(self, title_label):
        try:
            title_label.color = self._c('dim')
        except Exception:
            title_label.color = (0.4, 0.27, 0, 1)

    def _redraw_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            try:
                Color(*self._c('inactive', 0.3))
            except Exception:
                Color(0.04, 0.03, 0, 0.3)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            try:
                Color(*self._c('dim', 0.15))
            except Exception:
                Color(0.15, 0.1, 0, 0.15)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1)
