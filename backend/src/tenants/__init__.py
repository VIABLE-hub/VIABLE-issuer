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
from .detection import get_current_tenant_id, set_current_tenant, clear_tenant_detection_cache
from .config_manager import get_tenant_config, update_tenant_network_config, get_tenant_urls, clear_tenant_config_cache
from .middleware import TenantMiddleware, tenant_required, get_request_tenant_id, switch_tenant_context

__all__ = [
    # Legacy API (for backward compatibility)
    'TenantRegistry', 
    'get_current_tenant_config', 
    'BaseTenantConfig',
    
    # New Unified API (v2.0)
    'get_current_tenant_id',
    'set_current_tenant', 
    'clear_tenant_detection_cache',
    'get_tenant_config',
    'update_tenant_network_config',
    'get_tenant_urls',
    'clear_tenant_config_cache',
    'TenantMiddleware',
    'tenant_required',
    'get_request_tenant_id',
    'switch_tenant_context'
] 