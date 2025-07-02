from flask import Flask, redirect, url_for, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_migrate import Migrate
import logging
import random
import os
from flask_socketio import SocketIO
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="urllib3")

# Create and configure the logger
log_file_path = os.path.join("..", "instance", "service.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Set up the root logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler(),  # Optional: To also log to the console
    ],
)

logger = logging.getLogger("LOGGER")

# Log something in the main app
logger.info("Logger initialized!")

# Create the db
db = SQLAlchemy()
migrate = Migrate()
DB_NAME = "database.db"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}"

# Create socketio
socketio = SocketIO()

# random cookie key
SECRET_KEY = ''.join(random.choice(
    'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))

INSTANCE_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance')


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = SECRET_KEY
    
    # 🚨 CRITICAL: Configure tenant-specific database BEFORE setting default URI
    try:
        from .tenants.database import configure_tenant_database, get_current_tenant_from_environment
        current_tenant = get_current_tenant_from_environment()
        if current_tenant:
            tenant_db_uri = configure_tenant_database(app, current_tenant)
            logger.info(f"✅ Tenant database configured: {tenant_db_uri}")
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
            logger.info(f"⚠️  Using default database URI: {SQLALCHEMY_DATABASE_URI}")
    except Exception as e:
        logger.error(f"❌ Failed to configure tenant database: {e}")
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        logger.info(f"⚠️  Falling back to default database URI: {SQLALCHEMY_DATABASE_URI}")
    
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['INSTANCE_FOLDER_PATH'] = INSTANCE_PATH
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize CORS for iOS compatibility
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Ensure CSRF token is available for all requests
    @app.before_request
    def ensure_csrf_token():
        import secrets
        from flask import session
        
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)
    
    # Make csrf_token and tenant info accessible in templates
    @app.context_processor
    def inject_csrf_token():
        from flask import session
        
        context = {
            'csrf_token': session.get('csrf_token', ''),
        }
        
        # Add tenant/university information using new tenant system with fallback
        try:
            # Try new tenant system first
            from .tenants.registry import get_current_tenant_logos
            tenant_logos = get_current_tenant_logos()
            context.update(tenant_logos)
        except Exception as e:
            # Fallback to legacy tenant_utils.py for compatibility
            try:
                from .tenant_utils import get_tenant_logos
                tenant_logos = get_tenant_logos()
                context.update(tenant_logos)
            except Exception as fallback_error:
                # Ultimate fallback if both systems fail
                context.update({
                    'main_logo': 'studentVC-logo-sora-cropped.png',
                    'university_logo': None,
                    'university_name': None,
                    'tenant_color': '#003f7f'
                })
                logger.warning(f"Tenant detection failed - using default: {e}, fallback: {fallback_error}")
        
        return context
    
    # Explizite Route für favicon.ico, um 405-Fehler zu vermeiden
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('studentVC-logo-sora-cropped.png')
    
    # Route for tenant-specific static files
    @app.route('/tenant-static/<path:filename>')
    def tenant_static(filename):
        """Serve tenant-specific static files"""
        try:
            from .tenants.registry import get_current_tenant_config
            tenant_config = get_current_tenant_config()
            
            if tenant_config:
                # Check if file exists in tenant static directory
                tenant_file_path = os.path.join(tenant_config.static_path, filename)
                if os.path.exists(tenant_file_path):
                    return send_from_directory(tenant_config.static_path, filename)
            
            # Fallback to default static directory
            return app.send_static_file(filename)
            
        except Exception as e:
            logger.error(f"Error serving tenant static file {filename}: {e}")
            # Fallback to default static directory
            return app.send_static_file(filename)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize multi-tenant system (database already configured above)
    try:
        from .tenants.setup import initialize_tenant_system
        
        # Initialize tenant system (registry, config loading)
        initialize_tenant_system()
        logger.info("✅ Multi-tenant system registry initialized successfully")
        
    except Exception as e:
        logger.warning(f"⚠️  Multi-tenant system initialization failed: {e}")
        logger.info("🔄 Falling back to legacy tenant system")

    from .home import home
    from .auth import auth
    from .issuer.issuer import issuer
    from .verifier.main_routes import verifier_bp as verifier  # 🔧 MODULAR: Using split verifier architecture
    from .validate.vcstatus import vcstatus  # Aktualisiert: Verwendet jetzt die vcstatus.py Datei
    from .validate.validate import validate_legacy  # 🩺 CHIRURGISCHE REPARATUR: Import legacy blueprint
    from .settings import settings, api_settings  # Import settings from the package instead of directly from settings.py
    from .api_integration import api_integration  # Import the API integration blueprint

    from .issuer.debug import debug as debug_bp  # Import the debug blueprint
    from .usecases.usecases import usecases  # Import the usecases blueprint
    from .monitoring import monitoring  # Import the monitoring blueprint
    # Note: tenant_test module removed - tenant config endpoints moved to settings

    app.register_blueprint(home, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(issuer, url_prefix='/')
    app.register_blueprint(verifier, url_prefix='/verifier')
    app.register_blueprint(vcstatus, url_prefix='/vcstatus')
    app.register_blueprint(validate_legacy, url_prefix='/validate')  # 🩺 CHIRURGISCHE REPARATUR: Legacy route
    app.register_blueprint(settings, url_prefix='/')
    app.register_blueprint(api_settings, url_prefix='/')
    app.register_blueprint(api_integration, url_prefix='/')  # Register API integration blueprint
    app.register_blueprint(debug_bp, url_prefix='/debug')  # Register debug blueprint at root level
    app.register_blueprint(usecases, url_prefix='/usecases')  # Register usecases blueprint
    app.register_blueprint(monitoring)  # Register monitoring blueprint
    # Note: tenant config endpoints now handled by settings module
    
    # 🚀 PERFECTION: Register new modernized network API
    from .settings.network_api import register_network_api
    register_network_api(app)
    
    from .models import User

    with app.app_context():
        db.create_all()
        # addAllTrackableItems()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # CRITICAL FIX: Enhanced Socket.IO configuration for ngrok compatibility
    socketio.init_app(app, 
                     cors_allowed_origins="*", 
                     async_mode='threading',
                     ping_timeout=30,           # Increased for ngrok
                     ping_interval=25,
                     allow_upgrades=True,       # Allow transport upgrades
                     transports=['polling', 'websocket'],  # Enable both transports
                     engineio_logger=False,     # Disable for production
                     logger=False)              # Disable for production

    # Create alias for /api/credentials endpoint to ensure backward compatibility
    @app.route('/api/credentials', methods=['GET'])
    def api_credentials_alias():
        from .validate.vcstatus import api_get_credentials
        return api_get_credentials()
    
    # Create alias for /api/credential/<identifier> endpoint for management operations
    @app.route('/api/credential/<string:identifier>', methods=['GET', 'PUT', 'DELETE'])
    def api_credential_manage_alias(identifier):
        from .validate.vcstatus import api_manage_credential
        return api_manage_credential(identifier)
    
    # Create alias for /api/bulk endpoint for bulk operations
    @app.route('/api/bulk', methods=['POST'])
    def api_bulk_operations_alias():
        from .validate.vcstatus import api_bulk_operations
        return api_bulk_operations()
    
    # Add specific endpoint for revoking a credential by ID
    @app.route('/api/credential/<string:identifier>/revoke', methods=['POST'])
    def api_revoke_credential(identifier):
        from .models import VC_validity, db
        
        try:
            credential = VC_validity.query.filter_by(identifier=identifier).first()
            if not credential:
                return jsonify({'error': 'Credential not found'}), 404
                
            data = request.get_json() or {}
            reason = data.get('reason', 'Revoked via API')
            revoked_by = data.get('revoked_by', 'api')
            
            credential.revoke(reason=reason, revoked_by=revoked_by)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Credential revoked successfully',
                'identifier': identifier,
                'status': 'revoked',
                'revoked_at': credential.revoked_at.isoformat() if credential.revoked_at else None
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Add specific endpoint for restoring (unrevoking) a credential by ID
    @app.route('/api/credential/<string:identifier>/restore', methods=['POST'])
    def api_restore_credential(identifier):
        from .models import VC_validity, db
        
        try:
            credential = VC_validity.query.filter_by(identifier=identifier).first()
            if not credential:
                return jsonify({'error': 'Credential not found'}), 404
                
            credential.restore()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Credential restored successfully',
                'identifier': identifier,
                'status': 'valid'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Add specific endpoint for deleting a credential by ID
    @app.route('/api/credential/<string:identifier>/delete', methods=['POST'])
    def api_delete_credential(identifier):
        from .models import VC_validity, db
        
        try:
            credential = VC_validity.query.filter_by(identifier=identifier).first()
            if not credential:
                return jsonify({'error': 'Credential not found'}), 404
                
            db.session.delete(credential)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Credential deleted successfully',
                'identifier': identifier
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Main route
    @app.route('/')
    def index():
        return redirect(url_for('issuer.index'))

    return app
