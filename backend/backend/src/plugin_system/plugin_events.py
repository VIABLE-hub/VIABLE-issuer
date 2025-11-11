"""
Plugin Event System
Allows plugins to react to system events
"""

from enum import Enum
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of system events"""
    # Credential events
    CREDENTIAL_ISSUED = "credential_issued"
    CREDENTIAL_VERIFIED = "credential_verified"
    CREDENTIAL_REVOKED = "credential_revoked"
    CREDENTIAL_RESTORED = "credential_restored"
    
    # Tenant events
    TENANT_CREATED = "tenant_created"
    TENANT_UPDATED = "tenant_updated"
    TENANT_SWITCHED = "tenant_switched"
    
    # Settings events
    SETTINGS_UPDATED = "settings_updated"
    NETWORK_UPDATED = "network_updated"
    
    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_UNLOADED = "plugin_unloaded"


@dataclass
class Event:
    """Represents a system event"""
    event_type: EventType
    tenant_id: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str  # Component that generated the event
    event_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_type": self.event_type.value,
            "tenant_id": self.tenant_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "event_id": self.event_id
        }


class EventBus:
    """
    Central event bus for the plugin system.
    Manages event subscriptions and dispatches events to plugins.
    """
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._async_subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000  # Keep last 1000 events
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type with a synchronous callback.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscriber added for event: {event_type.value}")
    
    def subscribe_async(
        self,
        event_type: EventType,
        callback: Callable[[Event], Any]
    ) -> None:
        """
        Subscribe to an event type with an asynchronous callback.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Async function to call when event occurs
        """
        if event_type not in self._async_subscribers:
            self._async_subscribers[event_type] = []
        
        self._async_subscribers[event_type].append(callback)
        logger.debug(f"Async subscriber added for event: {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> bool:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event
            callback: Callback function to remove
        
        Returns:
            True if callback was found and removed
        """
        # Check sync subscribers
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                return True
            except ValueError:
                pass
        
        # Check async subscribers
        if event_type in self._async_subscribers:
            try:
                self._async_subscribers[event_type].remove(callback)
                return True
            except ValueError:
                pass
        
        return False
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        logger.info(f"📢 Event published: {event.event_type.value} for tenant {event.tenant_id}")
        
        # Call synchronous subscribers
        subscribers = self._subscribers.get(event.event_type, [])
        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event subscriber: {e}")
        
        # Call asynchronous subscribers
        async_subscribers = self._async_subscribers.get(event.event_type, [])
        if async_subscribers:
            # Run async subscribers in the background
            asyncio.create_task(self._dispatch_async(event, async_subscribers))
    
    async def _dispatch_async(self, event: Event, callbacks: List[Callable]) -> None:
        """Dispatch event to async subscribers"""
        for callback in callbacks:
            try:
                await callback(event)
            except Exception as e:
                logger.error(f"Error in async event subscriber: {e}")
    
    def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Event]:
        """
        Get event history with optional filtering.
        
        Args:
            event_type: Filter by event type
            tenant_id: Filter by tenant ID
            limit: Maximum number of events to return
        
        Returns:
            List of events
        """
        events = self._event_history.copy()
        
        # Apply filters
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        
        # Return most recent events up to limit
        return events[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history"""
        self._event_history.clear()


# Global event bus instance
_global_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _global_event_bus


def emit_event(
    event_type: EventType,
    tenant_id: str,
    data: Dict[str, Any],
    source: str
) -> None:
    """
    Convenience function to emit an event.
    
    Args:
        event_type: Type of event
        tenant_id: Tenant ID
        data: Event data
        source: Source component
    """
    event = Event(
        event_type=event_type,
        tenant_id=tenant_id,
        data=data,
        timestamp=datetime.now(),
        source=source
    )
    get_event_bus().publish(event)

