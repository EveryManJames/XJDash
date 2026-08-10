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

from kivy.config import Config

# Configure Kivy for portrait mode touchscreen (MUST be before Window import)
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', False)

# Optional: Set fullscreen for Pi deployment
# Config.set('graphics', 'fullscreen', 'auto')

# Optimize for embedded system
Config.set('graphics', 'maxfps', '30')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, NoTransition

from core.serial_manager import SerialManager
from core.data_manager import DataManager
from skins.skin_manager import SkinManager
from relay.relay_controller import RelayController

from screens.main_gauges_screen import MainGaugesScreen
from screens.relay_control_screen import RelayControlScreen
from screens.transmission_screen import TransmissionScreen
from screens.diagnostics_screen import DiagnosticsScreen
from screens.settings_screen import SettingsScreen


class XJDashApp(App):
    """Main XJDash Application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "XJDash"

        # Core managers
        self.data_manager = DataManager()
        self.serial_manager = SerialManager(self.data_manager)
        self.skin_manager = SkinManager()
        self.relay_controller = RelayController()

    def build(self):
        """Build the application UI"""

        # Load default skin
        self.skin_manager.load_skin('default_amber')

        # Connect relay controller (falls back to mock on desktop)
        self.relay_controller.connect()

        # Create screen manager with instant transitions
        sm = ScreenManager(transition=NoTransition())

        # Add all screens
        sm.add_widget(MainGaugesScreen(
            name='gauges', screen_name='gauges',
            title='XJDASH', screen_manager=sm))
        sm.add_widget(TransmissionScreen(
            name='transmission', screen_name='transmission',
            title='AW-4 TRANS', screen_manager=sm))
        sm.add_widget(RelayControlScreen(
            name='relay', screen_name='relay',
            title='RELAY CTRL', screen_manager=sm))
        sm.add_widget(DiagnosticsScreen(
            name='diagnostics', screen_name='diagnostics',
            title='DIAGNOSTICS', screen_manager=sm))
        sm.add_widget(SettingsScreen(
            name='settings', screen_name='settings',
            title='SETTINGS', screen_manager=sm))

        sm.current = 'gauges'
        return sm

    def on_start(self):
        """Called when app starts"""
        print("XJDash starting...")
        self.serial_manager.connect()
        print("XJDash ready!")

    def on_stop(self):
        """Called when app stops"""
        print("XJDash stopping...")
        self.relay_controller.disconnect()
        self.serial_manager.disconnect()
        self.data_manager.close()


if __name__ == '__main__':
    XJDashApp().run()
