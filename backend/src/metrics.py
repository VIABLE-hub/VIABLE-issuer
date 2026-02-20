"""Prometheus metrics for StudentVC - Student ID Card focused"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, REGISTRY
from flask import Blueprint, Response, request as flask_request, g
import time
import logging

logger = logging.getLogger("LOGGER")

# ============================================================================
# CREDENTIAL ISSUANCE METRICS
# ============================================================================
# System Status Metrics
studentvc_up = Gauge('studentvc_up', 'StudentVC Service Status')
studentvc_up.set(1)

# Application Uptime
app_start_time = time.time()
studentvc_uptime = Gauge('studentvc_uptime_seconds', 'Time since application process started')
studentvc_uptime.set_function(lambda: time.time() - app_start_time)

# Key Management Metrics (File-based)
signing_key_age_days = Gauge('studentvc_signing_key_age_days', 'Age of signing keys in days (Filesystem)', ['type'])

# Key Registry Metrics (Database-based)
key_registry_count = Gauge('studentvc_key_registry_count', 'Number of keys in registry', ['status', 'type'])
key_registry_expiring_soon = Gauge('studentvc_key_registry_expiring_soon', 'Active keys expiring within 30 days', ['type'])

did_web_status = Gauge('studentvc_did_web_status', 'Status of DID:Web configuration (1=Valid/Verified, 0=Invalid/Mismatch)')

# DID Information
did_info = Info('studentvc_issuer', 'StudentVC Issuer Configuration Information')

studentid_issued_total = Gauge(
    'studentvc_credentials_issued_total',
    'Total Student ID Cards issued'
)

# --- DID CHECK CACHING ---
_did_check_cache = {
    'last_check': 0,
    'status': 0
}

def check_did_configuration_cached():
    """
    Checks if the local DID configuration matches the remote did.json.
    Caches the result for 60 seconds to avoid network contention during scrapes.
    """
    now = time.time()
    if now - _did_check_cache['last_check'] < 60:
        return _did_check_cache['status']

    try:
        import requests
        from urllib.parse import urlparse
        from .issuer import issuer as issuer_module, key_generator
        from .utils import get_current_server_url

        # 1. Initialize Keys & Get Configured DID
        issuer_module.initialize_keys()
        config_did = getattr(issuer_module, 'issuer_did', None)
        
        if not config_did or not config_did.startswith("did:web:"):
             _did_check_cache['status'] = 0
             _did_check_cache['last_check'] = now
             return 0

        # 2. Determine Domain (Logic from issuer.py)
        domain = config_did[8:].replace("%3A", ":")

        # 3. Generate Local DID Doc
        # Note: We need to load keys fresh to compare with what's on disk
        # (in case keys were rotated but app not restarted, though initialize_keys handles some of that)
        bbs_private, bbs_public = key_generator.load_or_generate_bbs_keys()
        jwt_private, jwt_public = key_generator.load_or_generate_keys()
        local_did_doc = key_generator.generate_did_web_doc(domain, jwt_public, bbs_public)

        # 4. Fetch Remote DID Doc
        # Detect protocol (naive)
        protocol = "https"
        if "localhost" in domain or "127.0.0.1" in domain or "10.0.2.2" in domain or ":" in domain:
             protocol = "http" # Allow http for local dev / ports

        url = f"{protocol}://{domain}/.well-known/did.json"
        
        try:
            resp = requests.get(url, timeout=3, verify=False) # Short timeout
            if resp.status_code == 200:
                remote_did_doc = resp.json()
                # 5. Compare
                if remote_did_doc == local_did_doc:
                    _did_check_cache['status'] = 1
                else:
                    logger.warning(f"DID Mismatch for {domain}. Remote keys do not match local keys.")
                    _did_check_cache['status'] = 0
            else:
                logger.warning(f"DID Fetch Failed: {url} returned {resp.status_code}")
                _did_check_cache['status'] = 0
        except Exception as ex:
            logger.warning(f"DID Network Check Error: {ex}")
            _did_check_cache['status'] = 0

    except Exception as e:
        logger.error(f"DID Check Infrastructure Error: {e}")
        _did_check_cache['status'] = 0
    
    _did_check_cache['last_check'] = now
    return _did_check_cache['status']

studentid_issued_duration = Histogram(
    'studentvc_credential_issuance_duration_seconds',
    'Student ID Card issuance latency in seconds',
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# ============================================================================
# CREDENTIAL VERIFICATION METRICS
# ============================================================================
studentid_verified_success = Counter(
    'studentvc_credentials_verified_success_total',
    'Total successful Student ID Card verifications'
)

studentid_verified_failed = Counter(
    'studentvc_credentials_verified_failed_total',
    'Total failed Student ID Card verifications'
)

studentid_verification_duration = Histogram(
    'studentvc_credential_verification_duration_seconds',
    'Student ID Card verification latency in seconds',
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# ============================================================================
# CREDENTIAL STATE METRICS
# ============================================================================
studentid_valid_count = Gauge(
    'studentvc_valid_credentials_total',
    'Number of valid Student ID Cards'
)

studentid_revoked_total = Gauge(
    'studentvc_credentials_revoked_total',
    'Total Student ID Cards revoked'
)

# ============================================================================
# AUTHENTICATION METRICS
# ============================================================================
auth_attempts_total = Counter(
    'studentvc_auth_attempts_total',
    'Total authentication attempts',
    ['result']
)

# ============================================================================
# REQUEST TRACKING METRICS
# ============================================================================
request_duration = Histogram(
    'studentvc_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

request_count = Counter(
    'studentvc_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Create blueprint
metrics = Blueprint('metrics', __name__)

@metrics.route('/metrics')
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    
    # Check DID Status (Now uses robust, cached network check)
    try:
         # Uses the cached check we added at module level
         status = check_did_configuration_cached()
         did_web_status.set(status)
         
         # Also expose the DID string itself
         # Import the module to access the current value of the global variable
         from .issuer import issuer as issuer_module_instance
         # Initialize keys if needed (check_did_configuration_cached already does, but safe to do again)
         # issuer_module_instance.initialize_keys() 
         
         current_did = getattr(issuer_module_instance, 'issuer_did', 'unknown') or 'unknown'
         did_info.info({'did': current_did})
             
    except Exception as e:
         logger.error(f"Metrics DID Check Failed: {e}")
         did_web_status.set(0)

    # Check Key Ages
    try:
        from flask import current_app
        import os
        
        # Using current_app.instance_path is the most reliable way in Flask
        instance_path = current_app.instance_path
        
        # Check ECDSA Key Age
        ecdsa_path = os.path.join(instance_path, 'private.pem')
        if os.path.exists(ecdsa_path):
             # Calculate age in days
             age = (time.time() - os.path.getmtime(ecdsa_path)) / 86400
             signing_key_age_days.labels(type='ecdsa').set(age)
             
        # Check BBS+ Key Age
        bbs_path = os.path.join(instance_path, 'bbs_private.pem')
        if os.path.exists(bbs_path):
             age = (time.time() - os.path.getmtime(bbs_path)) / 86400
             signing_key_age_days.labels(type='bbs').set(age)
             
    except Exception as e:
        logger.warning(f"Error checking key ages: {e}")

    # Check Key Registry (Database) & File-Based Keys
    try:
        from .models import KeyRegistry
        from . import db
        from datetime import datetime, timedelta
        from sqlalchemy import inspect
        
        # 1. Reset counters to ensure valid metrics
        for ktype in ['bbs_issuer', 'jwt_signing', 'ecdsa']:
            for status in ['active', 'expired', 'revoked']:
                key_registry_count.labels(status=status, type=ktype).set(0)
            key_registry_expiring_soon.labels(type=ktype).set(0)

        # 2. Add File-Based Keys (since user confirmed keys are not in DB)
        if os.path.exists(ecdsa_path):
             key_registry_count.labels(status='active', type='ecdsa').set(1)
        
        if os.path.exists(bbs_path):
             key_registry_count.labels(status='active', type='bbs_issuer').set(1)

        # 3. Check Database (Optional, but safe if table exists)
        inspector = inspect(db.engine)
        if inspector.has_table("key_registry"):
            try:
                # Query aggregates
                results = db.session.query(
                    KeyRegistry.key_type, 
                    KeyRegistry.status, 
                    db.func.count(KeyRegistry.id)
                ).group_by(KeyRegistry.key_type, KeyRegistry.status).all()
                
                # If DB has keys, overwrite file-based counts (or sum them if needed)
                # But since user says keys are files, DB is likely empty.
                if results and len(results) > 0:
                    for key_type, status, count in results:
                        key_registry_count.labels(status=status, type=key_type).set(count)
                    
                # Expiring Soon
                threshold = datetime.utcnow() + timedelta(days=30)
                expiring_results = db.session.query(
                    KeyRegistry.key_type,
                    db.func.count(KeyRegistry.id)
                ).filter(
                    KeyRegistry.status == 'active',
                    KeyRegistry.expires_at <= threshold,
                    KeyRegistry.expires_at > datetime.utcnow()
                ).group_by(KeyRegistry.key_type).all()
                    
                for key_type, count in expiring_results:
                    key_registry_expiring_soon.labels(type=key_type).set(count)
            except Exception as e:
                logger.warning(f"Error executing KeyRegistry query: {e}")

    except Exception as e:
        logger.warning(f"Error in KeyRegistry block: {e}")

    # Check VC Counts from Database

    try:
        from .models import VC_validity, db
        from sqlalchemy import func
        
        # 1. Total Issued Credentials (All rows)
        issued_count = db.session.query(func.count(VC_validity.id)).scalar()
        studentid_issued_total.set(issued_count or 0)
        
        # 2. Valid Credentials
        valid_count = db.session.query(func.count(VC_validity.id)).filter(
            VC_validity.validity == True
        ).scalar()
        studentid_valid_count.set(valid_count or 0)
        
        # 3. Revoked Credentials
        revoked_count = db.session.query(func.count(VC_validity.id)).filter(
            VC_validity.validity == False
        ).scalar()
        studentid_revoked_total.set(revoked_count or 0)

    except Exception as e:
        logger.warning(f"Error querying VC metrics: {e}")
       
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

# Request tracking middleware
def init_request_metrics(app):
    """Initialize request metrics middleware"""
    
    @app.before_request
    def before_request():
        """Track request start time"""
        g.request_start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Track request metrics after response"""
        try:
            # Calculate request duration
            if hasattr(g, 'request_start_time'):
                duration = time.time() - g.request_start_time
                
                # Get endpoint and method
                endpoint = flask_request.endpoint or 'unknown'
                method = flask_request.method or 'unknown'
                status = response.status_code or 500
                
                # Record metrics
                request_count.labels(method=method, endpoint=endpoint, status=status).inc()
                request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        except Exception as e:
            logger.warning(f"Error recording request metrics: {e}")
        
        return response

