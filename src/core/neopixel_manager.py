"""
NeoPixel Manager - WS2812B RGB LED strip control for interior mood lighting

Hardware: WS2812B (NeoPixel) LED strip
  - Data pin: GPIO18 (PWM0, Pi pin 12)
  - Power: 5V from a separate 5V supply or the buck converter
           (do NOT power long strips from the Pi 5V header —
            use the buck converter output directly)
  - Ground: shared with Pi GND
  - One 300-470Ω resistor inline on the data line (close to the first LED)
  - One 1000µF capacitor across the strip's 5V/GND (prevents inrush damage)

Wiring:
    GPIO18 (pin 12) ──[330Ω]── NeoPixel Data In
    Buck 5V output  ────────── NeoPixel 5V
    GND (shared)    ────────── NeoPixel GND

Library: rpi_ws281x (requires root on Pi for PWM DMA access)

Modes:
    solid          - Static single color
    breathe        - Gentle pulse (fade in/out)
    rainbow        - Rotating rainbow cycle
    temp_reactive  - Color shifts with coolant temperature (via DataManager)
"""

import json
import math
import os
import threading
import time
from typing import Optional, Tuple

try:
    from rpi_ws281x import PixelStrip, Color
    NEOPIXEL_AVAILABLE = True
except ImportError:
    NEOPIXEL_AVAILABLE = False

from core.data_manager import DataManager
from core.mock_neopixel import MockPixelStrip

_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'neopixel_config.json'
)


def _color_int(r, g, b):
    """Pack RGB into a 24-bit integer (GRB order handled by library)."""
    return (int(r) << 16) | (int(g) << 8) | int(b)


