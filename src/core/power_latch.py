"""
Power Latch Controller - GPIO self-hold for Pi power management

Implements a self-latching power circuit so the Pi can hold its own 12V
supply on after the ignition key is turned off, then cut its own power
once shutdown is complete.  This eliminates parasitic draw from the buck
converter when the vehicle is off.

Hardware: Standard 12V automotive relay (Bosch-style 5-pin SPDT) + 2N2222
          NPN transistor + 1N4007 flyback diode + 1kΩ resistor.

Wiring diagram:

    Constant 12V ─────────────────────┬──── Relay pin 30 (common)
                                      │
                        ┌─────────────┘
                        │
              Relay pin 86 (coil +)
                        │
              Relay pin 85 (coil −) ──┬──── 2N2222 collector
                        │             │
              [ 1N4007 flyback        │     (diode band toward pin 86)
                across 85-86 ]        │
                                      │
                              2N2222 emitter ──── GND
                                      │
                              2N2222 base ── [ 1kΩ ] ── GPIO27 (Pi)

    Relay pin 87 (NO) ──── Buck converter VIN ──── Pi 5V
    Relay pin 87a (NC) ──── (unused)

    Ignition sense (separate, existing):
        Switched 12V ──[ 10kΩ ]──┬── GPIO17
                                 │
                               [ 4.7kΩ ]
                                 │
                                GND

    Ignition also drives the relay coil through a second path
    (diode-OR'd with the transistor) so that turning the key ON
    initially energizes the relay before the Pi has booted:

        Switched 12V ──[ 1N4007 ]──── Relay pin 85
                        (anode toward 12V, cathode toward pin 85)

    This means EITHER the ignition wire OR the Pi GPIO can hold
    the relay on.  Both must be off to drop power.

Sequence:
    1. Key ON  → ignition energizes relay → buck gets 12V → Pi boots
    2. Pi boots → PowerLatch.engage() sets GPIO27 HIGH → self-hold
    3. Key OFF → ignition drops, but GPIO27 still holds relay
    4. Pi detects key-off → runs cleanup → PowerLatch.release()
    5. GPIO27 goes LOW → relay drops → buck loses 12V → zero draw

Failsafe:
    If the Pi hangs and never calls release(), a watchdog timer
    (default 45s) will force-release the pin so the battery is
    not drained.
"""

import threading
import time
from typing import Optional

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


# Default GPIO pin for the keep-alive / self-hold latch (BCM numbering)
DEFAULT_LATCH_PIN = 27

# If the Pi never explicitly releases, force-release after this many seconds
# to prevent battery drain in case of a hang/crash
DEFAULT_FAILSAFE_SECONDS = 45.0


class PowerLatch:
    """
    Controls a GPIO pin that holds a relay coil energized, keeping the
    buck converter powered.  Call engage() on boot, release() after
    shutdown cleanup is done.
    """

    def __init__(
        self,
        gpio_pin: int = DEFAULT_LATCH_PIN,
        failsafe_seconds: float = DEFAULT_FAILSAFE_SECONDS,
    ):
        """
        Args:
            gpio_pin: BCM pin number driving the 2N2222 base (via 1kΩ).
            failsafe_seconds: Max time the latch stays engaged after
                              engage() is called.  Guards against hangs.
        """
        self._pin = gpio_pin
        self._failsafe_seconds = failsafe_seconds
        self._mock = not GPIO_AVAILABLE
        self._engaged = False
        self._failsafe_timer: Optional[threading.Timer] = None

    @property
    def engaged(self):
        return self._engaged

    def engage(self):
        """
        Assert the keep-alive pin HIGH so the relay stays latched
        even after the ignition key is turned off.  Call this early
        in the boot sequence.
        """
        if self._mock:
            self._engaged = True
            print("[PWR] Power latch engaged (mock — no GPIO)")
        else:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.OUT)
            GPIO.output(self._pin, GPIO.HIGH)
            self._engaged = True
            print(f"[PWR] Power latch engaged on GPIO{self._pin}")

        # Start failsafe timer (runs in mock mode too — it's a software safety net)
        self._start_failsafe()

    def release(self):
        """
        Release the keep-alive pin (LOW).  If the ignition is also off,
        the relay will drop and the buck converter loses power.
        This is the last thing called before OS halt.
        """
        self._cancel_failsafe()

        if self._mock:
            self._engaged = False
            print("[PWR] Power latch released (mock — no GPIO)")
            return

        if self._engaged:
            GPIO.output(self._pin, GPIO.LOW)
            self._engaged = False
            print(f"[PWR] Power latch released on GPIO{self._pin} — relay will drop")
            try:
                GPIO.cleanup(self._pin)
            except Exception:
                pass

    def _start_failsafe(self):
        """Start the failsafe timer that force-releases if we hang."""
        self._cancel_failsafe()
        self._failsafe_timer = threading.Timer(
            self._failsafe_seconds, self._failsafe_release
        )
        self._failsafe_timer.daemon = True
        self._failsafe_timer.start()
        print(f"[PWR] Failsafe timer set: {self._failsafe_seconds}s")

    def _cancel_failsafe(self):
        """Cancel the failsafe timer (normal shutdown path)."""
        if self._failsafe_timer is not None:
            self._failsafe_timer.cancel()
            self._failsafe_timer = None

    def _failsafe_release(self):
        """Called by timer if release() was never called."""
        print("[PWR] FAILSAFE: Pi did not shut down in time — forcing latch release")
        self.release()
