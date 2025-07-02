"""
Tenant Registry

Central registry for all university tenants with backward compatibility.
Manages tenant discovery, loading, and configuration.
"""

import os
import logging
from typing import Dict, Optional, Type, Any
from flask import request, has_request_context

from .base_config import BaseTenantConfig

logger = logging.getLogger(__name__)

class TenantRegistry:
    """
    Central registry for all university tenants.
    
    Provides:
    - Tenant registration and discovery
    - Environment variable and domain-based detection
    - Backward compatibility with legacy tenant_utils.py
    - Tenant configuration loading and caching
    """
    
    def __init__(self):
        self._tenants: Dict[str, Type[BaseTenantConfig]] = {}
        self._tenant_instances: Dict[str, BaseTenantConfig] = {}
        
    def register_tenant(self, tenant_id: str, tenant_class: Type[BaseTenantConfig]):
        """Register a tenant configuration class"""
        self._tenants[tenant_id] = tenant_class
        logger.info(f"Registered tenant: {tenant_id}")
    
    def get_available_tenants(self) -> list:
        """Get list of all registered tenant IDs"""
        return list(self._tenants.keys())
    
    def get_tenant_config(self, tenant_id: str) -> Optional[BaseTenantConfig]:
        """
        Get tenant configuration instance.
        Uses caching to avoid recreating instances.
        """
        if tenant_id not in self._tenants:
            logger.warning(f"Tenant not found: {tenant_id}")
            return None
            
        # Use cached instance if available
        if tenant_id not in self._tenant_instances:
            tenant_class = self._tenants[tenant_id]
            self._tenant_instances[tenant_id] = tenant_class()  # Fixed: no arguments needed
            logger.info(f"Created tenant instance: {tenant_id}")
            
        return self._tenant_instances[tenant_id]
    
    def detect_current_tenant(self) -> Optional[BaseTenantConfig]:
        """
        Detect current tenant based on environment variable or domain.
        
        Detection order:
        1. TENANT_ID environment variable
        2. Request domain pattern matching
        3. Fallback to legacy tenant_utils.py for compatibility
        4. Default to ROOT tenant if no specific tenant detected
        """
        
        # Method 1: Environment variable detection
        tenant_env = os.environ.get('TENANT_ID', '').lower()
        if tenant_env and tenant_env in self._tenants:
            logger.info(f"Tenant detected via environment: {tenant_env}")
            return self.get_tenant_config(tenant_env)
        
        # Method 2: Domain pattern matching
        if has_request_context():
            try:
                host = request.host.lower()
                for tenant_id, tenant_class in self._tenants.items():
                    # Get tenant instance to check domain patterns
                    tenant_config = self.get_tenant_config(tenant_id)
                    if tenant_config:
                        for pattern in tenant_config.domain_patterns:
                            if pattern in host:
                                logger.info(f"Tenant detected via domain pattern '{pattern}': {tenant_id}")
                                return tenant_config
            except Exception as e:
                logger.debug(f"Could not detect tenant from request: {e}")
        
        # Method 3: Fallback to legacy tenant_utils.py for compatibility
        try:
            from ..tenant_utils import detect_current_tenant as legacy_detect
            legacy_tenant = legacy_detect()
            if legacy_tenant and legacy_tenant.get('id') in self._tenants:
                tenant_id = legacy_tenant['id']
                logger.info(f"Tenant detected via legacy system: {tenant_id}")
                return self.get_tenant_config(tenant_id)
        except Exception as e:
            logger.debug(f"Legacy tenant detection failed: {e}")
        
        # Method 4: Default to ROOT tenant when no specific tenant detected
        # This ensures that all requests get proper branding instead of showing FUB branding
        if 'root' in self._tenants:
            logger.info("No specific tenant detected, defaulting to ROOT tenant")
            return self.get_tenant_config('root')
        
        logger.warning("No tenant detected and ROOT tenant not available!")
        return None
    
    def get_tenant_logos_dict(self, tenant_config: Optional[BaseTenantConfig] = None) -> Dict[str, Any]:
        """
        Get tenant logos dictionary for template compatibility.
        
        If no tenant_config provided, auto-detects current tenant.
        Returns format compatible with legacy get_tenant_logos() function.
        """
        if tenant_config is None:
            tenant_config = self.detect_current_tenant()
        
        # Default logos (compatible with legacy system)
        logos = {
            'main_logo': 'studentVC-logo-sora-cropped.png',  # StudentVC logo for header center
            'university_logo': None,  # University logo for header left
            'university_name': None,
            'tenant_color': '#003f7f'  # Default Berlin Blue
        }
        
        # Update with tenant-specific information
        if tenant_config:
            # 🔧 FIXED LOGO LOGIC:
            # - main_logo: ALWAYS StudentVC logo (header center)
            # - university_logo: University-specific logo (header left)
            logos.update({
                'main_logo': 'studentVC-logo-sora-cropped.png',  # Always StudentVC logo
                'university_logo': tenant_config.logo_filename,  # University logo (red TUB, green FUB, etc.)
                'university_name': tenant_config.short_name,
                'tenant_color': tenant_config.primary_color
            })
        
        return logos

# Global registry instance
_registry = TenantRegistry()

def get_tenant_registry() -> TenantRegistry:
    """Get the global tenant registry instance"""
    return _registry

def get_current_tenant_config() -> Optional[BaseTenantConfig]:
    """
    Convenience function to get current tenant configuration.
    Auto-detects based on environment/domain.
    """
    return _registry.detect_current_tenant()

def get_current_tenant_logos() -> Dict[str, Any]:
    """
    Convenience function to get current tenant logos.
    Compatible with legacy template usage.
    """
    return _registry.get_tenant_logos_dict()

# === LEGACY COMPATIBILITY FUNCTIONS === #

def register_legacy_compatibility():
    """
    Register compatibility functions to maintain backward compatibility
    with existing tenant_utils.py usage.
    """
    
    def legacy_detect_current_tenant():
        """Legacy compatibility wrapper"""
        tenant_config = get_current_tenant_config()
        return tenant_config.to_dict() if tenant_config else None
    
    def legacy_get_tenant_logos():
        """Legacy compatibility wrapper"""
        return get_current_tenant_logos()
    
    # Make functions available for import compatibility
    import sys
    current_module = sys.modules[__name__]
    current_module.legacy_detect_current_tenant = legacy_detect_current_tenant
    current_module.legacy_get_tenant_logos = legacy_get_tenant_logos

# Initialize legacy compatibility
register_legacy_compatibility() 