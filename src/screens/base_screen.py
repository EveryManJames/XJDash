"""
BaseScreen - Common screen structure with header, content area, and nav bar.

Layout (480x800):
  HeaderBar:  44px
  Content:   692px (subclass fills this)
  NavBar:     64px
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout

from widgets.header_bar import HeaderBar
from widgets.nav_bar import NavBar


class BaseScreen(Screen):
    """Base screen with header + content + bottom nav."""

    def __init__(self, screen_name, title, screen_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.screen_name = screen_name

        root = BoxLayout(orientation='vertical')

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
