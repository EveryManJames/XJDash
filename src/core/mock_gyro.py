"""
Mock Gyroscope - Simulates BNO055 IMU output for development
"""

import math
import random
import time


class MockGyro:
    """
    Simulates BNO055 gyroscope/IMU output for desktop development.
    Generates realistic pitch/roll values as if driving on terrain.
    """

    def __init__(self):
        self._pitch = 0.0  # degrees, nose up positive
        self._roll = 0.0   # degrees, right side down positive
        self._heading = 0.0
        self._sim_time = 0.0
        self._calibrated = True

    def read(self):
        """
        Read current pitch, roll, heading from simulated IMU.

        Returns:
            Tuple of (pitch, roll, heading) in degrees, or None if unavailable.
        """
        self._sim_time += 0.1

        # Simulate gentle off-road terrain movement
        # Slow sinusoidal base + random bumps
        self._pitch = (
            5.0 * math.sin(self._sim_time * 0.3)
            + 2.0 * math.sin(self._sim_time * 0.8)
            + random.uniform(-0.5, 0.5)
        )
        self._roll = (
            3.0 * math.sin(self._sim_time * 0.2 + 1.0)
            + 1.5 * math.sin(self._sim_time * 0.7)
            + random.uniform(-0.3, 0.3)
        )
        self._heading = (self._heading + random.uniform(-0.5, 0.5)) % 360

        return (self._pitch, self._roll, self._heading)

    @property
    def is_calibrated(self):
        return self._calibrated
