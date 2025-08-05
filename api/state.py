"""
Simplified state manager for iTrash system.
Core state management for hardware loop and display communication.
"""

import threading
from typing import Any, Dict

class LocalState:
    """Simple local state manager with thread safety"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.state = {
            "phase": "idle",
            "last_classification": None,
            "reward": False,
            "system_status": "initializing",
            "sensor_status": {
                "object_detected": False,
                "blue_bin": False,
                "yellow_bin": False,
                "brown_bin": False
            }
        }
    
    def update(self, key: str, value: Any) -> None:
        """Update a state value with thread safety"""
        with self._lock:
            self.state[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value with thread safety"""
        with self._lock:
            return self.state.get(key, default)
    
    def update_sensor_status(self, sensor: str, status: bool) -> None:
        """Update sensor status"""
        with self._lock:
            if "sensor_status" not in self.state:
                self.state["sensor_status"] = {}
            self.state["sensor_status"][sensor] = status
    
    def get_sensor_status(self, sensor: str) -> bool:
        """Get sensor status"""
        with self._lock:
            return self.state.get("sensor_status", {}).get(sensor, False)
    
    def reset(self) -> None:
        """Reset state to initial values"""
        with self._lock:
            self.state = {
                "phase": "idle",
                "last_classification": None,
                "reward": False,
                "system_status": "ready",
                "sensor_status": {
                    "object_detected": False,
                    "blue_bin": False,
                    "yellow_bin": False,
                    "brown_bin": False
                }
            }

# Global state instance
state = LocalState() 