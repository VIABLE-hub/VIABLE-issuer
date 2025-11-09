"""
Tenant Middleware
Automatically sets tenant context for every request

Uses UnifiedTenantDetector as single source of truth for tenant detection.
"""

import logging
from flask import request, g, current_app
from functools import wraps

from .unified_detector import get_current_tenant, set_current_tenant

logger = logging.getLogger(__name__)

class TenantMiddleware:
    """
    Middleware to handle tenant context for requests
    """
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        # Register before_request handler
        app.before_request(self._set_tenant_context)
        
        # Register after_request handler for cleanup
        app.after_request(self._cleanup_tenant_context)
        
        logger.info("🔧 Tenant middleware initialized")
    
    def _set_tenant_context(self):
        """
        Set tenant context before each request.
        Uses UnifiedTenantDetector for consistent detection.
        """
        try:
            # Get current tenant ID using unified detector
            # This will use cached g.tenant_id if available, or detect fresh
            tenant_id = get_current_tenant()
            
            # Store in request context (unified detector already did this, but ensure it's set)
            g.tenant_id = tenant_id
            g.tenant_middleware_active = True
            
            # Log tenant detection for debugging (only in debug mode to reduce noise)
            # Performance: Only log if DEBUG level is enabled to avoid overhead
            if logger.isEnabledFor(logging.DEBUG):
                method = getattr(g, 'tenant_detection_method', 'unknown')
                logger.debug(f"Request tenant: {tenant_id} (method: {method}) | Path: {request.path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to set tenant context: {e}")
            # Set fallback (unified detector guarantees valid tenant, but safety first)
            g.tenant_id = 'root'
            g.tenant_middleware_active = False
    
    def _cleanup_tenant_context(self, response):
        """Clean up tenant context after each request"""
        # Tenant context automatically cleaned up when request ends
        return response

def tenant_required(tenant_id=None):
    """
    Decorator to require specific tenant context
    
    Args:
        tenant_id: Required tenant ID (optional - validates current if not specified)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if tenant middleware is active
            if not hasattr(g, 'tenant_middleware_active') or not g.tenant_middleware_active:
                logger.warning("⚠️ Tenant middleware not active - manually setting tenant")
                current_tenant = get_current_tenant_id()
                g.tenant_id = current_tenant
            
            # Check specific tenant requirement
            if tenant_id and g.tenant_id != tenant_id:
                logger.warning(f"❌ Tenant mismatch: required {tenant_id}, got {g.tenant_id}")
                return {'error': f'Access denied - tenant {tenant_id} required'}, 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_request_tenant_id():
    """
    Get tenant ID for current request.
    Uses unified detector for consistency.
    
    Returns:
        str: Current request tenant ID (always valid)
    """
    # Use unified detector (it will check g.tenant_id first, then detect)
    return get_current_tenant()

def switch_tenant_context(tenant_id: str, persist: bool = False):
    """
    Switch tenant context for current request.
    Uses unified detector for consistency.
    
    Args:
        tenant_id: New tenant ID
        persist: Store in session for future requests
        
    Returns:
        bool: Success status
    """
    return set_current_tenant(tenant_id, persist)

# Utility functions for backward compatibility
def ensure_tenant_context():
    """
    Ensure tenant context is set for current request.
    Uses unified detector for consistency.
    """
    # Unified detector always returns valid tenant, so just call it
    tenant_id = get_current_tenant()
    if not hasattr(g, 'tenant_id') or g.tenant_id != tenant_id:
        g.tenant_id = tenant_id
        logger.debug(f"🔧 Ensured tenant context: {tenant_id}")

def clear_tenant_context():
    """Clear tenant context for current request"""
    if hasattr(g, 'tenant_id'):
        delattr(g, 'tenant_id')
    if hasattr(g, 'tenant_middleware_active'):
        delattr(g, 'tenant_middleware_active')
    logger.debug("🧹 Cleared tenant context") 