"""
Serial Manager - Handles communication with Renix Engine Monitor
"""

import threading
import time
from typing import Optional

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("⚠️  pyserial not installed - using mock serial data")

from core.data_manager import DataManager
from core.mock_serial import MockREMSerial


class SerialManager:
    """
    Manages serial connection to REM and parses incoming data
    """

    # REM Normal mode field order
    FIELD_NAMES = [
        'timestamp', 'MAP', 'VAC', 'CTS', 'IAT', 'RPM', 'Batt', 'o2',
        'exhaust', 'o2_Heater', 'Loop', 'EGR', 'TPS', 'TPS_mode',
        'IGN', 'Knock', 'INJ_ms', 'INJ_DC', 'Sync', 'STFT', 'LTFT',
        'AC_SW', 'AC_REQ', 'GPH', 'AFR'
    ]

    def __init__(self, data_manager: DataManager,
                 port: str = '/dev/ttyACM0',
                 baud: int = 115200):
        """
        Initialize serial manager

        Args:
            data_manager: Central data store
            port: Serial port (e.g., '/dev/ttyACM0', 'COM4')
            baud: Baud rate (default: 115200 for REM)
        """
        self.data_manager = data_manager
        self.port = port
        self.baud = baud

        self.serial = None
        self.connected = False
        self.running = False
        self.thread = None

        # Use mock serial if real serial not available
        self.use_mock = not SERIAL_AVAILABLE

    def connect(self):
        """Establish serial connection"""
        if self.connected:
            print("⚠️  Already connected")
            return

        if self.use_mock:
            print("🔧 Using mock REM data for development")
            self.serial = MockREMSerial()
            self.connected = True
        else:
            try:
                self.serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baud,
                    timeout=1
                )
                self.connected = True
                print(f"✅ Connected to REM on {self.port}")
            except Exception as e:
                print(f"❌ Failed to connect to REM: {e}")
                print("🔧 Falling back to mock data")
                self.serial = MockREMSerial()
                self.connected = True
                self.use_mock = True

        # Start reading thread
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def disconnect(self):
        """Close serial connection"""
        self.running = False

        if self.thread:
            self.thread.join(timeout=2)

        if self.serial and not self.use_mock:
            self.serial.close()

        self.connected = False
        print("🔌 Disconnected from REM")

    def _read_loop(self):
        """Background thread that reads serial data"""
        # Measured line rate, published as '_rem_hz' for diagnostics
        rate_count = 0
        rate_window_start = time.time()

        while self.running:
            try:
                if self.use_mock:
                    # Mock serial returns formatted line
                    line = self.serial.read_line()
                else:
                    # Real serial
                    if self.serial.in_waiting:
                        line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    else:
                        time.sleep(0.01)
                        continue

                # Parse and update data
                data = self._parse_line(line)
                if data:
                    for key, value in data.items():
                        self.data_manager.update(key, value)

                    rate_count += 1
                    now = time.time()
                    elapsed = now - rate_window_start
                    if elapsed >= 1.0:
                        self.data_manager.update('_rem_hz', rate_count / elapsed)
                        rate_count = 0
                        rate_window_start = now

            except Exception as e:
                print(f"⚠️  Serial read error: {e}")
                time.sleep(0.5)

    def _parse_line(self, line: str) -> Optional[dict]:
        """
        Parse REM Normal mode output line

        Args:
            line: Space-delimited REM data

        Returns:
            Dictionary of parsed values or None if invalid
        """
        try:
            values = line.strip().split()

            if len(values) != len(self.FIELD_NAMES):
                return None

            data = {}
            for i, field in enumerate(self.FIELD_NAMES):
                # String fields
                if field in ['exhaust', 'Loop', 'EGR', 'TPS_mode', 'AC_SW', 'AC_REQ', 'Sync']:
                    data[field] = values[i]
                # Numeric fields
                else:
                    try:
                        data[field] = float(values[i])
                    except ValueError:
                        data[field] = 0

            return data

        except Exception as e:
            print(f"⚠️  Parse error: {e}")
            return None
