"""
Tenant Configuration API Endpoints
Provides API endpoints for tenant configuration management
"""

from flask import Blueprint, jsonify, request, current_app
import logging
import os

logger = logging.getLogger(__name__)

def register_routes(settings_bp):
    """Register tenant configuration routes"""
    
    @settings_bp.route('/api/tenant/debug', methods=['GET'])
    def api_tenant_debug():
        """Debug tenant detection"""
        debug_info = {
            'app_config_tenant': current_app.config.get('CURRENT_TENANT'),
            'runtime_tenant_env': os.environ.get('RUNTIME_TENANT'),
            'university_tenant_env': os.environ.get('TENANT_ID'),
            'all_env_vars': {k: v for k, v in os.environ.items() if 'tenant' in k.lower()},
            'app_config_keys': list(current_app.config.keys()),
            'database_uri': current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        }
        
        return jsonify({
            "status": "success",
            "debug": debug_info
        })
    
    @settings_bp.route('/api/tenant/config', methods=['GET'])
    def api_tenant_config_get():
        """Get current tenant configuration for settings page"""
        try:
            # 🚀 PERFECTION: Use new unified tenant system
            from ..tenants import get_tenant_config, get_current_tenant_id
            
            tenant_id = get_current_tenant_id()
            tenant_config = get_tenant_config(tenant_id)
            
            logger.info(f"🔧 ✅ Using new tenant system - tenant: {tenant_id}")
            
            if not tenant_config:
                logger.error(f"❌ Failed to get tenant config for: {tenant_id}")
                return jsonify({
                    "status": "error",
                    "message": f"Tenant config not found: {tenant_id}"
                }), 404
            
            logger.info(f"✅ Loaded complete tenant config for: {tenant_id}")
            
            # Get or create tenant settings
            from ..models import TenantSettings
            tenant_settings = TenantSettings.get_or_create_default(tenant_id)
            
            # Get network settings with NGROK URL priority
            network_settings = tenant_settings.network_settings or {}
            saved_ngrok_url = network_settings.get('ngrok_url', '').strip()
            
            # Get the current server URL (considers NGROK settings)
            from ..utils import get_current_server_url
            server_url = get_current_server_url()
            
            # Use saved NGROK URL if available, otherwise use detected server URL
            effective_ngrok_url = saved_ngrok_url if saved_ngrok_url else server_url
            
            logger.info(f"🎯 Tenant config GET - Returning config for {tenant_id}")
            
            return jsonify({
                "status": "success",
                "config": {
                    "tenant_id": tenant_config.get('tenant_id', tenant_id),
                    "tenant_name": tenant_config.get('name', tenant_id),
                    "university_name": tenant_config.get('name', tenant_id),
                    "short_name": tenant_config.get('short_name', tenant_id.upper()),
                    "primary_color": tenant_config.get('primary_color', '#003f7f'),
                    "ngrok_url": effective_ngrok_url,
                    "server_url": server_url,
                    "network_settings": network_settings,
                    "appearance_settings": tenant_settings.appearance_settings or {},
                    "trust_settings": tenant_settings.trust_settings or {},
                    "advanced_settings": tenant_settings.advanced_settings or {}
                }
            })
            
        except Exception as e:
            import traceback
            logger.error(f"❌ CRITICAL ERROR in tenant config GET: {e}")
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            
            # Return error instead of fallback for debugging
            return jsonify({
                "status": "error",
                "message": f"Tenant config error: {str(e)}",
                "traceback": traceback.format_exc()
            }), 500

    @settings_bp.route('/api/tenant/config', methods=['POST'])
    def api_tenant_config_post():
        """Save tenant configuration"""
        try:
            from ..tenants.registry import get_tenant_registry
            from ..models import TenantSettings, db
            from sqlalchemy.orm.attributes import flag_modified
            import os
            
            # 🚨 CRITICAL FIX: Use app config first, then tenant detection
            tenant_id = (current_app.config.get('CURRENT_TENANT') or 
                        os.environ.get('RUNTIME_TENANT') or 
                        os.environ.get('TENANT_ID', '').lower() or 
                        'root')
            
            registry = get_tenant_registry()
            current_tenant = registry.get_tenant_config(tenant_id)
            
            # Fallback to root if no tenant detected
            if not current_tenant:
                current_tenant = registry.get_tenant_config('root')
            
            if not current_tenant:
                return jsonify({
                    "status": "error",
                    "message": f"Tenant config not found: {tenant_id}"
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    "status": "error", 
                    "message": "No data provided"
                }), 400
            
            # Get or create tenant settings
            effective_tenant_id = current_tenant.get('tenant_id', tenant_id) if isinstance(current_tenant, dict) else getattr(current_tenant, 'tenant_id', tenant_id)
            tenant_settings = TenantSettings.get_or_create_default(effective_tenant_id)
            
            # Update NGROK URL if provided
            ngrok_url = data.get('ngrok_url', '').strip()
            if ngrok_url:
                network_settings = tenant_settings.network_settings or {}
                network_settings['ngrok_url'] = ngrok_url
                network_settings['connection_mode'] = 'ngrok'
                network_settings['use_ngrok'] = True  # 🚨 FIX: Set use_ngrok flag
                
                tenant_settings.network_settings = network_settings
                flag_modified(tenant_settings, 'network_settings')
                
                # Update Flask config SERVER_URL
                current_app.config['SERVER_URL'] = ngrok_url
                
                logger.info(f"🌐 Updated NGROK URL for {effective_tenant_id}: {ngrok_url}")
            
            # Update other settings if provided
            if 'appearance_settings' in data:
                tenant_settings.appearance_settings = data['appearance_settings']
                flag_modified(tenant_settings, 'appearance_settings')
            
            if 'trust_settings' in data:
                tenant_settings.trust_settings = data['trust_settings']
                flag_modified(tenant_settings, 'trust_settings')
            
            if 'advanced_settings' in data:
                tenant_settings.advanced_settings = data['advanced_settings']
                flag_modified(tenant_settings, 'advanced_settings')
            
            # Save to database
            db.session.commit()
            
            logger.info(f"✅ Tenant config saved for {effective_tenant_id}")
            
            return jsonify({
                "status": "success",
                "message": "Configuration saved successfully",
                "tenant_id": effective_tenant_id
            })
            
        except Exception as e:
            logger.error(f"Error saving tenant config: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500 