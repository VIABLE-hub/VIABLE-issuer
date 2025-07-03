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
    except:
        pass
    return "127.0.0.1"

def get_ssl_context():
    """Get SSL context based on environment (Docker vs development)"""
    # 🚀 DOCKER NETWORK FIX: Use Docker-specific SSL certificates if available
    if os.environ.get('DOCKER_MODE') == 'true':
        ssl_cert_path = os.environ.get('SSL_CERT_PATH', '/app/docker-cert.pem')
        ssl_key_path = os.environ.get('SSL_KEY_PATH', '/app/docker-key.pem')
        
        # Check if Docker SSL certificates exist
        if os.path.exists(ssl_cert_path) and os.path.exists(ssl_key_path):
            print(f"🔒 Using Docker SSL certificates: {ssl_cert_path}")
            return (ssl_cert_path, ssl_key_path)
        else:
            print("⚠️  Docker SSL certificates not found, falling back to adhoc")
            return "adhoc"
    else:
        # Development mode: use adhoc certificates
        print("🔒 Using adhoc SSL certificates for development")
        return "adhoc"

def get_server_configuration():
    """Get server configuration based on environment"""
    LOCAL_IP = get_local_ip()
    FLASK_PORT = int(os.environ.get('SERVER_PORT', 8080))
    
    # Docker mode configuration
    if os.environ.get('DOCKER_MODE') == 'true':
        host = "0.0.0.0"  # Allow external connections in Docker
        ssl_context = get_ssl_context()
        print("🐳 Docker mode detected")
        print(f"🌐 Binding to: {host}:{FLASK_PORT}")
        print(f"🔒 SSL Context: {ssl_context}")
        print(f"🌐 Local IP: {LOCAL_IP}")
        print("📡 Network mode: Docker container with external access")
    else:
        # Development mode configuration
        host = "0.0.0.0"
        ssl_context = "adhoc"
        print("🛠️  Development mode detected")
        print(f"🌐 Binding to: {host}:{FLASK_PORT}")
        print(f"🔒 SSL Context: {ssl_context}")
        print(f"🌐 Local IP: {LOCAL_IP}")
        print("📡 Network mode: Local development with WiFi access")
    
    return {
        'host': host,
        'port': FLASK_PORT,
        'ssl_context': ssl_context,
        'local_ip': LOCAL_IP
    }

def ensure_tenant_database_isolation():
    """🚨 CRITICAL: Ensure tenant database isolation"""
    tenant_env = os.environ.get('TENANT_ID', '').lower().strip()
    
    if not tenant_env:
        print("⚠️  No TENANT_ID environment variable set, using 'root' as default")
        tenant_env = 'root'
    
    print(f"🏛️  TENANT DETECTED: {tenant_env.upper()}")
    print("💾 DATABASE ISOLATION: Each tenant uses separate database")
    
    # Initialize tenant database system
    try:
        from src.tenants.database import TenantDatabaseManager
        db_manager = TenantDatabaseManager()
        
        # Initialize all tenant databases
        tenant_results = {}
        for tenant_id in ['root', 'tub', 'fub']:
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
        
        print(f"📊 Tenant database initialization results: {tenant_results}")
        print(f"✅ Current active tenant: {tenant_env}")
        
        return tenant_env
        
    except Exception as e:
        print(f"❌ Tenant database initialization failed: {e}")
        print(f"📍 Falling back to simple tenant: {tenant_env}")
        return tenant_env

if __name__ == "__main__":
    # 🚨 CRITICAL: Initialize tenant system before creating app
    current_tenant = ensure_tenant_database_isolation()

    app = create_app()
    
    # 🚀 DOCKER COMPATIBILITY: Set debug mode based on environment
    app.config['DEBUG'] = os.environ.get('DOCKER_MODE') != 'true'

    # Store current tenant in app config
    app.config['CURRENT_TENANT'] = current_tenant
    print(f"🏛️  App configured for tenant: {current_tenant}")
    
    # 🚀 PERFECTION: Initialize new unified tenant system
    from src.tenants import TenantMiddleware
    tenant_middleware = TenantMiddleware(app)
    print("🔧 ✅ New unified tenant system initialized")

    # 🚨 NGROK DETECTION REMOVED: Now handled dynamically in utils.py per-request
    # This prevents Flask app context errors and ensures fresh NGROK URL lookup each time

    # Get server configuration
    server_config = get_server_configuration()
    
    print("🚀 Starting StudentVC server...")
    print()
    print("🚨 NGROK URLS: Server URLs now retrieved dynamically from tenant database")
    print("💡 Set NGROK URLs via tenant config API and they will be used immediately")
    print()
    print("📱 MOBILE WALLET ACCESS:")
    print(f"   • Local network: https://{server_config['local_ip']}:{server_config['port']}")
    print(f"   • NGROK: Configure via Settings → Network → NGROK Domain")
    print()
    
    try:
        # 🚀 ENHANCED SOCKET.IO: Configure for Docker compatibility
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
        print(f"❌ Server startup error: {e}")
        if os.environ.get('DOCKER_MODE') == 'true':
            print("🐳 Docker troubleshooting:")
            print("   • Check if ports are properly exposed")
            print("   • Verify SSL certificate generation")
            print("   • Check Docker network configuration")
        else:
            print("💡 Try: pkill -f 'python.*main.py' to kill existing processes")
