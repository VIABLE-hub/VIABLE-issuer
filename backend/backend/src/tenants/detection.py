"""
Legacy Tenant Detection System

DEPRECATED: This module is deprecated in favor of unified_detector.py
Use unified_detector.get_current_tenant() instead.

This module is kept for backward compatibility only.
All new code should use unified_detector.py
"""

import os
import logging
import warnings
from typing import Optional
from flask import request, has_request_context, g, session, current_app
from functools import lru_cache

logger = logging.getLogger(__name__)

# Deprecation warning
warnings.warn(
    "tenants.detection is deprecated. Use tenants.unified_detector.get_current_tenant() instead.",
    DeprecationWarning,
    stacklevel=2
)

class TenantDetector:
    """
    Unified tenant detection with clear priority order and caching
    """
    
    # Detection priority order (highest to lowest)
    DETECTION_PRIORITY = [
        'flask_g_context',      # Highest: Flask g object (request-scoped)
        'session_stored',       # Session-stored tenant (user preference)
        'environment_var',      # Environment variable (deployment config)
        'domain_pattern',       # Domain-based detection (hostname analysis)
        'app_config',          # Flask app configuration
        'default_fallback'     # Lowest: Default to root tenant
    ]
    
    def __init__(self):
        self._tenant_cache = {}
        self._detection_cache = {}
    
    def detect_current_tenant(self, force_refresh: bool = False) -> Optional[str]:
        """
        Detect current tenant using unified priority system
        
        Args:
            force_refresh: Skip cache and re-detect
            
        Returns:
            str: Tenant ID (guaranteed to be valid or 'root')
        """
        
        # Use cache if available and not forcing refresh
        if not force_refresh and hasattr(g, 'current_tenant_id'):
            return g.current_tenant_id
        
        detected_tenant = None
        detection_method = None
        
        # Try each detection method in priority order
        for method in self.DETECTION_PRIORITY:
            try:
                if method == 'flask_g_context':
                    detected_tenant = self._detect_from_flask_g()
                elif method == 'session_stored':
                    detected_tenant = self._detect_from_session()
                elif method == 'environment_var':
                    detected_tenant = self._detect_from_environment()
                elif method == 'domain_pattern':
                    detected_tenant = self._detect_from_domain()
                elif method == 'app_config':
                    detected_tenant = self._detect_from_app_config()
                elif method == 'default_fallback':
                    detected_tenant = 'root'  # Always valid fallback
                
                if detected_tenant and self._is_valid_tenant(detected_tenant):
                    detection_method = method
                    break
                    
            except Exception as e:
                logger.debug(f"Tenant detection method '{method}' failed: {e}")
                continue
        
        # Ensure we always have a valid tenant
        if not detected_tenant or not self._is_valid_tenant(detected_tenant):
            detected_tenant = 'root'
            detection_method = 'emergency_fallback'
        
        # Cache in Flask g for request duration
        if has_request_context():
            g.current_tenant_id = detected_tenant
            g.tenant_detection_method = detection_method
        
        logger.info(f"🎯 Tenant detected: {detected_tenant} (method: {detection_method})")
        return detected_tenant
    
    def _detect_from_flask_g(self) -> Optional[str]:
        """Detect from Flask g context (highest priority - request scoped)"""
        if has_request_context() and hasattr(g, 'current_tenant_id'):
            return g.current_tenant_id
        return None
    
    def _detect_from_session(self) -> Optional[str]:
        """Detect from user session (user preference)"""
        if has_request_context() and 'tenant_id' in session:
            return session.get('tenant_id')
        return None
    
    def _detect_from_environment(self) -> Optional[str]:
        """Detect from environment variable (deployment config)"""
        # Check multiple environment variable names for compatibility
        for env_var in ['UNIVERSITY_TENANT', 'TENANT_ID', 'RUNTIME_TENANT']:
            tenant_id = os.environ.get(env_var, '').lower().strip()
            if tenant_id:
                return tenant_id
        return None
    
    def _detect_from_domain(self) -> Optional[str]:
        """Detect from request domain patterns"""
        if not has_request_context():
            return None
            
        try:
            host = request.host.lower()
            
            # Domain pattern matching
            domain_patterns = {
                'tub': ['tu-berlin', 'tub', 'tuberlin'],
                'fub': ['fu-berlin', 'fub', 'fuberlin'],
                'veritas': ['veritas', 'veritas-university'],
                'root': ['localhost', 'studentvc', '127.0.0.1', '192.168.']
            }
            
            for tenant_id, patterns in domain_patterns.items():
                for pattern in patterns:
                    if pattern in host:
                        return tenant_id
                        
        except Exception as e:
            logger.debug(f"Domain detection failed: {e}")
        
        return None
    
    def _detect_from_app_config(self) -> Optional[str]:
        """Detect from Flask app configuration"""
        try:
            return current_app.config.get('CURRENT_TENANT')
        except:
            return None
    
    def _is_valid_tenant(self, tenant_id: str) -> bool:
        """Validate that tenant ID is supported"""
        VALID_TENANTS = ['root', 'tub', 'fub', 'veritas']
        return tenant_id in VALID_TENANTS
    
    def set_tenant_for_request(self, tenant_id: str) -> bool:
        """
        Explicitly set tenant for current request
        
        Args:
            tenant_id: Tenant to set
            
        Returns:
            bool: Success status
        """
        if not self._is_valid_tenant(tenant_id):
            logger.error(f"Invalid tenant ID: {tenant_id}")
            return False
        
        if has_request_context():
            g.current_tenant_id = tenant_id
            g.tenant_detection_method = 'explicit_override'
            
            # Also store in session for persistence
            session['tenant_id'] = tenant_id
            
            logger.info(f"🎯 Tenant explicitly set: {tenant_id}")
            return True
        
        return False
    
    def clear_tenant_cache(self):
        """Clear tenant detection cache"""
        self._tenant_cache.clear()
        self._detection_cache.clear()
        
        if has_request_context() and hasattr(g, 'current_tenant_id'):
            delattr(g, 'current_tenant_id')
        
        logger.info("🔄 Tenant detection cache cleared")

# Global detector instance
_detector = TenantDetector()

def get_current_tenant_id(force_refresh: bool = False) -> str:
    """
    Get current tenant ID (guaranteed to return valid tenant)
    
    Args:
        force_refresh: Skip cache and re-detect
        
    Returns:
        str: Current tenant ID
    """
    return _detector.detect_current_tenant(force_refresh=force_refresh)

def set_current_tenant(tenant_id: str) -> bool:
    """
    Set tenant for current request
    
    Args:
        tenant_id: Tenant to set
        
    Returns:
        bool: Success status
    """
    return _detector.set_tenant_for_request(tenant_id)

def clear_tenant_detection_cache():
    """Clear tenant detection cache"""
    _detector.clear_tenant_cache() 