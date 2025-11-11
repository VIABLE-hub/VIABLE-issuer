"""
StudentVC Plugin System
Enables students to create modular, decentralized extensions for Veritas

This plugin system allows students to:
- Add blockchain storage modules
- Integrate IPFS for distributed storage
- Create custom verification logic
- Build decentralized consensus mechanisms
- Extend the system without modifying core code
"""

from .plugin_interface import VeritasPlugin, PluginMetadata, PluginConfig
from .plugin_loader import PluginLoader, PluginRegistry
from .plugin_events import EventType, Event, EventBus

__all__ = [
    'VeritasPlugin',
    'PluginMetadata',
    'PluginConfig',
    'PluginLoader',
    'PluginRegistry',
    'EventType',
    'Event',
    'EventBus',
]

__version__ = '1.0.0'

