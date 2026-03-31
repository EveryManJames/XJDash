"""
Tests for NeoPixelManager and MockPixelStrip
"""

import json
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.data_manager import DataManager
from core.mock_neopixel import MockPixelStrip
from core.neopixel_manager import NeoPixelManager, _color_int


@pytest.fixture(autouse=True)
def reset_data_manager():
    """Reset the DataManager singleton between tests."""
    dm = DataManager()
    dm.close()
    dm.initialized = False
    dm.__init__()
    yield dm
    dm.close()


# ---------------------------------------------------------------------------
# MockPixelStrip tests
# ---------------------------------------------------------------------------

class TestMockPixelStrip:
    def test_init(self):
        strip = MockPixelStrip(30, 18)
        assert strip.numPixels() == 30

    def test_begin_no_error(self):
        strip = MockPixelStrip(10, 18)
        strip.begin()

    def test_set_and_get_pixel(self):
        strip = MockPixelStrip(10, 18)
        color = _color_int(255, 128, 0)
        strip.setPixelColor(0, color)
        assert strip.getPixelColor(0) == color

    def test_set_pixel_rgb(self):
        strip = MockPixelStrip(10, 18)
        strip.setPixelColorRGB(5, 100, 200, 50)
        expected = _color_int(100, 200, 50)
        assert strip.getPixelColor(5) == expected

    def test_brightness(self):
        strip = MockPixelStrip(10, 18, brightness=100)
        assert strip.getBrightness() == 100
        strip.setBrightness(200)
        assert strip.getBrightness() == 200

    def test_brightness_clamp(self):
        strip = MockPixelStrip(10, 18)
        strip.setBrightness(300)
        assert strip.getBrightness() == 255
        strip.setBrightness(-10)
        assert strip.getBrightness() == 0

    def test_out_of_range_pixel_ignored(self):
        strip = MockPixelStrip(5, 18)
        strip.setPixelColor(10, _color_int(255, 0, 0))  # no crash
        assert strip.getPixelColor(10) == 0

    def test_show_no_error(self):
        strip = MockPixelStrip(10, 18)
        strip.show()


# ---------------------------------------------------------------------------
# NeoPixelManager tests
# ---------------------------------------------------------------------------

class TestNeoPixelManager:
    def test_connect_uses_mock(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        assert mgr._mock is True
        assert mgr._running is True
        mgr.disconnect()

    def test_disconnect_stops_thread(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        mgr.disconnect()
        assert mgr._running is False

    def test_apply_preset_solid(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        mgr.apply_preset('solid_red')
        assert mgr._mode == 'solid'
        assert mgr._color == (255, 0, 0)
        assert reset_data_manager.get('neopixel_preset') == 'solid_red'
        mgr.disconnect()

    def test_apply_preset_breathe(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        mgr.apply_preset('trail_amber')
        assert mgr._mode == 'breathe'
        mgr.disconnect()

    def test_apply_preset_rainbow(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        mgr.apply_preset('rainbow')
        assert mgr._mode == 'rainbow'
        mgr.disconnect()

    def test_apply_preset_temp_reactive(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        mgr.apply_preset('temp_reactive')
        assert mgr._mode == 'temp_reactive'
        mgr.disconnect()

    def test_unknown_preset_ignored(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        mgr.apply_preset('solid_amber')
        mgr.apply_preset('nonexistent_preset')
        # Should still be on previous preset
        assert mgr._preset_name == 'solid_amber'
        mgr.disconnect()

    def test_set_custom_color(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        mgr.set_color(10, 20, 30)
        assert mgr._color == (10, 20, 30)
        assert mgr._mode == 'solid'
        assert reset_data_manager.get('neopixel_preset') == 'custom'
        mgr.disconnect()

    def test_set_brightness(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        mgr.set_brightness(50)
        assert mgr._brightness == 50
        assert reset_data_manager.get('neopixel_brightness') == 50
        mgr.disconnect()

    def test_brightness_clamped_to_max(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        mgr.set_brightness(999)
        assert mgr._brightness == 255
        mgr.disconnect()

    def test_off(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        mgr.apply_preset('solid_red')
        mgr.off()
        assert mgr._preset_name == 'off'
        mgr.disconnect()

    def test_get_presets_returns_dict(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        presets = mgr.get_presets()
        assert isinstance(presets, dict)
        assert 'solid_amber' in presets
        assert 'rainbow' in presets
        assert 'off' in presets

    def test_animation_loop_runs(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        # Let the animation loop run a few frames
        time.sleep(0.15)
        mgr.disconnect()
        # If we got here without error, the loop worked

    def test_default_preset_applied_on_connect(self, reset_data_manager):
        mgr = NeoPixelManager(reset_data_manager)
        mgr.connect()
        # Config default_preset is "solid_amber"
        assert mgr._preset_name == 'solid_amber'
        mgr.disconnect()


class TestColorHelpers:
    def test_color_int(self):
        assert _color_int(255, 0, 0) == 0xFF0000
        assert _color_int(0, 255, 0) == 0x00FF00
        assert _color_int(0, 0, 255) == 0x0000FF
        assert _color_int(255, 255, 255) == 0xFFFFFF

    def test_hsv_to_rgb_red(self):
        r, g, b = NeoPixelManager._hsv_to_rgb(0.0, 1.0, 1.0)
        assert r == 255
        assert g == 0
        assert b == 0

    def test_hsv_to_rgb_green(self):
        r, g, b = NeoPixelManager._hsv_to_rgb(1/3, 1.0, 1.0)
        assert g == 255

    def test_hsv_to_rgb_white(self):
        r, g, b = NeoPixelManager._hsv_to_rgb(0.0, 0.0, 1.0)
        assert r == 255 and g == 255 and b == 255

    def test_lerp_color_endpoints(self):
        c1 = (0, 0, 0)
        c2 = (255, 255, 255)
        assert NeoPixelManager._lerp_color(c1, c2, 0.0) == (0, 0, 0)
        assert NeoPixelManager._lerp_color(c1, c2, 1.0) == (255, 255, 255)

    def test_lerp_color_midpoint(self):
        c1 = (0, 0, 0)
        c2 = (200, 100, 50)
        result = NeoPixelManager._lerp_color(c1, c2, 0.5)
        assert result == (100, 50, 25)
