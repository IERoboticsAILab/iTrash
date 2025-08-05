"""
Global state singleton for iTrash unified system.
Shared across hardware loop, API endpoints, and MQTT client.
"""

from api.state import LocalState

# Shared singleton state instance
state = LocalState()

# Export for easy importing
__all__ = ['state'] 