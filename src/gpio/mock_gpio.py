"""
Mock GPIO - Simulates RPi.GPIO for development on desktop
"""


class MockGPIO:
    """
    Simulates Raspberry Pi GPIO for development without hardware
    """

    # GPIO modes
    BCM = "BCM"
    BOARD = "BOARD"

    # Pin modes
    IN = "IN"
    OUT = "OUT"

    # Pin states
    LOW = 0
    HIGH = 1

    # Pull up/down
    PUD_OFF = 0
    PUD_DOWN = 1
    PUD_UP = 2

    # Internal state tracking
    _mode = None
    _pin_modes = {}
    _pin_states = {}

    @classmethod
    def setmode(cls, mode):
        """Set GPIO numbering mode"""
        cls._mode = mode
        print(f"[MOCK GPIO] Set mode: {mode}")

    @classmethod
    def getmode(cls):
        """Get current GPIO numbering mode"""
        return cls._mode

    @classmethod
    def setup(cls, channel, mode, initial=LOW, pull_up_down=PUD_OFF):
        """Setup a GPIO pin"""
        cls._pin_modes[channel] = mode
        cls._pin_states[channel] = initial
        print(f"[MOCK GPIO] Setup pin {channel} as {mode} (initial={initial})")

    @classmethod
    def output(cls, channel, state):
        """Set GPIO pin output state"""
        if channel not in cls._pin_modes:
            print(f"[MOCK GPIO] ⚠️  Pin {channel} not setup!")
            return

        cls._pin_states[channel] = state
        state_str = "HIGH" if state else "LOW"
        print(f"[MOCK GPIO] Pin {channel} = {state_str}")

    @classmethod
    def input(cls, channel):
        """Read GPIO pin input state"""
        if channel not in cls._pin_modes:
            print(f"[MOCK GPIO] ⚠️  Pin {channel} not setup!")
            return cls.LOW

        return cls._pin_states.get(channel, cls.LOW)

    @classmethod
    def cleanup(cls, channel=None):
        """Cleanup GPIO pins"""
        if channel is None:
            print("[MOCK GPIO] Cleanup all pins")
            cls._pin_modes.clear()
            cls._pin_states.clear()
        else:
            print(f"[MOCK GPIO] Cleanup pin {channel}")
            cls._pin_modes.pop(channel, None)
            cls._pin_states.pop(channel, None)

    @classmethod
    def setwarnings(cls, enabled):
        """Enable/disable warnings"""
        print(f"[MOCK GPIO] Warnings: {enabled}")

    @classmethod
    def get_pin_state(cls, channel):
        """Get current pin state (for debugging)"""
        return {
            'mode': cls._pin_modes.get(channel),
            'state': cls._pin_states.get(channel)
        }

    @classmethod
    def get_all_states(cls):
        """Get all pin states (for debugging)"""
        return {
            'mode': cls._mode,
            'pins': {
                pin: {
                    'mode': cls._pin_modes.get(pin),
                    'state': cls._pin_states.get(pin)
                }
                for pin in cls._pin_modes.keys()
            }
        }


# Make it usable as drop-in replacement for RPi.GPIO
GPIO = MockGPIO