class NeoPixelManager:
    """
    Controls a WS2812B LED strip.  Runs an animation loop in a background
    thread and exposes simple methods for the UI to call.

    DataManager keys written:
        neopixel_preset     - name of the active preset
        neopixel_brightness - current brightness 0-255
        neopixel_mode       - current mode string
    """

    FRAME_INTERVAL = 0.03  # ~33 fps for smooth animations

    def __init__(self, data_manager: DataManager, config_path: str = _CONFIG_FILE):
        self.data_manager = data_manager
        self._config = self._load_config(config_path)

        self._strip = None
        self._mock = False
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Current state
        self._mode = 'solid'
        self._color: Tuple[int, int, int] = (0, 0, 0)
        self._brightness = self._config.get('default_brightness', 128)
        self._speed = 1.0
        self._preset_name = 'off'

        # Extra params for temp_reactive mode
        self._cool_color = (0, 100, 255)
        self._warm_color = (255, 140, 0)
        self._hot_color = (255, 0, 0)
        self._cool_temp = 180
        self._hot_temp = 230

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    @staticmethod
    def _load_config(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[NEOPIXEL] Could not load config: {e}")
            return {
                'gpio_pin': 18, 'num_leds': 30,
                'max_brightness': 255, 'default_brightness': 128,
                'dma_channel': 10, 'frequency': 800000, 'invert': False,
                'presets': {},
            }

    def get_presets(self):
        """Return the presets dict from config (for UI to list)."""
        return dict(self._config.get('presets', {}))

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self):
        """Initialize the LED strip or fall back to mock."""
        pin = self._config.get('gpio_pin', 18)
        num = self._config.get('num_leds', 30)
        freq = self._config.get('frequency', 800000)
        dma = self._config.get('dma_channel', 10)
        invert = self._config.get('invert', False)
        brightness = self._config.get('default_brightness', 128)

        if NEOPIXEL_AVAILABLE:
            try:
                self._strip = PixelStrip(
                    num, pin, freq, dma, invert, brightness,
                )
                self._strip.begin()
                self._mock = False
                print(f"[NEOPIXEL] Initialized {num} LEDs on GPIO{pin}")
            except Exception as e:
                print(f"[NEOPIXEL] Init failed: {e}")
                print("[NEOPIXEL] Falling back to mock")
                self._strip = MockPixelStrip(num, pin, brightness=brightness)
                self._strip.begin()
                self._mock = True
        else:
            print("[NEOPIXEL] rpi_ws281x not installed — using mock")
            self._strip = MockPixelStrip(num, pin, brightness=brightness)
            self._strip.begin()
            self._mock = True

        # Apply default preset
        default = self._config.get('default_preset', 'off')
        self.apply_preset(default)

        # Start animation thread
        self._running = True
        self._thread = threading.Thread(target=self._animation_loop, daemon=True)
        self._thread.start()

    def disconnect(self):
        """Turn off all LEDs and stop the animation thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self._strip:
            self._fill(0, 0, 0)
            self._strip.show()
        print("[NEOPIXEL] Disconnected — LEDs off")

    # ------------------------------------------------------------------
    # Public controls (called from UI)
    # ------------------------------------------------------------------

    def apply_preset(self, preset_name: str):
        """Apply a named preset from config."""
        presets = self._config.get('presets', {})
        if preset_name not in presets:
            print(f"[NEOPIXEL] Unknown preset: {preset_name}")
            return

        p = presets[preset_name]
        with self._lock:
            self._preset_name = preset_name
            self._mode = p.get('mode', 'solid')
            self._color = tuple(p.get('color', [0, 0, 0]))
            self._brightness = p.get('brightness', self._config.get('default_brightness', 128))
            self._speed = p.get('speed', 1.0)

            # Temp reactive params
            self._cool_color = tuple(p.get('cool_color', (0, 100, 255)))
            self._warm_color = tuple(p.get('warm_color', (255, 140, 0)))
            self._hot_color = tuple(p.get('hot_color', (255, 0, 0)))
            self._cool_temp = p.get('cool_temp', 180)
            self._hot_temp = p.get('hot_temp', 230)

        if self._strip:
            self._strip.setBrightness(self._brightness)

        # Publish to DataManager so UI can reflect state
        self.data_manager.update('neopixel_preset', preset_name)
        self.data_manager.update('neopixel_brightness', self._brightness)
        self.data_manager.update('neopixel_mode', self._mode)
        print(f"[NEOPIXEL] Preset: {preset_name} ({self._mode})")

    def set_color(self, r: int, g: int, b: int):
        """Set a custom solid color (overrides preset)."""
        with self._lock:
            self._mode = 'solid'
            self._color = (r, g, b)
            self._preset_name = 'custom'
        self.data_manager.update('neopixel_preset', 'custom')
        self.data_manager.update('neopixel_mode', 'solid')

    def set_brightness(self, brightness: int):
        """Set brightness (0-255)."""
        max_b = self._config.get('max_brightness', 255)
        brightness = max(0, min(max_b, brightness))
        with self._lock:
            self._brightness = brightness
        if self._strip:
            self._strip.setBrightness(brightness)
        self.data_manager.update('neopixel_brightness', brightness)

    def off(self):
        """Turn LEDs off."""
        self.apply_preset('off')

    # ------------------------------------------------------------------
    # Animation loop
    # ------------------------------------------------------------------

    def _animation_loop(self):
        """Background thread running the current lighting mode."""
        t = 0.0
        while self._running:
            with self._lock:
                mode = self._mode
                color = self._color
                speed = self._speed
                brightness = self._brightness

            if mode == 'solid':
                self._render_solid(color)
            elif mode == 'breathe':
                self._render_breathe(color, speed, t)
            elif mode == 'rainbow':
                self._render_rainbow(speed, t)
            elif mode == 'temp_reactive':
                self._render_temp_reactive()
            else:
                self._render_solid(color)

            if self._strip:
                self._strip.show()

            t += self.FRAME_INTERVAL
            time.sleep(self.FRAME_INTERVAL)

    # ------------------------------------------------------------------
    # Render modes
    # ------------------------------------------------------------------

    def _fill(self, r, g, b):
        """Set all pixels to one color."""
        c = _color_int(r, g, b)
        for i in range(self._strip.numPixels()):
            self._strip.setPixelColor(i, c)

    def _render_solid(self, color):
        self._fill(*color)

    def _render_breathe(self, color, speed, t):
        # Sinusoidal brightness pulse
        factor = (math.sin(t * speed * math.pi) + 1.0) / 2.0  # 0.0 – 1.0
        r = int(color[0] * factor)
        g = int(color[1] * factor)
        b = int(color[2] * factor)
        self._fill(r, g, b)

    def _render_rainbow(self, speed, t):
        num = self._strip.numPixels()
        for i in range(num):
            hue = ((i / num) + t * speed * 0.1) % 1.0
            r, g, b = self._hsv_to_rgb(hue, 1.0, 1.0)
            self._strip.setPixelColor(i, _color_int(r, g, b))

    def _render_temp_reactive(self):
        cts = self.data_manager.get('CTS', 180)
        try:
            cts = float(cts)
        except (TypeError, ValueError):
            cts = 180.0

        with self._lock:
            cool_c = self._cool_color
            warm_c = self._warm_color
            hot_c = self._hot_color
            cool_t = self._cool_temp
            hot_t = self._hot_temp

        mid_t = (cool_t + hot_t) / 2.0

        if cts <= cool_t:
            color = cool_c
        elif cts >= hot_t:
            color = hot_c
        elif cts < mid_t:
            f = (cts - cool_t) / (mid_t - cool_t)
            color = self._lerp_color(cool_c, warm_c, f)
        else:
            f = (cts - mid_t) / (hot_t - mid_t)
            color = self._lerp_color(warm_c, hot_c, f)

        self._fill(*color)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _lerp_color(c1, c2, f):
        f = max(0.0, min(1.0, f))
        return (
            int(c1[0] + (c2[0] - c1[0]) * f),
            int(c1[1] + (c2[1] - c1[1]) * f),
            int(c1[2] + (c2[2] - c1[2]) * f),
        )

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        """Convert HSV (0-1 range) to RGB (0-255 range)."""
        if s == 0.0:
            val = int(v * 255)
            return val, val, val
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = int(255 * v * (1.0 - s))
        q = int(255 * v * (1.0 - s * f))
        t = int(255 * v * (1.0 - s * (1.0 - f)))
        val = int(v * 255)
        i %= 6
        if i == 0: return val, t, p
        if i == 1: return q, val, p
        if i == 2: return p, val, t
        if i == 3: return p, q, val
        if i == 4: return t, p, val
        return val, p, q
