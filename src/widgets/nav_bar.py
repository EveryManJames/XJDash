"""
NavBar - Bottom navigation bar with 5 tabs.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line
from kivy.app import App

from widgets.base_widget import DashWidget
from widgets.icons import IconWidget


# Canvas icon names from the icon library \u2014 Kivy's bundled font has no
# glyphs for the symbol/emoji codepoints, so text icons render as boxes.
TABS = [
    ('gauges', 'GAUGES', 'gauge'),
    ('transmission', 'TRANS', 'arrows_updown'),
    ('relay', 'RELAY', 'lightning'),
    ('diagnostics', 'DIAG', 'wrench'),
    ('settings', 'SET', 'gear'),
]


class NavTab(ButtonBehavior, BoxLayout):
    """Single nav tab button."""

    def __init__(self, screen_name, label_text, icon_name, **kwargs):
        kwargs['orientation'] = 'vertical'
        kwargs['size_hint_x'] = 1
        kwargs['padding'] = [0, 6, 0, 4]
        kwargs['spacing'] = 2
        super().__init__(**kwargs)

        self.screen_name = screen_name
        self.active = False

        self.icon_widget = IconWidget(
            icon_name=icon_name,
            scale=0.85,
            size_hint_y=0.6,
        )

        self.text_label = Label(
            text=label_text,
            font_size='9sp',
            size_hint_y=0.4,
            halign='center',
            valign='top',
        )
        self.text_label.bind(size=self.text_label.setter('text_size'))

        self.add_widget(self.icon_widget)
        self.add_widget(self.text_label)

    def set_active(self, active, primary_color, dim_color):
        self.active = active
        color = primary_color if active else dim_color
        self.icon_widget.set_color(color)
        self.text_label.color = color


class NavBar(DashWidget):
    """Bottom navigation bar with 5 screen tabs."""

    def __init__(self, active_tab='gauges', screen_manager=None, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 64)
        super().__init__(**kwargs)

        self.screen_manager = screen_manager
        self._active_tab = active_tab
        self._tabs = []

        for screen_name, label_text, icon_name in TABS:
            tab = NavTab(screen_name, label_text, icon_name)
            tab.bind(on_press=self._on_tab_press)
            self._tabs.append(tab)
            self.add_widget(tab)

        self.bind(size=self._redraw, pos=self._redraw)
        # Apply colors now and on every skin change
        self._watch_skin(self._apply_colors)
        self._watch_skin(self._redraw)

    def _on_tab_press(self, tab):
        if self.screen_manager and tab.screen_name != self._active_tab:
            self._active_tab = tab.screen_name
            self.screen_manager.current = tab.screen_name
            self._apply_colors()

    def _apply_colors(self, *args):
        try:
            primary = self._c('primary')
            dim = self._c('dim')
        except Exception:
            primary = (1, 0.69, 0, 1)
            dim = (0.4, 0.27, 0, 1)

        for tab in self._tabs:
            tab.set_active(tab.screen_name == self._active_tab, primary, dim)

    def set_active(self, screen_name):
        """Update active tab externally."""
        self._active_tab = screen_name
        self._apply_colors()

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            try:
                Color(*self._c('background'))
            except Exception:
                Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=self.size)
            try:
                Color(*self._c('dim', 0.3))
            except Exception:
                Color(0.2, 0.2, 0.2, 1)
            Line(points=[self.x, self.top, self.right, self.top], width=1)
