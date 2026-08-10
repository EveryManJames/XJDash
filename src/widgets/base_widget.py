"""
DashWidget - Base class for all XJDash widgets.

Provides DataManager/SkinManager integration, color conversion,
and 10Hz polling for live data updates.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.clock import Clock

from core.data_manager import DataManager


class DashWidget(BoxLayout):
    """Base widget with DataManager + SkinManager integration."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = DataManager()
        self._app = None
        self._update_event = None

    @property
    def skin(self):
        if self._app is None:
            self._app = App.get_running_app()
        return self._app.skin_manager

    def _c(self, color_name, alpha=1.0):
        """Get a skin color as Kivy-normalized RGBA tuple.
        Shorthand for the most common operation in every widget."""
        rgb = self.skin.get_color(color_name)
        return self._to_kivy_color(rgb, alpha)

    def _to_kivy_color(self, rgb, alpha=1.0):
        """Convert (255,176,0) to (1.0, 0.69, 0.0, 1.0)."""
        if len(rgb) == 4:
            return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, rgb[3] / 255)
        return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha)

    def _watch_skin(self, callback):
        """Invoke callback now and whenever the skin changes.

        Deferred one frame so App.get_running_app() is available. Use for
        widgets whose redraws are change-gated and would otherwise keep
        stale colors after a theme switch.
        """
        def _sub(dt):
            try:
                self.skin.subscribe(callback)
            except Exception:
                pass
            callback()
        Clock.schedule_once(_sub, 0)

    def _schedule_update(self, hz=10):
        """Start polling at given Hz."""
        if self._update_event is None:
            self._update_event = Clock.schedule_interval(self._update, 1.0 / hz)

    def _unschedule_update(self):
        """Stop polling."""
        if self._update_event:
            self._update_event.cancel()
            self._update_event = None

    def _update(self, dt):
        """Override in subclass to read data and refresh display."""
        pass
