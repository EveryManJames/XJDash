"""
Mock NeoPixel - Simulates WS2812B LED strip for desktop development
"""


class MockPixelStrip:
    """
    Simulates the rpi_ws281x PixelStrip interface for desktop development.
    Prints state changes to console.
    """

    def __init__(self, num_leds, pin, **kwargs):
        self._num = num_leds
        self._pin = pin
        self._pixels = [(0, 0, 0)] * num_leds
        self._brightness = kwargs.get('brightness', 255)

    def begin(self):
        print(f"[NEOPIXEL MOCK] Initialized {self._num} LEDs on GPIO{self._pin}")

    def show(self):
        pass  # No-op in mock

    def setPixelColor(self, n, color):
        if 0 <= n < self._num:
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            self._pixels[n] = (r, g, b)

    def setPixelColorRGB(self, n, r, g, b):
        if 0 <= n < self._num:
            self._pixels[n] = (r, g, b)

    def getPixelColor(self, n):
        if 0 <= n < self._num:
            r, g, b = self._pixels[n]
            return (r << 16) | (g << 8) | b
        return 0

    def numPixels(self):
        return self._num

    def setBrightness(self, brightness):
        self._brightness = max(0, min(255, brightness))

    def getBrightness(self):
        return self._brightness
