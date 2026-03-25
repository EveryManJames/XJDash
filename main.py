#!/usr/bin/env python3
"""
XJDash - Digital Dashboard for 1990 Jeep Cherokee XJ
Main application entry point

Author: James Martin
License: MIT
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

# Configure Kivy for portrait mode touchscreen
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', False)

# Optional: Set fullscreen for Pi deployment
# Config.set('graphics', 'fullscreen', 'auto')

# Optimize for embedded system
Config.set('graphics', 'maxfps', '30')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from core.serial_manager import SerialManager
from core.data_manager import DataManager
from skins.skin_manager import SkinManager

# Import screens (we'll create these)
# from screens.main_screen import MainGaugeScreen
# from screens.relay_screen import RelayControlScreen
# from screens.settings_screen import SettingsScreen


class XJDashApp(App):
    """Main XJDash Application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "XJDash - Jeep Cherokee Digital Dashboard"

        # Core managers
        self.data_manager = DataManager()
        self.serial_manager = SerialManager(self.data_manager)
        self.skin_manager = SkinManager()

        # Screen manager
        self.screen_manager = None

    def build(self):
        """Build the application UI"""

        # Load default skin
        self.skin_manager.load_skin('default_amber')

        # Create screen manager
        self.screen_manager = ScreenManager(transition=SlideTransition())

        # Add screens (placeholder for now)
        # self.screen_manager.add_widget(MainGaugeScreen(name='main'))
        # self.screen_manager.add_widget(RelayControlScreen(name='relay'))
        # self.screen_manager.add_widget(SettingsScreen(name='settings'))

        # Temporary placeholder screen
        placeholder = Screen(name='placeholder')
        self.screen_manager.add_widget(placeholder)

        return self.screen_manager

    def on_start(self):
        """Called when app starts"""
        print("🚙 XJDash starting...")

        # Start serial connection to REM
        # (will use mock data if REM not connected)
        self.serial_manager.connect()

        print("✅ XJDash ready!")

    def on_stop(self):
        """Called when app stops"""
        print("🛑 XJDash stopping...")

        # Clean shutdown
        self.serial_manager.disconnect()
        self.data_manager.close()


if __name__ == '__main__':
    XJDashApp().run()
