"""
Relay Controller - RS485/Modbus RTU interface to Waveshare 8-Ch Relay Module (B)

Hardware: Waveshare Industrial Modbus RTU 8-Ch Relay Module (B)
Connection: Pi USB → USB-to-RS485 adapter → 2-wire twisted pair → relay module
Protocol: Modbus RTU over RS485

Threading model: Modbus serial transactions are slow (9600 baud, blocking),
so UI widgets must never talk to the bus directly. A background poller
refreshes all 8 channel states in a single read_coils transaction and the
UI reads the cache via get_cached(). All bus I/O is serialized by _io_lock.
"""

import time
import threading

try:
    from pymodbus.client import ModbusSerialClient
    HAS_PYMODBUS = True
except ImportError:
    HAS_PYMODBUS = False

from relay.mock_relay import MockRelayController

# Default Modbus configuration for Waveshare module
DEFAULT_CONFIG = {
    'port': '/dev/ttyUSB0',
    'baudrate': 9600,
    'parity': 'N',
    'stopbits': 1,
    'bytesize': 8,
    'slave_address': 0x01,
    'timeout': 1,
}

# Default relay channel assignments
DEFAULT_CHANNELS = {
    1: {'name': 'AW-4 Solenoid A (1-2)', 'coil': 0x00, 'enabled': True},
    2: {'name': 'AW-4 Solenoid B (2-3)', 'coil': 0x01, 'enabled': True},
    3: {'name': 'TCC Lockup', 'coil': 0x02, 'enabled': True},
    4: {'name': 'Electric Fan Low', 'coil': 0x03, 'enabled': True},
    5: {'name': 'Electric Fan High', 'coil': 0x04, 'enabled': True},
    6: {'name': 'Light Bar 1', 'coil': 0x05, 'enabled': True},
    7: {'name': 'Light Bar 2', 'coil': 0x06, 'enabled': True},
    8: {'name': 'Spare', 'coil': 0x07, 'enabled': True},
}

# Minimum time between state changes per channel (seconds)
MIN_CYCLE_TIME = 1.0

# Background state poll interval (seconds)
POLL_INTERVAL = 0.25


