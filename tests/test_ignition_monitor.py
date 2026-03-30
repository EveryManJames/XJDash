"""
Tests for IgnitionShutdownManager
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.ignition_monitor import IgnitionShutdownManager


class TestIgnitionMonitorDesktop:
    """Tests that run on desktop (no RPi.GPIO)."""

    def test_starts_in_mock_mode(self):
        called = []
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: called.append(True),
            enable_halt=False,
        )
        assert monitor._mock is True

    def test_start_stop_no_error(self):
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: None,
            enable_halt=False,
        )
        monitor.start()  # should print desktop mode message, not crash
        monitor.stop()

    def test_cleanup_callback_called_on_shutdown(self):
        called = []
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: called.append(True),
            enable_halt=False,
        )
        # Directly call the internal shutdown method
        monitor._initiate_shutdown()
        assert len(called) == 1

    def test_shutdown_only_runs_once(self):
        called = []
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: called.append(True),
            enable_halt=False,
        )
        monitor._initiate_shutdown()
        monitor._initiate_shutdown()
        # _shutdown_initiated flag prevents double cleanup
        assert len(called) == 1

    def test_default_pin_is_17(self):
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: None,
        )
        assert monitor._pin == 17

    def test_custom_pin(self):
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: None,
            gpio_pin=27,
        )
        assert monitor._pin == 27

    def test_custom_debounce(self):
        monitor = IgnitionShutdownManager(
            cleanup_callback=lambda: None,
            debounce_seconds=5.0,
        )
        assert monitor._debounce == 5.0
