from src import create_app, socketio
import os
import socket

# Database cleanup disabled to prevent startup issues
# if os.path.exists("instance/database.db"):
#     os.remove("instance/database.db")

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if not ip.startswith('127.'):
            return ip
    except (OSError, socket.error) as e:
        print(f"Warning: Could not determine local IP: {e}")
    return "127.0.0.1"

def get_ssl_context():
    """Get SSL context based on environment (Docker vs development)"""
    # DOCKER NETWORK FIX: Use Docker-specific SSL certificates if available
    if os.environ.get('DOCKER_MODE') == 'true':
        ssl_cert_path = os.environ.get('SSL_CERT_PATH', '/app/docker-cert.pem')
        ssl_key_path = os.environ.get('SSL_KEY_PATH', '/app/docker-key.pem')
        
        # Check if Docker SSL certificates exist
        if os.path.exists(ssl_cert_path) and os.path.exists(ssl_key_path):
            import logging
            logging.getLogger(__name__).info(f"Using Docker SSL certificates: {ssl_cert_path}")
            return (ssl_cert_path, ssl_key_path)
        else:
            import logging
            logging.getLogger(__name__).warning("Docker SSL certificates not found, falling back to adhoc")
            return "adhoc"
    else:
        # Development mode: use adhoc certificates
        import logging
        logging.getLogger(__name__).info("Using adhoc SSL certificates for development")
        return "adhoc"

def get_server_configuration():
    """Get server configuration based on environment"""
    LOCAL_IP = get_local_ip()
    FLASK_PORT = int(os.environ.get('SERVER_PORT', 8080))
    
    # Docker mode configuration
    import logging
    logger = logging.getLogger(__name__)
    
    if os.environ.get('DOCKER_MODE') == 'true':
        host = "0.0.0.0"  # Allow external connections in Docker
        ssl_context = get_ssl_context()
        logger.info("Docker mode detected")
        logger.info(f"Binding to: {host}:{FLASK_PORT}")
        logger.info(f"SSL Context: {ssl_context}")
        logger.info(f"Local IP: {LOCAL_IP}")
        logger.info("Network mode: Docker container with external access")
    else:
        # Development mode configuration
        host = "0.0.0.0"
        ssl_context = "adhoc"
        logger.info("Development mode detected")
        logger.info(f"Binding to: {host}:{FLASK_PORT}")
        logger.info(f"SSL Context: {ssl_context}")
        logger.info(f"Local IP: {LOCAL_IP}")
        logger.info("Network mode: Local development with WiFi access")
    
    return {
        'host': host,
        'port': FLASK_PORT,
        'ssl_context': ssl_context,
        'local_ip': LOCAL_IP
    }
    
# remove this for seperate tenants !!!
def ensure_tenant_database_isolation():
    """CRITICAL: Ensure tenant database isolation"""
    import logging
    logger = logging.getLogger(__name__)
    
    tenant_env = os.environ.get('TENANT_ID', '').lower().strip()
    
    if not tenant_env:
        logger.warning("WARNING: No TENANT_ID environment variable set, using 'root' as default")
        tenant_env = 'root'
    
    logger.info(f"TENANT DETECTED: {tenant_env.upper()}")
    logger.info("DATABASE ISOLATION: Each tenant uses separate database")
    
    # Initialize tenant database system
    try:
        from src.tenants.database import TenantDatabaseManager
        db_manager = TenantDatabaseManager()
        
        # Initialize all tenant databases
        tenant_results = {}
        for tenant_id in ['root', 'tub', 'fub', 'veritas']:
            try:
                db_uri = db_manager.get_database_uri_for_tenant(tenant_id)
                tenant_results[tenant_id] = {
                    'status': 'success',
                    'db_uri': db_uri
                }
            except Exception as e:
                tenant_results[tenant_id] = {
                    'status': 'error', 
                    'error': str(e)
                }
        
        logger.info(f"Tenant database initialization results: {tenant_results}")
        logger.info(f"Current active tenant: {tenant_env}")
        
        return tenant_env
        
    except Exception as e:
        logger.error(f"Tenant database initialization failed: {e}")
        logger.info(f"Falling back to simple tenant: {tenant_env}")
        return tenant_env

if __name__ == "__main__":
    # CRITICAL: Initialize tenant system before creating app
    # remove this for seperate tenants!!!
    current_tenant = ensure_tenant_database_isolation()

    # Set tenant in environment for app creation (tenant middleware uses this)
    # remove this for seperate tenants!!!
    os.environ['TENANT_ID'] = current_tenant

    app = create_app()
    
    # DOCKER COMPATIBILITY: Set debug mode based on environment
    app.config['DEBUG'] = os.environ.get('DOCKER_MODE') != 'true'

    # Store current tenant in app config
    import logging
    logger = logging.getLogger(__name__)
    # remove this for seperate tenants!!!
    app.config['CURRENT_TENANT'] = current_tenant
    logger.info(f"App configured for tenant: {current_tenant}")
    
    # Note: TenantMiddleware is now initialized inside create_app() for optimal performance
    # No need for post-creation initialization

    # NGROK DETECTION REMOVED: Now handled dynamically in utils.py per-request
    # This prevents Flask app context errors and ensures fresh NGROK URL lookup each time

    # Get server configuration
    server_config = get_server_configuration()
    
    logger.info("Starting StudentVC server...")
    logger.info("")
    logger.info("NGROK URLS: Server URLs now retrieved dynamically from tenant database")
    logger.info("Set NGROK URLs via tenant config API and they will be used immediately")
    logger.info("")
    logger.info("MOBILE WALLET ACCESS:")
    logger.info(f"   - Local network: https://{server_config['local_ip']}:{server_config['port']}")
    logger.info(f"   - NGROK: Configure via Settings -> Network -> NGROK Domain")
    logger.info("")
    
    try:
        # ENHANCED SOCKET.IO: Configure for Docker compatibility
        socketio.run(
            app,
            debug=app.config['DEBUG'],
            host=server_config['host'],
            port=server_config['port'],
            ssl_context=server_config['ssl_context'],
            allow_unsafe_werkzeug=True,
            log_output=False if os.environ.get('DOCKER_MODE') == 'true' else True
        )
    except Exception as e:
        logger.error(f"Server startup error: {e}")
        if os.environ.get('DOCKER_MODE') == 'true':
            logger.error("Docker troubleshooting:")
            logger.error("   - Check if ports are properly exposed")
            logger.error("   - Verify SSL certificate generation")
            logger.error("   - Check Docker network configuration")
        else:
            logger.error("Try: pkill -f 'python.*main.py' to kill existing processes")
