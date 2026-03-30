"""
Tests for GyroManager and MockGyro
"""

import json
import os
import sys
import time

import pytest

# Ensure src is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.data_manager import DataManager
from core.mock_gyro import MockGyro
from core.gyro_manager import GyroManager, _CALIBRATION_FILE


@pytest.fixture(autouse=True)
def reset_data_manager():
    """Reset the DataManager singleton between tests."""
    dm = DataManager()
    dm.close()
    dm.initialized = False
    dm.__init__()
    yield dm
    dm.close()


@pytest.fixture
def clean_calibration():
    """Remove calibration file before/after test."""
    if os.path.exists(_CALIBRATION_FILE):
        os.remove(_CALIBRATION_FILE)
    yield
    if os.path.exists(_CALIBRATION_FILE):
        os.remove(_CALIBRATION_FILE)


class TestMockGyro:
    def test_read_returns_tuple(self):
        gyro = MockGyro()
        result = gyro.read()
        assert result is not None
        assert len(result) == 3

    def test_read_returns_floats(self):
        gyro = MockGyro()
        pitch, roll, heading = gyro.read()
        assert isinstance(pitch, float)
        assert isinstance(roll, float)
        assert isinstance(heading, float)

    def test_pitch_roll_in_range(self):
        gyro = MockGyro()
        for _ in range(100):
            pitch, roll, heading = gyro.read()
            assert -20 < pitch < 20
            assert -15 < roll < 15

    def test_heading_in_range(self):
        gyro = MockGyro()
        for _ in range(100):
            _, _, heading = gyro.read()
            assert 0 <= heading < 360

    def test_is_calibrated(self):
        gyro = MockGyro()
        assert gyro.is_calibrated is True


class TestGyroManager:
    def test_connect_uses_mock(self, reset_data_manager):
        gm = GyroManager(reset_data_manager)
        gm.connect()
        assert gm._mock is True
        assert gm._running is True
        gm.disconnect()

    def test_pushes_data_to_data_manager(self, reset_data_manager):
        gm = GyroManager(reset_data_manager)
        gm.connect()
        # Give the read loop time to push at least one sample
        time.sleep(0.2)
        gm.disconnect()

        pitch = reset_data_manager.get('gyro_pitch')
        roll = reset_data_manager.get('gyro_roll')
        heading = reset_data_manager.get('gyro_heading')

        assert pitch is not None
        assert roll is not None
        assert heading is not None

    def test_calibrate_zeros_readings(self, reset_data_manager, clean_calibration):
        gm = GyroManager(reset_data_manager)
        gm.connect()
        time.sleep(0.2)

        gm.calibrate()

        # After calibration, next readings should be near zero
        time.sleep(0.2)
        pitch = reset_data_manager.get('gyro_pitch')
        roll = reset_data_manager.get('gyro_roll')
        # Within a few degrees of zero (mock data drifts slightly)
        assert abs(pitch) < 5.0
        assert abs(roll) < 5.0
        gm.disconnect()

    def test_calibration_persists(self, reset_data_manager, clean_calibration):
        gm = GyroManager(reset_data_manager)
        gm.connect()
        time.sleep(0.2)
        gm.calibrate()
        gm.disconnect()

        assert os.path.exists(_CALIBRATION_FILE)
        with open(_CALIBRATION_FILE) as f:
            data = json.load(f)
        assert 'pitch_offset' in data
        assert 'roll_offset' in data

    def test_reset_calibration(self, reset_data_manager, clean_calibration):
        gm = GyroManager(reset_data_manager)
        gm.connect()
        time.sleep(0.2)
        gm.calibrate()
        assert gm._pitch_offset != 0.0 or gm._roll_offset != 0.0

        gm.reset_calibration()
        assert gm._pitch_offset == 0.0
        assert gm._roll_offset == 0.0
        gm.disconnect()

    def test_disconnect_stops_thread(self, reset_data_manager):
        gm = GyroManager(reset_data_manager)
        gm.connect()
        assert gm._running is True
        gm.disconnect()
        assert gm._running is False
