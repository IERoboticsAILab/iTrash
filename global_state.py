"""
Simplified global state for iTrash core system.
Shared between hardware loop and display manager.
"""

from api.state import LocalState

# Shared singleton state instance
state = LocalState()

# Export for easy importing
__all__ = ['state'] 