#!/usr/bin/env python3
"""
XJDash - Digital Dashboard for 1990 Jeep Cherokee XJ
Main application entry point

Author: James Martin
License: MIT
"""

import os
import signal
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
from core.gyro_manager import GyroManager
from core.power_latch import PowerLatch
from core.ignition_monitor import IgnitionShutdownManager
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

        # Power latch — hold the relay ON so buck converter stays powered
        # Must be engaged before anything else so we don't lose power
        # if the ignition key is released during boot
        self.power_latch = PowerLatch()
        self.power_latch.engage()

        # Core managers
        self.data_manager = DataManager()
        self.serial_manager = SerialManager(self.data_manager)
        self.gyro_manager = GyroManager(self.data_manager)
        self.skin_manager = SkinManager()

        # Ignition-sense shutdown manager
        self.ignition_monitor = IgnitionShutdownManager(
            cleanup_callback=self._cleanup,
            power_latch=self.power_latch,
        )

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

        # Start gyroscope/IMU
        # (will use mock data if BNO055 not connected)
        self.gyro_manager.connect()

        # Start ignition sense monitoring
        # (disabled automatically on desktop — no RPi.GPIO)
        self.ignition_monitor.start()

        # Handle SIGTERM / SIGINT so systemd stop and Ctrl-C
        # still trigger a clean shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        print("✅ XJDash ready!")

    def on_stop(self):
        """Called when app stops (normal Kivy exit)"""
        self._cleanup()

    def _cleanup(self):
        """Shared shutdown sequence used by on_stop, signal handler, and ignition monitor."""
        if getattr(self, '_cleaned_up', False):
            return
        self._cleaned_up = True

        print("🛑 XJDash shutting down...")
        self.ignition_monitor.stop()
        self.serial_manager.disconnect()
        self.gyro_manager.disconnect()
        self.data_manager.close()
        print("🛑 Cleanup complete")

    def _signal_handler(self, signum, frame):
        """Handle SIGTERM/SIGINT for clean shutdown."""
        print(f"[SIG] Received signal {signum} — shutting down")
        self._cleanup()
        self.power_latch.release()
        self.stop()


if __name__ == '__main__':
    XJDashApp().run()
