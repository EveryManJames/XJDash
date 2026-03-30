"""
Ignition Shutdown Manager - Monitors switched 12V ignition line via GPIO

Detects when the ignition key is turned off (GPIO pin goes LOW) and triggers
a graceful shutdown sequence: relays off → app cleanup → OS halt.

Hardware wiring:
    Switched 12V (IGN wire) ──[ 10kΩ ]──┬── GPIO pin (default GPIO17, pin 11)
                                         │
                                       [ 4.7kΩ ]
                                         │
                                        GND

    Optional: 100nF ceramic cap across the 4.7kΩ resistor to filter
    ignition noise.

    This voltage divider brings 12V → ~3.1V (safe for Pi 3.3V GPIO).
    When ignition is ON:  GPIO reads HIGH
    When ignition is OFF: GPIO reads LOW

The manager debounces the signal (default 3 seconds) to avoid false
triggers from momentary voltage dips during cranking.
"""

import os
import threading
import time
from typing import Callable, Optional

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


# Default GPIO pin for ignition sense (BCM numbering)
DEFAULT_IGN_PIN = 17

# How long the pin must stay LOW before we consider ignition truly off
DEFAULT_DEBOUNCE_SECONDS = 3.0

# After cleanup, wait this long before issuing halt (lets logs flush)
HALT_DELAY_SECONDS = 2.0


class IgnitionShutdownManager:
    """
    Monitors a GPIO pin connected to the switched 12V ignition line.
    When the pin goes LOW for longer than the debounce period, runs
    a cleanup callback and then halts the Pi.
    """

    def __init__(
        self,
        cleanup_callback: Callable[[], None],
        gpio_pin: int = DEFAULT_IGN_PIN,
        debounce_seconds: float = DEFAULT_DEBOUNCE_SECONDS,
        enable_halt: bool = True,
    ):
        """
        Args:
            cleanup_callback: Called before OS halt (should do relays-off,
                              serial disconnect, data manager close, etc.)
            gpio_pin: BCM pin number connected to ignition sense divider
            debounce_seconds: Ignition must be off this long before shutdown
            enable_halt: If True, issue 'sudo shutdown -h now' after cleanup.
                         Set False for desktop development / testing.
        """
        self._cleanup = cleanup_callback
        self._pin = gpio_pin
        self._debounce = debounce_seconds
        self._enable_halt = enable_halt

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._mock = not GPIO_AVAILABLE
        self._shutdown_initiated = False

    def start(self):
        """Begin monitoring the ignition sense pin."""
        if self._mock:
            print("[IGN] RPi.GPIO not available — ignition monitor disabled (desktop mode)")
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print(f"[IGN] Monitoring ignition on GPIO{self._pin} (debounce={self._debounce}s)")

    def stop(self):
        """Stop monitoring (called during normal app exit)."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if not self._mock:
            try:
                GPIO.cleanup(self._pin)
            except Exception:
                pass
        print("[IGN] Ignition monitor stopped")

    def _monitor_loop(self):
        """Poll the ignition pin, debounce, and trigger shutdown."""
        low_since = None

        while self._running:
            pin_state = GPIO.input(self._pin)

            if pin_state == GPIO.HIGH:
                # Ignition is on — reset timer
                low_since = None
            else:
                # Ignition is off
                if low_since is None:
                    low_since = time.monotonic()
                elif (time.monotonic() - low_since) >= self._debounce:
                    if not self._shutdown_initiated:
                        self._initiate_shutdown()
                    return

            time.sleep(0.25)

    def _initiate_shutdown(self):
        """Run cleanup and halt the Pi."""
        if self._shutdown_initiated:
            return
        self._shutdown_initiated = True
        print("[IGN] Ignition OFF detected — initiating graceful shutdown")

        # Run the app's cleanup (relays off, serial close, etc.)
        try:
            self._cleanup()
        except Exception as e:
            print(f"[IGN] Cleanup error: {e}")

        if self._enable_halt:
            print(f"[IGN] Halting system in {HALT_DELAY_SECONDS}s...")
            time.sleep(HALT_DELAY_SECONDS)
            os.system('sudo shutdown -h now')
        else:
            print("[IGN] Halt disabled (dev mode) — shutdown sequence complete")
