"""
Data Manager - Central data store for XJDash
Singleton pattern to share data between components
"""

import threading
import time
from typing import Dict, Any, Optional, Callable


class DataManager:
    """
    Thread-safe central data store for all REM and GPIO data
    Uses singleton pattern
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._data = {}
            self._timestamps = {}
            self._callbacks = {}
            self._data_lock = threading.Lock()
            self.initialized = True

    def update(self, key: str, value: Any):
        """
        Update a data value and notify subscribers

        Args:
            key: Data key (e.g., 'RPM', 'CTS', 'relay_1_state')
            value: New value
        """
        with self._data_lock:
            old_value = self._data.get(key)
            self._data[key] = value
            self._timestamps[key] = time.time()

            # Trigger callbacks if value changed
            if old_value != value and key in self._callbacks:
                for callback in self._callbacks[key]:
                    try:
                        callback(key, value, old_value)
                    except Exception as e:
                        print(f"Error in callback for {key}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a data value

        Args:
            key: Data key
            default: Default value if key doesn't exist

        Returns:
            Current value or default
        """
        with self._data_lock:
            return self._data.get(key, default)

    def subscribe(self, key: str, callback: Callable):
        """
        Subscribe to data changes

        Args:
            key: Data key to watch
            callback: Function to call on change (signature: func(key, new_value, old_value))
        """
        if key not in self._callbacks:
            self._callbacks[key] = []
        self._callbacks[key].append(callback)

    def unsubscribe(self, key: str, callback: Callable):
        """
        Unsubscribe from data changes

        Args:
            key: Data key
            callback: Callback function to remove
        """
        if key in self._callbacks and callback in self._callbacks[key]:
            self._callbacks[key].remove(callback)

    def age(self, key: str) -> Optional[float]:
        """
        Seconds since a key was last updated, or None if never updated.

        Lets consumers detect stale data (e.g. REM unplugged mid-drive)
        instead of trusting whatever value was stored last.
        """
        with self._data_lock:
            ts = self._timestamps.get(key)
        if ts is None:
            return None
        return time.time() - ts

    def get_all(self) -> Dict[str, Any]:
        """Get all data (snapshot)"""
        with self._data_lock:
            return self._data.copy()

    def close(self):
        """Cleanup resources"""
        self._callbacks.clear()
        self._data.clear()
        self._timestamps.clear()
