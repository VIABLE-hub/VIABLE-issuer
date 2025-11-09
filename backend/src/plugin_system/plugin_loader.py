"""
Plugin Loader and Registry
Handles discovery, loading, and management of plugins
"""

import importlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type
import logging
import json

from .plugin_interface import VeritasPlugin, PluginConfig, PluginMetadata, PluginType

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Central registry for all loaded plugins.
    Manages plugin lifecycle and provides access to plugin instances.
    """
    
    def __init__(self):
        self._plugins: Dict[str, VeritasPlugin] = {}
        self._plugin_classes: Dict[str, Type[VeritasPlugin]] = {}
        self._plugin_metadata: Dict[str, PluginMetadata] = {}
        self._enabled_plugins: Dict[str, Dict[str, VeritasPlugin]] = {}  # tenant_id -> plugins
    
    def register_plugin_class(
        self,
        plugin_class: Type[VeritasPlugin],
        metadata: PluginMetadata
    ) -> bool:
        """
        Register a plugin class (not an instance).
        
        Args:
            plugin_class: Plugin class to register
            metadata: Plugin metadata
        
        Returns:
            True if registration successful
        """
        try:
            if not issubclass(plugin_class, VeritasPlugin):
                logger.error(f"Plugin {metadata.name} does not inherit from VeritasPlugin")
                return False
            
            self._plugin_classes[metadata.name] = plugin_class
            self._plugin_metadata[metadata.name] = metadata
            
            logger.info(f"✅ Registered plugin class: {metadata.name} v{metadata.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register plugin {metadata.name}: {e}")
            return False
    
    def load_plugin(
        self,
        plugin_name: str,
        config: PluginConfig
    ) -> Optional[VeritasPlugin]:
        """
        Load and initialize a plugin instance for a specific tenant.
        
        Args:
            plugin_name: Name of registered plugin
            config: Plugin configuration
        
        Returns:
            Plugin instance or None if loading failed
        """
        try:
            if plugin_name not in self._plugin_classes:
                logger.error(f"Plugin {plugin_name} not registered")
                return None
            
            # Create plugin instance
            plugin_class = self._plugin_classes[plugin_name]
            plugin = plugin_class(config)
            
            # Validate configuration
            if not plugin.validate_config():
                logger.error(f"Invalid configuration for plugin {plugin_name}")
                return None
            
            # Initialize plugin
            if not plugin.initialize():
                logger.error(f"Failed to initialize plugin {plugin_name}")
                return None
            
            plugin._initialized = True
            
            # Store in registry
            tenant_id = config.tenant_id
            if tenant_id not in self._enabled_plugins:
                self._enabled_plugins[tenant_id] = {}
            
            self._enabled_plugins[tenant_id][plugin_name] = plugin
            
            logger.info(f"✅ Loaded plugin: {plugin_name} for tenant {tenant_id}")
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return None
    
    def get_plugin(self, plugin_name: str, tenant_id: str) -> Optional[VeritasPlugin]:
        """
        Get a loaded plugin instance for a specific tenant.
        
        Args:
            plugin_name: Name of plugin
            tenant_id: Tenant ID
        
        Returns:
            Plugin instance or None if not found
        """
        return self._enabled_plugins.get(tenant_id, {}).get(plugin_name)
    
    def get_plugins_by_type(
        self,
        plugin_type: PluginType,
        tenant_id: str
    ) -> List[VeritasPlugin]:
        """
        Get all loaded plugins of a specific type for a tenant.
        
        Args:
            plugin_type: Type of plugins to retrieve
            tenant_id: Tenant ID
        
        Returns:
            List of plugin instances
        """
        tenant_plugins = self._enabled_plugins.get(tenant_id, {})
        
        result = []
        for plugin_name, plugin in tenant_plugins.items():
            metadata = self._plugin_metadata.get(plugin_name)
            if metadata and metadata.plugin_type == plugin_type:
                result.append(plugin)
        
        return result
    
    def unload_plugin(self, plugin_name: str, tenant_id: str) -> bool:
        """
        Unload a plugin instance.
        
        Args:
            plugin_name: Name of plugin
            tenant_id: Tenant ID
        
        Returns:
            True if unload successful
        """
        try:
            tenant_plugins = self._enabled_plugins.get(tenant_id, {})
            if plugin_name in tenant_plugins:
                plugin = tenant_plugins[plugin_name]
                plugin.shutdown()
                del tenant_plugins[plugin_name]
                logger.info(f"Unloaded plugin: {plugin_name} for tenant {tenant_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def get_all_registered_plugins(self) -> Dict[str, PluginMetadata]:
        """Get metadata for all registered plugins."""
        return self._plugin_metadata.copy()
    
    def get_loaded_plugins(self, tenant_id: str) -> Dict[str, VeritasPlugin]:
        """Get all loaded plugins for a tenant."""
        return self._enabled_plugins.get(tenant_id, {}).copy()


class PluginLoader:
    """
    Discovers and loads plugins from the filesystem.
    """
    
    def __init__(self, registry: PluginRegistry, plugin_dirs: List[Path]):
        """
        Initialize plugin loader.
        
        Args:
            registry: Plugin registry to register discovered plugins
            plugin_dirs: List of directories to search for plugins
        """
        self.registry = registry
        self.plugin_dirs = plugin_dirs
    
    def discover_plugins(self) -> List[str]:
        """
        Discover all plugins in configured directories.
        
        Returns:
            List of discovered plugin names
        """
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
                continue
            
            logger.info(f"Searching for plugins in: {plugin_dir}")
            
            # Look for plugin modules (directories with __init__.py)
            for item in plugin_dir.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    try:
                        plugins = self._load_plugin_module(item)
                        discovered.extend(plugins)
                    except Exception as e:
                        logger.error(f"Failed to load plugin from {item}: {e}")
        
        logger.info(f"Discovered {len(discovered)} plugins")
        return discovered
    
    def _load_plugin_module(self, plugin_path: Path) -> List[str]:
        """
        Load a plugin module and register all plugin classes found.
        
        Args:
            plugin_path: Path to plugin directory
        
        Returns:
            List of registered plugin names
        """
        registered = []
        
        try:
            # Import the plugin module
            module_name = f"plugins.{plugin_path.name}"
            spec = importlib.util.spec_from_file_location(
                module_name,
                plugin_path / "__init__.py"
            )
            
            if spec is None or spec.loader is None:
                logger.error(f"Could not load plugin module from {plugin_path}")
                return registered
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find all plugin classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's a VeritasPlugin subclass (but not VeritasPlugin itself)
                if (issubclass(obj, VeritasPlugin) and 
                    obj is not VeritasPlugin and
                    obj.__module__ == module_name):
                    
                    # Try to get metadata
                    try:
                        # Create temporary instance to get metadata
                        temp_config = PluginConfig(
                            plugin_name="temp",
                            enabled=False,
                            tenant_id="temp",
                            settings={}
                        )
                        temp_instance = obj(temp_config)
                        metadata = temp_instance.get_metadata()
                        
                        # Register the plugin class
                        if self.registry.register_plugin_class(obj, metadata):
                            registered.append(metadata.name)
                    
                    except Exception as e:
                        logger.error(f"Failed to get metadata for {name}: {e}")
            
            return registered
            
        except Exception as e:
            logger.error(f"Error loading plugin module {plugin_path}: {e}")
            return registered
    
    def load_plugins_from_config(self, config_path: Path) -> None:
        """
        Load and initialize plugins based on configuration file.
        
        Config format (JSON):
        {
            "plugins": {
                "tenant_id": {
                    "plugin_name": {
                        "enabled": true,
                        "settings": {
                            "key": "value"
                        },
                        "priority": 100
                    }
                }
            }
        }
        
        Args:
            config_path: Path to plugin configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            plugins_config = config_data.get('plugins', {})
            
            for tenant_id, tenant_plugins in plugins_config.items():
                for plugin_name, plugin_settings in tenant_plugins.items():
                    if not plugin_settings.get('enabled', False):
                        continue
                    
                    config = PluginConfig(
                        plugin_name=plugin_name,
                        enabled=True,
                        tenant_id=tenant_id,
                        settings=plugin_settings.get('settings', {}),
                        priority=plugin_settings.get('priority', 100)
                    )
                    
                    self.registry.load_plugin(plugin_name, config)
            
            logger.info("Loaded plugins from configuration")
            
        except Exception as e:
            logger.error(f"Failed to load plugins from config: {e}")


# Global plugin registry instance
_global_registry = PluginRegistry()


def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry instance."""
    return _global_registry

