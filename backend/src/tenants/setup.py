"""
Tenant Setup and Registration

This module registers all available tenant configurations with the central registry.
Called during application initialization to set up the multi-tenant system.
"""

import logging
from .registry import get_tenant_registry
from .instances.root_config import RootConfig
from .instances.tub.config import TUBerlinConfig
from .instances.fub.config import FUBerlinConfig

logger = logging.getLogger(__name__)

def register_all_tenants():
    """
    Register all available tenant configurations with the central registry.
    
    🚨 NUCLEAR FIX: BULLETPROOF 3-TENANT REGISTRATION 🚨
    Fixes the critical 4-tenant registration bug permanently!
    
    This function should be called during application initialization to
    set up the multi-tenant system with all available university tenants.
    """
    registry = get_tenant_registry()
    
    try:
        logger.info("🚨 NUCLEAR FIX: Starting bulletproof 3-tenant registration...")
        
        # 🚨 NUCLEAR CLEANUP: Clear ALL existing registrations to prevent corruption
        if hasattr(registry, '_tenants'):
            registry._tenants.clear()
        if hasattr(registry, '_tenant_instances'):
            registry._tenant_instances.clear()
        if hasattr(registry, '_domain_patterns'):
            registry._domain_patterns.clear()
        logger.info("✅ NUCLEAR - Cleared ALL existing tenant registrations and patterns")
        
        # 🚨 BULLETPROOF: Register exactly 3 tenants - NO MORE, NO LESS
        tenants_to_register = [
            ('root', RootConfig, "Root tenant (default)"),
            ('tub', TUBerlinConfig, "TU Berlin tenant"),
            ('fub', FUBerlinConfig, "FU Berlin tenant")
        ]
        
        # Register each tenant with validation
        registered_count = 0
        for tenant_id, tenant_class, description in tenants_to_register:
            # Double-check tenant ID is allowed
            if tenant_id not in ['root', 'tub', 'fub']:
                raise Exception(f"NUCLEAR ERROR: Invalid tenant ID '{tenant_id}' - only root, tub, fub allowed!")
            
            registry.register_tenant(tenant_id, tenant_class)
            registered_count += 1
            logger.info(f"✅ NUCLEAR - Registered {description}: {tenant_id}")
        
        # 🚨 CRITICAL VALIDATION: Ensure exactly 3 tenants, no duplicates
        available_tenants = registry.get_available_tenants()
        
        if len(available_tenants) != 3:
            raise Exception(f"NUCLEAR ERROR: Expected exactly 3 tenants, got {len(available_tenants)}: {available_tenants}")
        
        expected_tenants = {'root', 'tub', 'fub'}
        if set(available_tenants) != expected_tenants:
            raise Exception(f"NUCLEAR ERROR: Wrong tenants registered. Expected {expected_tenants}, got {set(available_tenants)}")
            
        if registered_count != 3:
            raise Exception(f"NUCLEAR ERROR: Registration count mismatch. Expected 3, registered {registered_count}")
        
        # 🚨 FINAL VALIDATION: No forbidden tenant IDs
        forbidden_tenants = {'tuberlin', 'fuberlin', 'tu-berlin', 'fu-berlin'}
        if any(tenant in available_tenants for tenant in forbidden_tenants):
            raise Exception(f"NUCLEAR ERROR: Forbidden tenants detected: {available_tenants}")
        
        logger.info(f"✅ NUCLEAR SUCCESS: Exactly 3 tenants registered: {sorted(available_tenants)}")
        logger.info(f"✅ NUCLEAR SUCCESS: Total registered tenants: {len(available_tenants)} - ['root', 'tub', 'fub']")
        return True
        
    except Exception as e:
        logger.error(f"❌ NUCLEAR FAILURE: Failed to register tenants: {e}")
        raise e

def initialize_tenant_system():
    """
    Initialize the complete tenant system.
    
    This function:
    1. Registers all tenant configurations
    2. Ensures tenant directory structures exist
    3. Sets up backward compatibility
    4. Validates the tenant system
    """
    logger.info("Initializing StudentVC multi-tenant system...")
    
    # Step 1: Register all tenants
    if not register_all_tenants():
        logger.error("Failed to register tenants - tenant system not initialized")
        return False
    
    # Step 2: Ensure tenant directories exist
    registry = get_tenant_registry()
    for tenant_id in registry.get_available_tenants():
        tenant_config = registry.get_tenant_config(tenant_id)
        if tenant_config:
            try:
                tenant_config.ensure_directories()
                logger.info(f"Ensured directories for tenant: {tenant_id}")
            except Exception as e:
                logger.warning(f"Could not ensure directories for tenant {tenant_id}: {e}")
    
    # Step 3: Test tenant detection
    try:
        current_tenant = registry.detect_current_tenant()
        if current_tenant:
            logger.info(f"Current tenant detected: {current_tenant.tenant_id} ({current_tenant.short_name})")
        else:
            logger.info("No specific tenant detected - using default configuration")
    except Exception as e:
        logger.warning(f"Tenant detection test failed: {e}")
    
    logger.info("StudentVC multi-tenant system initialized successfully")
    return True

def get_tenant_status():
    """
    Get current status of the tenant system for debugging/monitoring.
    
    Returns:
        dict: Status information about the tenant system
    """
    registry = get_tenant_registry()
    
    status = {
        "system_initialized": True,
        "available_tenants": [],
        "current_tenant": None,
        "tenant_configs": {}
    }
    
    try:
        # Get available tenants
        available_tenants = registry.get_available_tenants()
        status["available_tenants"] = available_tenants
        
        # Get current tenant
        current_tenant = registry.detect_current_tenant()
        if current_tenant:
            status["current_tenant"] = {
                "id": current_tenant.tenant_id,
                "name": current_tenant.name,
                "short_name": current_tenant.short_name,
                "primary_color": current_tenant.primary_color
            }
        
        # Get tenant configs
        for tenant_id in available_tenants:
            tenant_config = registry.get_tenant_config(tenant_id)
            if tenant_config:
                status["tenant_configs"][tenant_id] = {
                    "name": tenant_config.name,
                    "short_name": tenant_config.short_name,
                    "database_path": tenant_config.database_path,
                    "keys_path": tenant_config.keys_path,
                    "static_path": tenant_config.static_path
                }
    
    except Exception as e:
        status["error"] = str(e)
        status["system_initialized"] = False
        logger.error(f"Error getting tenant status: {e}")
    
    return status 