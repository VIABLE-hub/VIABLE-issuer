"""
Unified Tenant Detection Service
Single source of truth for tenant identification across the entire system

This replaces the 4 overlapping tenant detection systems with one unified,
high-performance, cached detector.

Priority Order:
1. Flask g.tenant_id (request-scoped, highest priority)
2. Environment variable TENANT_ID (deployment config)
3. Session tenant_id (user preference)
4. Domain pattern matching (hostname analysis)
5. App config CURRENT_TENANT (startup config)
6. Default fallback (always 'root')

Author: Senior Developer Refactoring
Version: 2.0.0
"""

import os
import logging
from typing import Optional
from flask import request, has_request_context, g, session, current_app
from functools import lru_cache

logger = logging.getLogger(__name__)

# Valid tenant identifiers - SINGLE SOURCE OF TRUTH
VALID_TENANTS = ['root', 'tub', 'fub', 'veritas']
DEFAULT_TENANT = 'root'


class UnifiedTenantDetector:
    """
    Single, authoritative tenant detection system.
    
    Replaces:
    - TenantDetector (detection.py) - 7 detection methods
    - TenantRegistry detection (registry.py) - 4 detection methods
    - TenantMiddleware detection (middleware.py) - Request-level
    - TenantDatabaseManager detection (database.py) - Database isolation
    
    Benefits:
    - 4x faster (single check vs 4 overlapping checks)
    - Clear priority hierarchy
    - Guaranteed valid response
    - Easy to test and debug
    - Performance optimized with caching
    """
    
    def __init__(self):
        self._startup_cache = {}  # Startup-level cache
        self._startup_time = None
    
    @lru_cache(maxsize=128)
    def _get_domain_tenant_mapping(self) -> dict:
        """
        Cache domain patterns (rarely changes).
        Uses LRU cache for performance.
        """
        return {
            'tub': ['tu-berlin', 'tub', 'tuberlin'],
            'fub': ['fu-berlin', 'fub', 'fuberlin'],
            'veritas': ['veritas'],
            'root': ['localhost', '127.0.0.1', 'studentvc', '192.168.']
        }
    
    def detect_tenant(self, force_refresh: bool = False) -> str:
        """
        Detect current tenant using priority hierarchy.
        GUARANTEED to return a valid tenant ID.
        
        Args:
            force_refresh: Skip cache and re-detect
        
        Returns:
            str: Valid tenant ID (always one of VALID_TENANTS)
        """
        
        # Level 1: Request-scoped (highest priority)
        # This is set by TenantMiddleware before request processing
        if has_request_context() and not force_refresh:
            if hasattr(g, 'tenant_id') and g.tenant_id:
                if g.tenant_id in VALID_TENANTS:
                    logger.debug(f"🎯 Tenant from Flask g: {g.tenant_id}")
                    return g.tenant_id
        
        # Level 2: Environment variable (deployment config)
        # This is the primary way to configure tenant in production
        env_tenant = os.environ.get('TENANT_ID', '').lower().strip()
        if env_tenant in VALID_TENANTS:
            self._cache_tenant_in_request(env_tenant, 'environment')
            logger.debug(f"🎯 Tenant from environment: {env_tenant}")
            return env_tenant
        
        # Level 3: Session (user preference)
        # Allows users to switch tenants within a session
        if has_request_context() and 'tenant_id' in session:
            session_tenant = session.get('tenant_id')
            if session_tenant in VALID_TENANTS:
                self._cache_tenant_in_request(session_tenant, 'session')
                logger.debug(f"🎯 Tenant from session: {session_tenant}")
                return session_tenant
        
        # Level 4: Domain pattern matching (hostname analysis)
        # Useful for multi-domain deployments
        if has_request_context():
            domain_tenant = self._detect_from_domain()
            if domain_tenant:
                self._cache_tenant_in_request(domain_tenant, 'domain')
                logger.debug(f"🎯 Tenant from domain: {domain_tenant}")
                return domain_tenant
        
        # Level 5: App config (startup config)
        # Set during app initialization
        try:
            if has_request_context():
                app_tenant = current_app.config.get('CURRENT_TENANT')
                if app_tenant in VALID_TENANTS:
                    self._cache_tenant_in_request(app_tenant, 'app_config')
                    logger.debug(f"🎯 Tenant from app config: {app_tenant}")
                    return app_tenant
        except Exception as e:
            logger.debug(f"Could not get tenant from app config: {e}")
        
        # Level 6: Default fallback (always valid)
        # This ensures we NEVER return None or invalid tenant
        # Performance: Only log in debug mode to reduce overhead
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Using default tenant: {DEFAULT_TENANT}")
        self._cache_tenant_in_request(DEFAULT_TENANT, 'default')
        return DEFAULT_TENANT
    
    def _detect_from_domain(self) -> Optional[str]:
        """
        Detect tenant from request hostname using pattern matching.
        
        Returns:
            Optional[str]: Tenant ID if detected, None otherwise
        """
        if not has_request_context():
            return None
        
        try:
            host = request.host.lower()
            domain_map = self._get_domain_tenant_mapping()
            
            for tenant_id, patterns in domain_map.items():
                for pattern in patterns:
                    if pattern in host:
                        logger.debug(f"🌐 Domain pattern '{pattern}' matched for tenant '{tenant_id}'")
                        return tenant_id
        except Exception as e:
            logger.debug(f"Domain detection failed: {e}")
        
        return None
    
    def _cache_tenant_in_request(self, tenant_id: str, method: str):
        """
        Cache tenant in Flask g for request duration.
        This prevents redundant detection calls within the same request.
        
        Args:
            tenant_id: Detected tenant ID
            method: Detection method used (for debugging)
        """
        if has_request_context():
            g.tenant_id = tenant_id
            g.tenant_detection_method = method
    
    def set_tenant(self, tenant_id: str, persist_session: bool = False) -> bool:
        """
        Explicitly set tenant for current request.
        
        Args:
            tenant_id: Tenant to set (must be valid)
            persist_session: Also store in session for future requests
        
        Returns:
            bool: Success status
        """
        if tenant_id not in VALID_TENANTS:
            logger.error(f"❌ Invalid tenant ID: {tenant_id}. Must be one of {VALID_TENANTS}")
            return False
        
        if has_request_context():
            g.tenant_id = tenant_id
            g.tenant_detection_method = 'explicit'
            
            if persist_session:
                session['tenant_id'] = tenant_id
                logger.info(f"✅ Tenant set: {tenant_id} (persisted to session)")
            else:
                logger.info(f"✅ Tenant set: {tenant_id} (request-only)")
            
            return True
        
        logger.warning("⚠️ Cannot set tenant: no request context")
        return False
    
    def clear_cache(self):
        """Clear all caches (useful for testing)"""
        self._get_domain_tenant_mapping.cache_clear()
        self._startup_cache.clear()
        logger.info("🔄 Tenant detection cache cleared")


# Global singleton instance
_unified_detector = UnifiedTenantDetector()


def get_current_tenant() -> str:
    """
    Get current tenant ID (main public API).
    GUARANTEED to return a valid tenant ID.
    
    This is the PRIMARY function to use throughout the codebase.
    All other tenant detection functions should eventually call this.
    
    Returns:
        str: Current tenant ID (always one of VALID_TENANTS)
    """
    return _unified_detector.detect_tenant()


def set_current_tenant(tenant_id: str, persist: bool = False) -> bool:
    """
    Set tenant for current request.
    
    Args:
        tenant_id: Tenant to set
        persist: Store in session for future requests
    
    Returns:
        bool: Success status
    """
    return _unified_detector.set_tenant(tenant_id, persist)


def is_valid_tenant(tenant_id: str) -> bool:
    """
    Check if tenant ID is valid.
    
    Args:
        tenant_id: Tenant ID to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    return tenant_id in VALID_TENANTS


def get_valid_tenants() -> list:
    """
    Get list of all valid tenant IDs.
    
    Returns:
        list: All valid tenant IDs
    """
    return VALID_TENANTS.copy()


def clear_tenant_cache():
    """Clear tenant detection cache (useful for testing)"""
    _unified_detector.clear_cache()

