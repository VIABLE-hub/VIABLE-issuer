"""
Tenant Configuration Manager
Handles unified tenant configuration with proper persistence, caching, and synchronization
"""

import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from flask import current_app
from sqlalchemy.orm.attributes import flag_modified

from .detection import get_current_tenant_id
from ..models import TenantSettings, db

logger = logging.getLogger(__name__)

class TenantConfigManager:
    """
    Unified tenant configuration manager
    Combines static config (JSON) with dynamic settings (database)
    """
    
    def __init__(self):
        self._config_cache = {}
        self._settings_cache = {}
        self._static_config_cache = {}
    
    def get_complete_tenant_config(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get complete tenant configuration (static + dynamic)
        
        Args:
            tenant_id: Specific tenant ID (defaults to current)
            
        Returns:
            dict: Complete tenant configuration
        """
        if not tenant_id:
            tenant_id = get_current_tenant_id()
        
        # Check cache first
        cache_key = f"complete_config_{tenant_id}"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        # Load static configuration
        static_config = self._load_static_config(tenant_id)
        
        # Load dynamic settings
        dynamic_settings = self._load_dynamic_settings(tenant_id)
        
        # Merge configurations
        complete_config = {
            # Static configuration (from JSON)
            'tenant_id': static_config.get('tenantId', tenant_id),
            'display_name': static_config.get('displayName', 'StudentVC'),
            'short_name': static_config.get('shortName', 'StudentVC'),
            'primary_color': static_config.get('primaryColor', '#003f7f'),
            'accent_color': static_config.get('accentColor', '#0066cc'),
            'text_color': static_config.get('textColor', '#333333'),
            'background_color': static_config.get('backgroundColor', '#FFFFFF'),
            'font_family': static_config.get('fontFamily', 'system-ui'),
            'logo_path': static_config.get('logoPath', 'studentVC-logo-sora-cropped.png'),
            'main_logo_path': static_config.get('mainLogoPath', 'studentVC-logo-sora-cropped.png'),
            'domain_patterns': static_config.get('domainPatterns', []),
            
            # Dynamic settings (from database)
            'network_settings': dynamic_settings.get('network_settings', {}),
            'disclosure_settings': dynamic_settings.get('disclosure_settings', {}),
            'appearance_settings': dynamic_settings.get('appearance_settings', {}),
            'trust_settings': dynamic_settings.get('trust_settings', {}),
            'advanced_settings': dynamic_settings.get('advanced_settings', {}),
            
            # Computed properties
            'ngrok_url': self._get_effective_ngrok_url(dynamic_settings),
            'server_url': self._get_effective_server_url(dynamic_settings),
            'issuer_url': None,  # Will be computed on demand
            'verifier_url': None,  # Will be computed on demand
        }
        
        # Cache the result
        self._config_cache[cache_key] = complete_config
        
        logger.debug(f"🔧 Complete config loaded for tenant: {tenant_id}")
        return complete_config
    
    def update_tenant_setting(self, category: str, key: str, value: Any, tenant_id: Optional[str] = None) -> bool:
        """
        Update a specific tenant setting
        
        Args:
            category: Settings category (network_settings, appearance_settings, etc.)
            key: Setting key
            value: Setting value
            tenant_id: Specific tenant ID (defaults to current)
            
        Returns:
            bool: Success status
        """
        if not tenant_id:
            tenant_id = get_current_tenant_id()
        
        try:
            # Get tenant settings
            tenant_settings = TenantSettings.get_or_create_default(tenant_id)
            
            # Get current category settings
            current_settings = getattr(tenant_settings, category, {}) or {}
            
            # Update the specific key
            current_settings[key] = value
            
            # Save back to database
            setattr(tenant_settings, category, current_settings)
            flag_modified(tenant_settings, category)
            
            db.session.commit()
            
            # Clear cache for this tenant
            self._clear_tenant_cache(tenant_id)
            
            logger.info(f"🔧 Updated {category}.{key} for tenant {tenant_id}: {value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update tenant setting: {e}")
            db.session.rollback()
            return False
    
    def update_network_config(self, config_updates: Dict[str, Any], tenant_id: Optional[str] = None) -> bool:
        """
        Update network configuration for a tenant
        
        Args:
            config_updates: Network config updates
            tenant_id: Specific tenant ID (defaults to current)
            
        Returns:
            bool: Success status
        """
        if not tenant_id:
            tenant_id = get_current_tenant_id()
        
        try:
            tenant_settings = TenantSettings.get_or_create_default(tenant_id)
            
            # Get current network settings
            network_settings = tenant_settings.network_settings or {}
            
            # Update with new values
            network_settings.update(config_updates)
            
            # Special handling for ngrok configuration
            if 'ngrok_url' in config_updates:
                ngrok_url = config_updates['ngrok_url'].strip()
                if ngrok_url:
                    # Ensure proper format
                    if not ngrok_url.startswith(('http://', 'https://')):
                        ngrok_url = f"https://{ngrok_url}"
                    
                    network_settings['ngrok_url'] = ngrok_url
                    network_settings['use_ngrok'] = True
                    network_settings['connection_mode'] = 'ngrok'
                    
                    # Update Flask config for immediate effect
                    current_app.config['SERVER_URL'] = ngrok_url
                else:
                    network_settings['use_ngrok'] = False
                    network_settings['connection_mode'] = 'local'
            
            # Save to database
            tenant_settings.network_settings = network_settings
            flag_modified(tenant_settings, 'network_settings')
            
            db.session.commit()
            
            # Clear cache
            self._clear_tenant_cache(tenant_id)
            
            logger.info(f"🌐 Network config updated for tenant {tenant_id}: {config_updates}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update network config: {e}")
            db.session.rollback()
            return False
    
    def get_tenant_urls(self, tenant_id: Optional[str] = None) -> Dict[str, str]:
        """
        Get all tenant URLs (server, issuer, verifier)
        
        Args:
            tenant_id: Specific tenant ID (defaults to current)
            
        Returns:
            dict: URLs for the tenant
        """
        if not tenant_id:
            tenant_id = get_current_tenant_id()
        
        config = self.get_complete_tenant_config(tenant_id)
        server_url = config['server_url']
        
        return {
            'server_url': server_url,
            'issuer_url': f"{server_url}/issuer",
            'verifier_url': f"{server_url}/verifier",
            'vcstatus_url': f"{server_url}/vcstatus",
            'settings_url': f"{server_url}/settings",
            'well_known_issuer': f"{server_url}/.well-known/openid-credential-issuer",
            'well_known_config': f"{server_url}/.well-known/openid-configuration"
        }
    
    def _load_static_config(self, tenant_id: str) -> Dict[str, Any]:
        """Load static configuration from JSON file"""
        cache_key = f"static_{tenant_id}"
        if cache_key in self._static_config_cache:
            return self._static_config_cache[cache_key]
        
        try:
            config_file = Path(__file__).parent / "instances" / tenant_id / "config.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    static_config = json.load(f)
                    self._static_config_cache[cache_key] = static_config
                    return static_config
            else:
                logger.warning(f"⚠️ Static config file not found for tenant: {tenant_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to load static config for {tenant_id}: {e}")
        
        # Return default configuration
        default_config = {
            'tenantId': tenant_id,
            'displayName': 'StudentVC',
            'shortName': 'StudentVC',
            'primaryColor': '#003f7f',
            'accentColor': '#0066cc',
            'textColor': '#333333',
            'backgroundColor': '#FFFFFF',
            'fontFamily': 'system-ui',
            'logoPath': 'studentVC-logo-sora-cropped.png',
            'mainLogoPath': 'studentVC-logo-sora-cropped.png',
            'domainPatterns': []
        }
        
        self._static_config_cache[cache_key] = default_config
        return default_config
    
    def _load_dynamic_settings(self, tenant_id: str) -> Dict[str, Any]:
        """Load dynamic settings from database"""
        cache_key = f"dynamic_{tenant_id}"
        if cache_key in self._settings_cache:
            return self._settings_cache[cache_key]
        
        try:
            tenant_settings = TenantSettings.get_or_create_default(tenant_id)
            
            dynamic_settings = {
                'network_settings': tenant_settings.network_settings or {},
                'disclosure_settings': tenant_settings.disclosure_settings or {},
                'appearance_settings': tenant_settings.appearance_settings or {},
                'trust_settings': tenant_settings.trust_settings or {},
                'advanced_settings': tenant_settings.advanced_settings or {},
                'key_settings': tenant_settings.key_settings or {},
                'notification_settings': tenant_settings.notification_settings or {}
            }
            
            self._settings_cache[cache_key] = dynamic_settings
            return dynamic_settings
            
        except Exception as e:
            logger.error(f"❌ Failed to load dynamic settings for {tenant_id}: {e}")
            return {}
    
    def _get_effective_ngrok_url(self, dynamic_settings: Dict[str, Any]) -> str:
        """Get effective ngrok URL from settings"""
        network_settings = dynamic_settings.get('network_settings', {})
        
        use_ngrok = network_settings.get('use_ngrok', False)
        ngrok_url = network_settings.get('ngrok_url', '').strip()
        
        if use_ngrok and ngrok_url:
            return ngrok_url
        return ''
    
    def _get_effective_server_url(self, dynamic_settings: Dict[str, Any]) -> str:
        """Get effective server URL (ngrok or local)"""
        network_settings = dynamic_settings.get('network_settings', {})
        
        # Check for ngrok configuration
        use_ngrok = network_settings.get('use_ngrok', False)
        ngrok_url = network_settings.get('ngrok_url', '').strip()
        
        if use_ngrok and ngrok_url:
            if not ngrok_url.startswith(('http://', 'https://')):
                ngrok_url = f"https://{ngrok_url}"
            return ngrok_url.rstrip('/')
        
        # Fallback to local configuration
        default_ip = network_settings.get('default_ip', '192.168.178.122')
        default_port = network_settings.get('default_port', '8080')
        use_https = network_settings.get('use_https', True)
        
        protocol = 'https' if use_https else 'http'
        return f"{protocol}://{default_ip}:{default_port}"
    
    def _clear_tenant_cache(self, tenant_id: str):
        """Clear cache for specific tenant"""
        keys_to_remove = [
            f"complete_config_{tenant_id}",
            f"static_{tenant_id}",
            f"dynamic_{tenant_id}"
        ]
        
        for key in keys_to_remove:
            self._config_cache.pop(key, None)
            self._static_config_cache.pop(key, None)
            self._settings_cache.pop(key, None)
        
        logger.debug(f"🔄 Cache cleared for tenant: {tenant_id}")
    
    def clear_all_cache(self):
        """Clear all configuration cache"""
        self._config_cache.clear()
        self._settings_cache.clear()
        self._static_config_cache.clear()
        logger.info("🔄 All tenant configuration cache cleared")

# Global configuration manager
_config_manager = TenantConfigManager()

def get_tenant_config(tenant_id: Optional[str] = None) -> Dict[str, Any]:
    """Get complete tenant configuration"""
    return _config_manager.get_complete_tenant_config(tenant_id)

def update_tenant_network_config(config_updates: Dict[str, Any], tenant_id: Optional[str] = None) -> bool:
    """Update tenant network configuration"""
    return _config_manager.update_network_config(config_updates, tenant_id)

def get_tenant_urls(tenant_id: Optional[str] = None) -> Dict[str, str]:
    """Get all tenant URLs"""
    return _config_manager.get_tenant_urls(tenant_id)

def clear_tenant_config_cache():
    """Clear tenant configuration cache"""
    _config_manager.clear_all_cache() 