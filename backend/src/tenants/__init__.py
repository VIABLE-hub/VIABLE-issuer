"""
StudentVC Multi-Tenant System

This package provides tenant-specific configurations, database isolation,
and university-specific customizations for the StudentVC platform.

Architecture:
- Each tenant has its own configuration, database, and settings
- Tenants are identified by environment variable or domain detection
- Falls back to legacy tenant_utils.py for compatibility

New Unified Systems (v2.0):
- Unified tenant detection with priority-based resolution
- Centralized configuration management with caching
- Request middleware for automatic tenant context
"""

from .registry import TenantRegistry, get_current_tenant_config
from .base_config import BaseTenantConfig
# Unified detector is now the primary tenant detection system
from .unified_detector import (
    get_current_tenant, 
    set_current_tenant, 
    is_valid_tenant,
    get_valid_tenants,
    clear_tenant_cache
)
# Legacy detection functions (deprecated, use unified_detector instead)
from .detection import get_current_tenant_id as _legacy_get_current_tenant_id
from .config_manager import get_tenant_config, update_tenant_network_config, get_tenant_urls, clear_tenant_config_cache
from .middleware import TenantMiddleware, tenant_required, get_request_tenant_id, switch_tenant_context

# Re-export legacy function for backward compatibility
get_current_tenant_id = _legacy_get_current_tenant_id

__all__ = [
    # Legacy API (for backward compatibility)
    'TenantRegistry', 
    'get_current_tenant_config', 
    'BaseTenantConfig',
    
    # Unified Tenant Detection API (v2.0) - PRIMARY API
    'get_current_tenant',      # PRIMARY: Use this for tenant detection
    'set_current_tenant',      # PRIMARY: Use this to set tenant
    'is_valid_tenant',         # PRIMARY: Use this to validate tenant ID
    'get_valid_tenants',       # PRIMARY: Get list of valid tenants
    'clear_tenant_cache',      # PRIMARY: Clear detection cache
    
    # Legacy detection API (deprecated, use unified_detector instead)
    'get_current_tenant_id',   # DEPRECATED: Use get_current_tenant() instead
    
    # Tenant Configuration API
    'get_tenant_config',
    'update_tenant_network_config',
    'get_tenant_urls',
    'clear_tenant_config_cache',
    
    # Middleware API
    'TenantMiddleware',
    'tenant_required',
    'get_request_tenant_id',
    'switch_tenant_context'
] 