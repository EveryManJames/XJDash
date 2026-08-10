"""Shared test setup: make src/ importable and give tests the repo root."""
import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, 'src'))


@pytest.fixture
def repo_root():
    return REPO_ROOT


@pytest.fixture
def fresh_data_manager():
    """DataManager is a singleton — hand tests a cleaned instance."""
    from core.data_manager import DataManager
    dm = DataManager()
    dm._data.clear()
    dm._timestamps.clear()
    dm._callbacks.clear()
    yield dm
    dm._data.clear()
    dm._timestamps.clear()
    dm._callbacks.clear()
