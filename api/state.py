"""
Local state manager for iTrash system.
Replaces MongoDB with simple in-memory state management.
"""

import threading
import time
from typing import Any, Dict, Optional
from datetime import datetime

class LocalState:
    """Simple local state manager with thread safety"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.state = {
            "phase": "idle",
            "last_classification": None,
            "reward": False,
            "last_update": datetime.now().isoformat(),
            "system_status": "initializing",
            "current_image": None,
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
            self.state["last_update"] = datetime.now().isoformat()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value with thread safety"""
        with self._lock:
            return self.state.get(key, default)
    
    def all(self) -> Dict[str, Any]:
        """Get all state values with thread safety"""
        with self._lock:
            return self.state.copy()
    
    def update_sensor_status(self, sensor: str, status: bool) -> None:
        """Update sensor status"""
        with self._lock:
            if "sensor_status" not in self.state:
                self.state["sensor_status"] = {}
            self.state["sensor_status"][sensor] = status
            self.state["last_update"] = datetime.now().isoformat()
    
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
                "last_update": datetime.now().isoformat(),
                "system_status": "ready",
                "current_image": None,
                "sensor_status": {
                    "object_detected": False,
                    "blue_bin": False,
                    "yellow_bin": False,
                    "brown_bin": False
                }
            }

# Global state instance
state = LocalState() 