class RelayController:
    """
    Controls Waveshare Modbus RTU 8-Ch Relay Module via RS485.

    Falls back to MockRelayController when pymodbus is not installed
    or when the RS485 adapter is not connected (desktop development).
    """

    def __init__(self, config=None, channels=None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.channels = {**DEFAULT_CHANNELS, **(channels or {})}
        self._client = None
        self._connected = False
        self._mock = False
        self._states = {ch: False for ch in range(1, 9)}
        self._last_change = {ch: 0.0 for ch in range(1, 9)}
        self._lock = threading.Lock()      # guards cycle-time bookkeeping
        self._io_lock = threading.Lock()   # serializes Modbus transactions
        self._poll_thread = None
        self._polling = False

    @property
    def connected(self):
        return self._connected

    @property
    def is_mock(self):
        return self._mock

    def connect(self):
        """Connect to the relay module. Falls back to mock on failure."""
        if not HAS_PYMODBUS:
            print("[RELAY] pymodbus not installed — using mock relay")
            self._use_mock()
            return True

        try:
            self._client = ModbusSerialClient(
                port=self.config['port'],
                baudrate=self.config['baudrate'],
                parity=self.config['parity'],
                stopbits=self.config['stopbits'],
                bytesize=self.config['bytesize'],
                timeout=self.config['timeout'],
            )
            if self._client.connect():
                self._connected = True
                self._mock = False
                print(f"[RELAY] Connected via RS485 on {self.config['port']}")
                self.all_off()
                self._start_poller()
                return True
            else:
                print(f"[RELAY] Failed to connect on {self.config['port']} — using mock")
                self._use_mock()
                return True
        except Exception as e:
            print(f"[RELAY] Connection error: {e} — using mock")
            self._use_mock()
            return True

    def _use_mock(self):
        """Fall back to mock relay controller."""
        self._client = MockRelayController()
        self._client.connect()
        self._connected = True
        self._mock = True

    def _start_poller(self):
        """Start the background state poller (real hardware only —
        mock reads are instant so the UI reads it directly)."""
        self._polling = True
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()

    def _stop_poller(self):
        self._polling = False
        if self._poll_thread:
            self._poll_thread.join(timeout=2)
            self._poll_thread = None

    def _poll_loop(self):
        """Refresh all channel states with one Modbus transaction per cycle."""
        while self._polling:
            try:
                self.get_all_states()
            except Exception as e:
                print(f"[RELAY] Poll error: {e}")
            time.sleep(POLL_INTERVAL)

    def disconnect(self):
        """Disconnect from relay module, turning all relays off first."""
        if self._connected:
            self._stop_poller()
            try:
                self.all_off()
            except Exception:
                pass
            if not self._mock and self._client:
                self._client.close()
            self._connected = False
            print("[RELAY] Disconnected")

    def set_relay(self, channel, state, force=False):
        """
        Set a relay channel on or off.

        Args:
            channel: Relay number 1-8
            state: True for ON, False for OFF
            force: Bypass the minimum cycle time (safety shutdowns only)

        Returns:
            True if successful, False otherwise
        """
        if channel not in self.channels:
            print(f"[RELAY] Invalid channel: {channel}")
            return False

        if not self.channels[channel]['enabled']:
            print(f"[RELAY] Channel {channel} is disabled")
            return False

        # Enforce minimum cycle time
        now = time.time()
        with self._lock:
            if not force and now - self._last_change[channel] < MIN_CYCLE_TIME:
                print(f"[RELAY] Channel {channel} cycle too fast, ignoring")
                return False
            self._last_change[channel] = now

        if self._mock:
            self._client.set_relay(channel, state)
            self._states[channel] = state
            return True

        try:
            coil = self.channels[channel]['coil']
            with self._io_lock:
                result = self._client.write_coil(
                    coil, state, slave=self.config['slave_address']
                )
            if result.isError():
                print(f"[RELAY] Write failed on CH{channel}: {result}")
                return False
            self._states[channel] = state
            name = self.channels[channel]['name']
            print(f"[RELAY] CH{channel} ({name}) = {'ON' if state else 'OFF'}")
            return True
        except Exception as e:
            print(f"[RELAY] Error setting CH{channel}: {e}")
            return False

    def get_cached(self, channel):
        """
        Read a channel state without touching the bus.

        This is what UI widgets should call — the background poller keeps
        the cache fresh. On mock, reads the mock directly (instant).
        """
        if self._mock and self._client:
            return self._client.get_relay(channel)
        return self._states.get(channel, False)

    def get_relay(self, channel):
        """Read the current state of a relay channel from the hardware.
        Blocking — do not call from the UI thread; use get_cached()."""
        if self._mock:
            return self._client.get_relay(channel)

        try:
            coil = self.channels[channel]['coil']
            with self._io_lock:
                result = self._client.read_coils(
                    coil, 1, slave=self.config['slave_address']
                )
            if not result.isError():
                self._states[channel] = result.bits[0]
                return result.bits[0]
        except Exception as e:
            print(f"[RELAY] Error reading CH{channel}: {e}")

        return self._states.get(channel, False)

    def get_all_states(self):
        """Read all relay states in one transaction. Returns dict {channel: bool}.
        Blocking on real hardware — the poller calls this; UI should use
        get_cached()."""
        if self._mock:
            return {ch: self._client.get_relay(ch) for ch in range(1, 9)}

        try:
            with self._io_lock:
                result = self._client.read_coils(
                    0x00, 8, slave=self.config['slave_address']
                )
            if not result.isError():
                for i in range(8):
                    self._states[i + 1] = result.bits[i]
        except Exception as e:
            print(f"[RELAY] Error reading all states: {e}")

        return dict(self._states)

    def all_off(self):
        """Turn all relays off (safety shutdown). Bypasses the minimum
        cycle time — a shutdown must never leave a channel energized."""
        for ch in range(1, 9):
            self.set_relay(ch, False, force=True)
        print("[RELAY] All channels OFF")

    def toggle(self, channel):
        """Toggle a relay channel."""
        current = self.get_cached(channel)
        return self.set_relay(channel, not current)
