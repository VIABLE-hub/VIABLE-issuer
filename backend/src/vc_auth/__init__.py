"""
VC-Based Authentication Module

This module provides Verifiable Credential-based authentication for StudentVC.
Users can authenticate using their issued login credentials instead of passwords.

Architecture:
- LoginCredential: Database model for issued login VCs
- LoginSession: Active login sessions
- Issuer: Admin interface for issuing login credentials
- Verifier: Verification endpoint for login presentations
- Session: Flask-Login integration

Usage:
    from src.vc_auth import vc_auth_bp
    app.register_blueprint(vc_auth_bp, url_prefix='/vc-auth')
"""

from flask import Blueprint
from logging import getLogger

logger = getLogger("VC_AUTH")

# Create the blueprint
vc_auth_bp = Blueprint('vc_auth', __name__, url_prefix='/vc-auth')
vc_admin_bp = Blueprint('vc_admin', __name__, url_prefix='/admin/vc-auth')

# Import routes to register them with blueprints
# Note: Import after blueprint creation to avoid circular imports
def init_vc_auth():
    """Initialize VC authentication module"""
    try:
        # Import models to ensure they're registered
        from . import models
        
        # Import routes
        from . import issuer_routes
        from . import verifier_routes
        from . import admin_routes
        
        logger.info("✅ VC Authentication module initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize VC Authentication module: {e}")
        return False

__all__ = ['vc_auth_bp', 'vc_admin_bp', 'init_vc_auth']

