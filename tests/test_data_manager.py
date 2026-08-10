"""Tests for the DataManager singleton store."""
import time

from core.data_manager import DataManager


def test_singleton():
    assert DataManager() is DataManager()


def test_update_and_get(fresh_data_manager):
    dm = fresh_data_manager
    dm.update('RPM', 750)
    assert dm.get('RPM') == 750
    assert dm.get('missing', 'default') == 'default'


def test_age_tracks_updates(fresh_data_manager):
    dm = fresh_data_manager
    assert dm.age('RPM') is None
    dm.update('RPM', 750)
    age = dm.age('RPM')
    assert age is not None and age < 1.0

    # Age grows without new updates
    time.sleep(0.05)
    assert dm.age('RPM') >= 0.05


def test_callbacks_fire_on_change(fresh_data_manager):
    dm = fresh_data_manager
    calls = []
    dm.subscribe('CTS', lambda k, new, old: calls.append((k, new, old)))

    dm.update('CTS', 195)
    dm.update('CTS', 195)  # unchanged — no callback
    dm.update('CTS', 210)

    assert calls == [('CTS', 195, None), ('CTS', 210, 195)]
