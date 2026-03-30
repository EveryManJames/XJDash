"""
Gyro Manager - Handles BNO055 9-DOF IMU for pitch/roll/heading

Hardware: Adafruit BNO055 Absolute Orientation Sensor
  - 9-DOF IMU with on-chip sensor fusion (Euler angles output)
  - Interface: I2C (SDA/SCL on Pi GPIO 2/3)
  - Address: 0x28 (default) or 0x29
  - Supply: 3.3V from Pi header
  - Product: Adafruit #2472 (BNO055 breakout)
  - Wiring: VIN→3.3V, GND→GND, SDA→GPIO2, SCL→GPIO3

Provides calibrated pitch and roll readings with a user-settable
zero-point offset (calibrate button sets current orientation as 0°).
"""

import json
import os
import threading
import time
from typing import Optional, Tuple

try:
    import board
    import adafruit_bno055
    BNO055_AVAILABLE = True
except ImportError:
    BNO055_AVAILABLE = False

from core.data_manager import DataManager
from core.mock_gyro import MockGyro

# Persistent calibration file alongside this source
_CALIBRATION_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'gyro_calibration.json'
)


class GyroManager:
    """
    Reads pitch/roll/heading from a BNO055 IMU and pushes values
    into DataManager.  Falls back to MockGyro on desktop.

    DataManager keys written:
        gyro_pitch   - degrees (positive = nose up)
        gyro_roll    - degrees (positive = right side down)
        gyro_heading - degrees (0-360 compass heading)
    """

    # Read rate (seconds between samples)
    READ_INTERVAL = 0.05  # 20 Hz

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

        self._sensor = None
        self._mock = False
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Calibration offsets (subtracted from raw readings)
        self._pitch_offset = 0.0
        self._roll_offset = 0.0
        self._lock = threading.Lock()

        # Load saved calibration
        self._load_calibration()

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self):
        """Initialize the BNO055 sensor or fall back to mock."""
        if BNO055_AVAILABLE:
            try:
                i2c = board.I2C()
                self._sensor = adafruit_bno055.BNO055_I2C(i2c)
                print("Connected to BNO055 IMU")
            except Exception as e:
                print(f"BNO055 init failed: {e}")
                print("Falling back to mock gyro data")
                self._sensor = MockGyro()
                self._mock = True
        else:
            print("BNO055 library not installed - using mock gyro data")
            self._sensor = MockGyro()
            self._mock = True

        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def disconnect(self):
        """Stop the read loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("Gyro disconnected")

    # ------------------------------------------------------------------
    # Calibration
    # ------------------------------------------------------------------

    def calibrate(self):
        """
        Set the current orientation as the zero reference.
        Saves offsets to disk so they persist across restarts.
        """
        raw = self._read_raw()
        if raw is None:
            return

        pitch_raw, roll_raw, _ = raw
        with self._lock:
            self._pitch_offset = pitch_raw
            self._roll_offset = roll_raw

        self._save_calibration()
        print(f"Gyro calibrated: pitch_offset={pitch_raw:.1f}, roll_offset={roll_raw:.1f}")

        # Push zeros immediately so UI updates
        self.data_manager.update('gyro_pitch', 0.0)
        self.data_manager.update('gyro_roll', 0.0)

    def reset_calibration(self):
        """Clear calibration offsets back to factory zero."""
        with self._lock:
            self._pitch_offset = 0.0
            self._roll_offset = 0.0
        self._save_calibration()
        print("Gyro calibration reset to factory zero")

    def _save_calibration(self):
        try:
            with open(_CALIBRATION_FILE, 'w') as f:
                json.dump({
                    'pitch_offset': self._pitch_offset,
                    'roll_offset': self._roll_offset,
                }, f)
        except OSError as e:
            print(f"Could not save gyro calibration: {e}")

    def _load_calibration(self):
        try:
            with open(_CALIBRATION_FILE, 'r') as f:
                data = json.load(f)
                self._pitch_offset = float(data.get('pitch_offset', 0.0))
                self._roll_offset = float(data.get('roll_offset', 0.0))
                print(f"Loaded gyro calibration: pitch={self._pitch_offset:.1f}, roll={self._roll_offset:.1f}")
        except (OSError, json.JSONDecodeError, ValueError):
            pass  # No saved calibration yet — use defaults

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def _read_raw(self) -> Optional[Tuple[float, float, float]]:
        """Read raw (pitch, roll, heading) from sensor or mock."""
        try:
            if self._mock:
                return self._sensor.read()
            else:
                euler = self._sensor.euler
                if euler is None or euler[0] is None:
                    return None
                # BNO055 euler: (heading, roll, pitch)
                heading, roll, pitch = euler
                return (pitch, roll, heading)
        except Exception as e:
            print(f"Gyro read error: {e}")
            return None

    def _read_loop(self):
        """Background thread that reads IMU data."""
        while self._running:
            raw = self._read_raw()
            if raw is not None:
                pitch_raw, roll_raw, heading = raw
                with self._lock:
                    pitch = pitch_raw - self._pitch_offset
                    roll = roll_raw - self._roll_offset

                self.data_manager.update('gyro_pitch', round(pitch, 1))
                self.data_manager.update('gyro_roll', round(roll, 1))
                self.data_manager.update('gyro_heading', round(heading, 1))

            time.sleep(self.READ_INTERVAL)
