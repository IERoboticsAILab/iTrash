"""
Simplified state manager for iTrash system.
Core state management for hardware loop and display communication.
"""

import threading
from typing import Any, Dict, Optional

class LocalState:
    """Simple local state manager with thread safety.

    Provides atomic update/get for a shared dictionary used across threads.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self.state: Dict[str, Any] = {
            "phase": "idle",
            "last_classification": None,
            "last_classification_ts": None,
            "reward": False,
            "system_status": "initializing",
            "last_disposal": {
                "user_thrown": None,
                "timestamp": None,
                "correct": None,
            },
            "sensor_status": {
                "object_detected": False,
                "blue_bin": False,
                "yellow_bin": False,
                "brown_bin": False
            }
        }
    
    def update(self, key: str, value: Any) -> None:
        """Update a state value with thread safety."""
        with self._lock:
            self.state[key] = value
            # When transitioning back to idle, clear last classification data
            if key == "phase" and value == "idle":
                self.state["last_classification"] = None
                self.state["last_classification_ts"] = None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value with thread safety."""
        with self._lock:
            return self.state.get(key, default)
    
    def update_sensor_status(self, sensor: str, status: bool) -> None:
        """Update sensor status atomically."""
        with self._lock:
            if "sensor_status" not in self.state:
                self.state["sensor_status"] = {}
            self.state["sensor_status"][sensor] = status
    
    def get_sensor_status(self, sensor: str) -> bool:
        """Get sensor status in a thread-safe manner."""
        with self._lock:
            return self.state.get("sensor_status", {}).get(sensor, False)
    
    def reset(self) -> None:
        """Reset state to initial values atomically."""
        with self._lock:
            self.state = {
                "phase": "idle",
                "last_classification": None,
                "last_classification_ts": None,
                "reward": False,
                "system_status": "ready",
                "last_disposal": {
                    "user_thrown": None,
                    "timestamp": None,
                    "correct": None,
                },
                "sensor_status": {
                    "object_detected": False,
                    "blue_bin": False,
                    "yellow_bin": False,
                    "brown_bin": False
                }
            }

# Global state instance
state = LocalState() 