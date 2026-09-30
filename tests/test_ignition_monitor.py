"""
Tests for IgnitionShutdownManager and PowerLatch
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.power_latch import PowerLatch
from core.ignition_monitor import IgnitionShutdownManager


@pytest.fixture
def latch():
    return PowerLatch()


# ---------------------------------------------------------------------------
# PowerLatch tests
# ---------------------------------------------------------------------------

class TestPowerLatch:
    def test_starts_disengaged(self, latch):
        assert latch.engaged is False

    def test_engage_sets_engaged(self, latch):
        latch.engage()
        assert latch.engaged is True
        latch.release()

    def test_release_clears_engaged(self, latch):
        latch.engage()
        latch.release()
        assert latch.engaged is False

    def test_double_release_no_error(self, latch):
        latch.engage()
        latch.release()
        latch.release()  # should not raise
        assert latch.engaged is False

    def test_mock_mode_on_desktop(self, latch):
        assert latch._mock is True

    def test_default_pin_is_27(self, latch):
        assert latch._pin == 27

    def test_custom_pin(self):
        latch = PowerLatch(gpio_pin=22)
        assert latch._pin == 22

    def test_custom_failsafe(self):
        latch = PowerLatch(failsafe_seconds=60.0)
        assert latch._failsafe_seconds == 60.0

    def test_failsafe_timer_starts_on_engage(self, latch):
        latch.engage()
        assert latch._failsafe_timer is not None
        latch.release()

    def test_failsafe_timer_cancelled_on_release(self, latch):
        latch.engage()
        latch.release()
        assert latch._failsafe_timer is None


# ---------------------------------------------------------------------------
# IgnitionShutdownManager tests
# ---------------------------------------------------------------------------

class TestIgnitionMonitorDesktop:
    """Tests that run on desktop (no RPi.GPIO)."""

    def test_starts_in_mock_mode(self, latch):
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: None,
            power_latch=latch,
            enable_halt=False,
        )
        assert monitor._mock is True

    def test_start_stop_no_error(self, latch):
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: None,
            power_latch=latch,
            enable_halt=False,
        )
        monitor.start()
        monitor.stop()

    def test_cleanup_callback_called_on_shutdown(self, latch):
        called = []
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: called.append(True),
            power_latch=latch,
            enable_halt=False,
        )
        monitor._initiate_shutdown()
        assert len(called) == 1

    def test_shutdown_only_runs_once(self, latch):
        called = []
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: called.append(True),
            power_latch=latch,
            enable_halt=False,
        )
        monitor._initiate_shutdown()
        monitor._initiate_shutdown()
        assert len(called) == 1

    def test_power_latch_released_on_shutdown(self, latch):
        latch.engage()
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: None,
            power_latch=latch,
            enable_halt=False,
        )
        monitor._initiate_shutdown()
        assert latch.engaged is False

    def test_default_pin_is_17(self, latch):
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: None,
            power_latch=latch,
        )
        assert monitor._pin == 17

    def test_custom_pin(self, latch):
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: None,
            power_latch=latch,
            gpio_pin=22,
        )
        assert monitor._pin == 22

    def test_custom_debounce(self, latch):
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: None,
            power_latch=latch,
            debounce_seconds=5.0,
        )
        assert monitor._debounce == 5.0
