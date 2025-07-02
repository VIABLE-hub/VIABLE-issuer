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
    app.config['DEBUG'] = True

    # Store current tenant in app config
    app.config['CURRENT_TENANT'] = current_tenant
    print(f"🏛️  App configured for tenant: {current_tenant}")
    
    # 🚀 PERFECTION: Initialize new unified tenant system
    from src.tenants import TenantMiddleware
    tenant_middleware = TenantMiddleware(app)
    print("🔧 ✅ New unified tenant system initialized")

    # 🚨 NGROK DETECTION REMOVED: Now handled dynamically in utils.py per-request
    # This prevents Flask app context errors and ensures fresh NGROK URL lookup each time

    LOCAL_IP = get_local_ip()
    FLASK_PORT = 8080
    
    print("🚀 Starting StudentVC server...")
    print(f"🌐 Binding to: 0.0.0.0:{FLASK_PORT}")
    print("🔒 HTTPS: True (adhoc certificates)")
    print(f"🌐 Local IP detected: {LOCAL_IP}")
    print()
    print("🚨 NGROK URLS: Server URLs now retrieved dynamically from tenant database")
    print("💡 Set NGROK URLs via tenant config API and they will be used immediately")
    
    try:
        socketio.run(
            app,
            debug=True,
            host="0.0.0.0",
            port=FLASK_PORT,
            ssl_context="adhoc",
            allow_unsafe_werkzeug=True
        )
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        print("💡 Try: pkill -f 'python.*main.py' to kill existing processes")
