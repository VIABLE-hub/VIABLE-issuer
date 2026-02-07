script = ["dummy"]
allowed_list = script


def valid_user_rerout(input) -> bool:
    return input in allowed_list

from src.models import SystemSettings
from flask import current_app, request
import socket
import logging
import os

logger = logging.getLogger(__name__)

def get_server_url_no_context():
    """
    🌐 Get server URL without Flask context (for Docker environments)
    
    This function works in any environment and prioritizes external configuration.
    """
    try:
        external_url = os.environ.get('EXTERNAL_SERVER_URL')
        use_external = os.environ.get('USE_EXTERNAL_URL', 'false').lower() == 'true'
        
        if use_external and external_url:
            logger.info(f"🌍 Using EXTERNAL_SERVER_URL (no context): {external_url}")
            return external_url.rstrip('/')
        
        # Check for NGROK URL in environment
        ngrok_url = os.environ.get('NGROK_URL')
        if ngrok_url:
            logger.info(f"🌐 Using NGROK_URL from environment: {ngrok_url}")
            return ngrok_url.rstrip('/')
        
        if os.environ.get('DOCKER_MODE') == 'true':
            local_ip = get_local_ip()
            if local_ip.startswith('172.'):
                logger.warning(f"⚠️ Docker internal IP detected ({local_ip}) - mobile wallets cannot reach this!")
                logger.warning(f"⚠️ Set EXTERNAL_SERVER_URL and USE_EXTERNAL_URL=true for production")
        
        # Fallback to local IP with default port
        local_ip = get_local_ip()
        port = os.environ.get('SERVER_PORT', '8080')
        fallback_url = f"https://{local_ip}:{port}"
        
        logger.info(f"⚠️ No external/NGROK URL configured, using local IP: {fallback_url}")
        return fallback_url
        
    except Exception as e:
        logger.error(f"❌ Error getting server URL (no context): {e}")
        return "https://localhost:8080"

def get_current_server_url():
    """
    🌐 Get current server URL dynamically from the request headers.
    
    This ensures compatibility with reverse proxies (Caddy, Nginx) and local dev.
    It removes the need for manual network configuration or database storage.
    """
    try:
        # 1. Try to use the Flask Request context (Best for handling Proxies automatically)
        if request:
            # request.url_root gives 'https://example.com/' (including scheme and host)
            # rstrip('/') removes the trailing slash
            # Flask handles X-Forwarded-Host/Proto if ProxyFix is used or if the WSGI server sets environ correctly.
            # Even without ProxyFix, request.host_url is usually the best best for the verification URL.
            url = request.url_root.rstrip('/')
            logger.debug(f"🌐 Determined Server URL from request: {url}")
            return url
    except Exception as e:
        # No request context (e.g. background thread), or request import failed (unlikely)
        logger.debug(f"ℹ️ No request context available ({e}) - falling back to environment/local")
        pass

    # 2. Fallback: Environment Variables (Good for Docker/Dev overrides)
    external_url = os.environ.get('EXTERNAL_SERVER_URL')
    if external_url:
        logger.info(f"🌍 Using EXTERNAL_SERVER_URL from env: {external_url}")
        return external_url.rstrip('/')
    
    # 3. Fallback: Local IP (Last resort)
    try:
        local_ip = get_local_ip()
        port = os.environ.get('PORT', '8080')
        fallback_url = f"https://{local_ip}:{port}"
        logger.info(f"⚠️ Using Local IP fallback: {fallback_url}")
        return fallback_url
    except Exception as e:
        logger.error(f"❌ Error generating fallback URL: {e}")
        return "https://localhost:8080"

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
