"""
BaseScreen - Common screen structure with header, content area, and nav bar.

Layout (480x800):
  HeaderBar:  44px
  Content:   692px (subclass fills this)
  NavBar:     64px

Also owns the skin background (solid color, or image with darken overlay)
and re-applies skin colors to registered static labels when the user
switches themes.
"""

import os

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout

from widgets.header_bar import HeaderBar
from widgets.nav_bar import NavBar


class BaseScreen(Screen):
    """Base screen with header + content + bottom nav."""

    def __init__(self, screen_name, title, screen_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.screen_name = screen_name
        self._skin_labels = []

        root = BoxLayout(orientation='vertical')
        self._root = root

        # Header
        self.header = HeaderBar(title=title)
        root.add_widget(self.header)

        # Content area — subclasses add widgets to this
        self.content = BoxLayout(orientation='vertical')
        root.add_widget(self.content)

        # Bottom nav
        self.nav = NavBar(active_tab=screen_name, screen_manager=screen_manager)
        root.add_widget(self.nav)

        self.add_widget(root)

        root.bind(size=self._redraw_background, pos=self._redraw_background)
        Clock.schedule_once(self._subscribe_skin, 0)

    # ─── Skin integration ─────────────────────────────────────────

    def register_skin_label(self, label, color_name, alpha=1.0):
        """Track a static label so its color follows the active skin."""
        self._skin_labels.append((label, color_name, alpha))

    def _subscribe_skin(self, *args):
        app = App.get_running_app()
        if app and hasattr(app, 'skin_manager'):
            app.skin_manager.subscribe(self._on_skin_change)
        self._on_skin_change()

    def _on_skin_change(self):
        self._redraw_background()
        self._apply_skin_labels()
        self.apply_skin()

    def _apply_skin_labels(self):
        app = App.get_running_app()
        if not app:
            return
        for label, color_name, alpha in self._skin_labels:
            rgb = app.skin_manager.get_color(color_name)
            label.color = (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha)

    def apply_skin(self):
        """Hook for subclasses with skin-dependent state beyond labels."""
        pass

    def _redraw_background(self, *args):
        app = App.get_running_app()
        if not app or not hasattr(app, 'skin_manager'):
            return

        bg = app.skin_manager.get_background()
        canvas = self._root.canvas.before
        canvas.clear()
        with canvas:
            color = bg.get('color', [0, 0, 0])
            Color(color[0] / 255, color[1] / 255, color[2] / 255, 1)
            Rectangle(pos=self._root.pos, size=self._root.size)

            if bg.get('type') == 'image':
                path = bg.get('path', '')
                if path and os.path.exists(path):
                    Color(1, 1, 1, bg.get('opacity', 1.0))
                    Rectangle(pos=self._root.pos, size=self._root.size,
                              source=path)
                    darken = bg.get('darken', 0)
                    if darken:
                        Color(0, 0, 0, darken)
                        Rectangle(pos=self._root.pos, size=self._root.size)
