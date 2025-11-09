"""
Plugin Interface for StudentVC
Defines the contract that all plugins must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins supported"""
    STORAGE = "storage"  # Blockchain, IPFS, etc.
    VERIFICATION = "verification"  # Custom verification logic
    CONSENSUS = "consensus"  # Distributed consensus
    ANALYTICS = "analytics"  # Data analytics
    NOTIFICATION = "notification"  # Notifications
    CUSTOM = "custom"  # Other extensions


@dataclass
class PluginMetadata:
    """Metadata about a plugin"""
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    dependencies: List[str]
    min_studentvc_version: str = "1.0.0"
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None


@dataclass
class PluginConfig:
    """Configuration for a plugin instance"""
    plugin_name: str
    enabled: bool
    tenant_id: str
    settings: Dict[str, Any]
    priority: int = 100  # Lower number = higher priority


class VeritasPlugin(ABC):
    """
    Base class for all StudentVC plugins.
    
    Students should inherit from this class and implement the required methods.
    
    Example:
        class MyBlockchainPlugin(VeritasPlugin):
            def initialize(self) -> bool:
                self.web3 = Web3(self.config.settings['rpc_url'])
                return self.web3.is_connected()
            
            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="Blockchain Storage",
                    version="1.0.0",
                    author="Student Name",
                    description="Store credentials on Ethereum",
                    plugin_type=PluginType.STORAGE,
                    dependencies=["web3"]
                )
    """
    
    def __init__(self, config: PluginConfig):
        """
        Initialize the plugin with configuration.
        
        Args:
            config: Plugin configuration including tenant context and settings
        """
        self.config = config
        self.logger = logging.getLogger(f"plugin.{config.plugin_name}")
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        This method is called when the plugin is loaded. Use it to:
        - Connect to external services (blockchain, IPFS, etc.)
        - Validate configuration
        - Set up resources
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Return plugin metadata.
        
        Returns:
            PluginMetadata object with plugin information
        """
        pass
    
    def shutdown(self) -> None:
        """
        Clean up plugin resources.
        
        Override this method to:
        - Close connections
        - Save state
        - Clean up resources
        """
        pass
    
    def register_routes(self, app) -> None:
        """
        Register Flask routes for this plugin.
        
        Override this method to add API endpoints.
        
        Example:
            @app.route('/api/plugin/my-plugin/status')
            def plugin_status():
                return jsonify({"status": "active"})
        
        Args:
            app: Flask application instance
        """
        pass
    
    def handle_event(self, event: 'Event') -> None:
        """
        Handle system events.
        
        Override this method to react to system events like:
        - credential_issued
        - credential_verified
        - credential_revoked
        - tenant_changed
        
        Args:
            event: Event object containing event data
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current plugin status.
        
        Override this method to provide custom status information.
        
        Returns:
            Dict with status information
        """
        return {
            "name": self.config.plugin_name,
            "enabled": self.config.enabled,
            "initialized": self._initialized,
            "tenant_id": self.config.tenant_id
        }
    
    def validate_config(self) -> bool:
        """
        Validate plugin configuration.
        
        Override this method to add custom configuration validation.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        return True


class StoragePlugin(VeritasPlugin):
    """
    Base class for storage plugins (Blockchain, IPFS, etc.)
    """
    
    @abstractmethod
    def store_credential(self, credential: Dict[str, Any]) -> str:
        """
        Store a credential.
        
        Args:
            credential: Credential data to store
        
        Returns:
            Storage identifier (transaction hash, CID, etc.)
        """
        pass
    
    @abstractmethod
    def retrieve_credential(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a credential by identifier.
        
        Args:
            identifier: Storage identifier
        
        Returns:
            Credential data or None if not found
        """
        pass
    
    @abstractmethod
    def verify_storage(self, credential: Dict[str, Any], identifier: str) -> bool:
        """
        Verify that stored data matches original.
        
        Args:
            credential: Original credential
            identifier: Storage identifier
        
        Returns:
            True if verification successful, False otherwise
        """
        pass


class VerificationPlugin(VeritasPlugin):
    """
    Base class for verification plugins
    """
    
    @abstractmethod
    def verify_credential(self, credential: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform additional verification on a credential.
        
        Args:
            credential: Credential to verify
        
        Returns:
            Dict with verification results:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "metadata": Dict[str, Any]
            }
        """
        pass


class ConsensusPlugin(VeritasPlugin):
    """
    Base class for distributed consensus plugins
    """
    
    @abstractmethod
    async def validate_with_consensus(
        self,
        credential: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate credential using distributed consensus.
        
        Args:
            credential: Credential to validate
        
        Returns:
            Dict with consensus results:
            {
                "valid": bool,
                "consensus_reached": bool,
                "approval_rate": float,
                "validators": int,
                "timestamp": float
            }
        """
        pass

