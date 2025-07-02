script = ["dummy"]
allowed_list = script


def valid_user_rerout(input) -> bool:
    return input in allowed_list

from src.models import TenantSettings
from flask import current_app
import socket
import logging
import os

logger = logging.getLogger(__name__)

def get_current_server_url():
    """
    🌐 Get current server URL using unified tenant configuration system
    
    Returns:
        str: The current server URL (either tenant NGROK URL or default local IP)
    """
    try:
        # First check if we have a current tenant
        tenant_id = (current_app.config.get('CURRENT_TENANT') or 
                     os.environ.get('RUNTIME_TENANT') or 
                     os.environ.get('TENANT_ID', '').lower() or 
                     'root')
        
        logger.info(f"🔍 Getting server URL for tenant: {tenant_id}")
        
        # Get tenant settings from database
        tenant_settings = TenantSettings.get_or_create_default(tenant_id)
        network_settings = tenant_settings.network_settings or {}
        
        # Check if NGROK is enabled and URL is configured
        if network_settings.get('use_ngrok') and network_settings.get('ngrok_url'):
            ngrok_url = network_settings['ngrok_url'].strip()
            if ngrok_url:
                logger.info(f"🌐 Using NGROK URL from tenant settings: {ngrok_url}")
                return ngrok_url
        
        # Check Flask config for SERVER_URL
        server_url = current_app.config.get('SERVER_URL')
        if server_url and not server_url.startswith('https://localhost'):
            logger.info(f"🌐 Using SERVER_URL from Flask config: {server_url}")
            return server_url
        
        # Fallback to local IP
        local_ip = get_local_ip()
        port = current_app.config.get('PORT', 8080)
        fallback_url = f"https://{local_ip}:{port}"
        
        logger.info(f"⚠️ No NGROK URL configured, using local IP: {fallback_url}")
        return fallback_url
        
    except Exception as e:
        logger.error(f"🚨 get_current_server_url() failed: {e}")
        
        # Emergency fallback
        local_ip = get_local_ip()
        emergency_url = f"https://{local_ip}:8080"
        
        logger.error(f"🚨 Using emergency fallback: {emergency_url}")
        return emergency_url

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if not ip.startswith('127.'):
            return ip
    except:
        pass
    return "127.0.0.1"
