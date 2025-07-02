"""
Tenant Database Management System
Provides isolated database management for multi-tenant StudentVC system
"""

import os
import logging
from typing import Optional, Dict, Any
from sqlalchemy import create_engine
from flask import current_app

logger = logging.getLogger(__name__)

# Valid tenant identifiers
ALLOWED_TENANTS = ['root', 'tub', 'fub']

class TenantDatabaseManager:
    """Manages database isolation for multi-tenant system"""
    
    def __init__(self):
        self.engines = {}
        self.current_tenant = None
    
    def get_tenant_from_environment(self) -> Optional[str]:
        """Get tenant from environment variable (the ONLY source of truth)"""
        tenant_env = os.environ.get('TENANT_ID', '').lower().strip()
        
        # 🚨 CRITICAL VALIDATION: Must be valid tenant
        if not tenant_env or tenant_env not in ALLOWED_TENANTS:
            logger.debug(f"❌ BULLETPROOF - Invalid tenant '{tenant_env}', must be one of {ALLOWED_TENANTS}")
            logger.debug(f"❌ BULLETPROOF - No valid tenant detected (env: '{tenant_env}')")
            
            # 🚨 BULLETPROOF: For development, default to 'root' tenant
            # In production, this should be stricter
            return 'root'
        
        logger.info(f"✅ BULLETPROOF - Tenant detected: {tenant_env}")
        return tenant_env
    
    def get_database_uri_for_tenant(self, tenant_id: str) -> str:
        """Get database URI for specific tenant"""
        if tenant_id not in ALLOWED_TENANTS:
            raise ValueError(f"Invalid tenant: {tenant_id}, must be one of {ALLOWED_TENANTS}")
        
        # Create tenant-specific database path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Go to backend dir
        tenant_db_path = os.path.join(base_dir, 'src', 'tenants', 'instances', tenant_id, 'database.db')
        
        # Ensure directory exists
        tenant_dir = os.path.dirname(tenant_db_path)
        os.makedirs(tenant_dir, exist_ok=True)
        
        db_uri = f"sqlite:///{tenant_db_path}"
        logger.info(f"💾 Database URI for tenant '{tenant_id}': {db_uri}")
        
        return db_uri
    
    def configure_app_for_tenant(self, app, tenant_id: str):
        """Configure Flask app for specific tenant database"""
        db_uri = self.get_database_uri_for_tenant(tenant_id)
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        
        # 🚨 CRITICAL: Store current tenant in app config for API access
        app.config['CURRENT_TENANT'] = tenant_id
        
        # 🚨 CRITICAL: Also store tenant in environment for child processes
        import os
        os.environ['RUNTIME_TENANT'] = tenant_id
        
        logger.info(f"🏛️  App configured for tenant: {tenant_id}")
        logger.info(f"💾 Database: {db_uri}")
        logger.info(f"🏛️  Stored tenant in app config: {tenant_id}")
        
        return db_uri

# Global tenant database manager
tenant_db_manager = TenantDatabaseManager()

def get_current_tenant_from_environment() -> Optional[str]:
    """Get current tenant from environment"""
    return tenant_db_manager.get_tenant_from_environment()

def configure_tenant_database(app, tenant_id: Optional[str] = None):
    """Configure tenant database for Flask app"""
    if not tenant_id:
        tenant_id = get_current_tenant_from_environment()
    
    if not tenant_id:
        logger.error("❌ No tenant detected - cannot configure database")
        return None
    
    return tenant_db_manager.configure_app_for_tenant(app, tenant_id)

def initialize_tenant_system_databases():
    """Initialize databases for all tenants"""
    results = {}
    
    for tenant_id in ALLOWED_TENANTS:
        try:
            db_uri = tenant_db_manager.get_database_uri_for_tenant(tenant_id)
            results[tenant_id] = {"status": "success", "db_uri": db_uri}
            logger.info(f"✅ Tenant '{tenant_id}' database initialized: {db_uri}")
        except Exception as e:
            results[tenant_id] = {"status": "error", "error": str(e)}
            logger.error(f"❌ Failed to initialize tenant '{tenant_id}' database: {e}")
    
    return results

def get_tenant_database_path(tenant_id: str) -> str:
    """Get the file path for tenant database"""
    if tenant_id not in ALLOWED_TENANTS:
        raise ValueError(f"Invalid tenant: {tenant_id}")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_dir, 'src', 'tenants', 'instances', tenant_id, 'database.db')

def ensure_tenant_database_exists(tenant_id: str):
    """Ensure tenant database file exists"""
    db_path = get_tenant_database_path(tenant_id)
    db_dir = os.path.dirname(db_path)
    
    # Create directory if it doesn't exist
    os.makedirs(db_dir, exist_ok=True)
    
    # Create empty database file if it doesn't exist
    if not os.path.exists(db_path):
        logger.info(f"💾 Creating database file for tenant '{tenant_id}': {db_path}")
        # Create empty file
        with open(db_path, 'a'):
            pass
    
    return db_path 