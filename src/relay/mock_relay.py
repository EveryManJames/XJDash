"""
Mock Relay Controller - Simulates Waveshare Modbus RTU relay for desktop development.

Drop-in replacement for the real Modbus relay connection.
Prints state changes to console for debugging.
"""


class MockRelayController:
    """Simulates Waveshare Modbus RTU 8-Ch Relay Module for development."""

    def __init__(self):
        self._states = {i: False for i in range(1, 9)}
        self._connected = False

    def connect(self):
        """Simulate connecting to relay module."""
        self._connected = True
        print("[MOCK RELAY] Connected (simulated)")
        return True

    def set_relay(self, channel, state):
        """Set a relay channel on or off."""
        if 1 <= channel <= 8:
            self._states[channel] = state
            state_str = "ON" if state else "OFF"
            print(f"[MOCK RELAY] CH{channel} = {state_str}")
            return True
        return False

    def get_relay(self, channel):
        """Read relay channel state."""
        return self._states.get(channel, False)

    def all_off(self):
        """Turn all relays off."""
        for ch in self._states:
            self._states[ch] = False
        print("[MOCK RELAY] All channels OFF")

    def get_all_states(self):
        """Get all relay states."""
        return dict(self._states)

    def close(self):
        """Simulate disconnect."""
        self._connected = False
        print("[MOCK RELAY] Disconnected")
