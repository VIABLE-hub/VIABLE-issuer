"""
Tenant Middleware
Automatically sets tenant context for every request
"""

import logging
from flask import request, g, current_app
from functools import wraps

from .detection import get_current_tenant_id, set_current_tenant

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
        """Set tenant context before each request"""
        try:
            # Get current tenant ID
            tenant_id = get_current_tenant_id()
            
            # Store in request context
            g.tenant_id = tenant_id
            g.tenant_middleware_active = True
            
            # Log tenant detection for debugging
            logger.debug(f"🎯 Request tenant: {tenant_id} | Path: {request.path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to set tenant context: {e}")
            # Set fallback
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
    Get tenant ID for current request
    
    Returns:
        str: Current request tenant ID
    """
    if hasattr(g, 'tenant_id'):
        return g.tenant_id
    
    # Fallback to detection
    return get_current_tenant_id()

def switch_tenant_context(tenant_id: str):
    """
    Switch tenant context for current request
    
    Args:
        tenant_id: New tenant ID
        
    Returns:
        bool: Success status
    """
    try:
        if set_current_tenant(tenant_id):
            g.tenant_id = tenant_id
            logger.info(f"🔄 Switched request tenant to: {tenant_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Failed to switch tenant context: {e}")
        return False

# Utility functions for backward compatibility
def ensure_tenant_context():
    """Ensure tenant context is set for current request"""
    if not hasattr(g, 'tenant_id'):
        g.tenant_id = get_current_tenant_id()
        logger.debug(f"🔧 Ensured tenant context: {g.tenant_id}")

def clear_tenant_context():
    """Clear tenant context for current request"""
    if hasattr(g, 'tenant_id'):
        delattr(g, 'tenant_id')
    if hasattr(g, 'tenant_middleware_active'):
        delattr(g, 'tenant_middleware_active')
    logger.debug("🧹 Cleared tenant context") 