def record_request(method, endpoint, status, duration):
    """Record a request in Prometheus metrics"""
    try:
        request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    except Exception as e:
        logger.warning(f"Error recording request metrics: {e}")

def record_student_id_issued(duration_seconds=0):
    """Record a Student ID Card issuance"""
    try:
        studentid_issued_total.inc()
        if duration_seconds > 0:
            studentid_issued_duration.observe(duration_seconds)
        logger.info("📊 Student ID Card issued - metric recorded")
    except Exception as e:
        logger.warning(f"Error recording Student ID Card issuance: {e}")

def record_student_id_verified(success=True, duration_seconds=0):
    """Record a Student ID Card verification"""
    try:
        if success:
            studentid_verified_success.inc()
            logger.info("📊 Student ID Card verified (success) - metric recorded")
        else:
            studentid_verified_failed.inc()
            logger.info("📊 Student ID Card verified (failed) - metric recorded")
        
        if duration_seconds > 0:
            studentid_verification_duration.observe(duration_seconds)
    except Exception as e:
        logger.warning(f"Error recording Student ID Card verification: {e}")

def record_student_id_revoked():
    """Record a Student ID Card revocation"""
    try:
        studentid_revoked_total.inc()
        logger.info("📊 Student ID Card revoked - metric recorded")
    except Exception as e:
        logger.warning(f"Error recording Student ID Card revocation: {e}")

def update_valid_credentials(count):
    """Update the gauge for valid Student ID Cards"""
    try:
        studentid_valid_count.set(count)
        logger.info(f"📊 Valid Student ID Cards: {count}")
    except Exception as e:
        logger.warning(f"Error updating valid credentials gauge: {e}")

def record_auth_attempt(success=True):
    """Record an authentication attempt"""
    try:
        result = "success" if success else "failed"
        auth_attempts_total.labels(result=result).inc()
        logger.info(f"📊 Auth attempt ({result}) - metric recorded")
    except Exception as e:
        logger.warning(f"Error recording auth attempt: {e}")

def update_total_credentials(count):
    """Update the gauge for total Student ID Cards"""
    try:
        studentid_issued_total.set(count)
        logger.info(f"📊 Total Student ID Cards: {count}")
    except Exception as e:
        logger.warning(f"Error updating total credentials gauge: {e}")

def update_revoked_credentials(count):
    """Update the gauge for revoked/invalid Student ID Cards"""
    try:
        studentid_revoked_total.set(count)
        logger.info(f"📊 Revoked/Invalid Student ID Cards: {count}")
    except Exception as e:
        logger.warning(f"Error updating revoked credentials gauge: {e}")
