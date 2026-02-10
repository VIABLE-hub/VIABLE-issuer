"""Prometheus metrics for StudentVC - Student ID Card focused"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
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

did_web_status = Gauge('studentvc_did_web_status', 'Status of DID:Web configuration (1=Valid, 0=Invalid)')

studentid_issued_total = Counter(
    'studentvc_credentials_issued_total',
    'Total Student ID Cards issued'
)

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

studentid_revoked_total = Counter(
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
    
    # Check DID Status
    try:
        from .issuer.issuer import initialize_keys, issuer_did
        initialize_keys()
        if issuer_did:
            did_web_status.set(1)
        else:
            did_web_status.set(0)
    except Exception as e:
        logger.error(f"Metrics Check Failed: {e}")
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
        # Check Key Registry (Database)
        try:
            from .models import KeyRegistry
            from . import db
            from datetime import datetime, timedelta
            
            # Reset counters
            # Note: In a real prod env, we might want to be more careful about resetting 
            # if we have high cardinality, but for keys (low cardinality), this is fine.
            
            # 1. Status Counts
            # We explicitly set 0 for known states to ensure they exist in Prometheus
            for ktype in ['bbs_issuer', 'jwt_signing']:
                for status in ['active', 'expired', 'revoked']:
                    key_registry_count.labels(status=status, type=ktype).set(0)
            
            # Query aggregates
            results = db.session.query(
                KeyRegistry.key_type, 
                KeyRegistry.status, 
                db.func.count(KeyRegistry.id)
            ).group_by(KeyRegistry.key_type, KeyRegistry.status).all()
            
            for key_type, status, count in results:
                key_registry_count.labels(status=status, type=key_type).set(count)
                
            # 2. Expiring Soon (Active keys only)
            threshold = datetime.utcnow() + timedelta(days=30)
            expiring_results = db.session.query(
                KeyRegistry.key_type,
                db.func.count(KeyRegistry.id)
            ).filter(
                KeyRegistry.status == 'active',
                KeyRegistry.expires_at <= threshold,
                KeyRegistry.expires_at > datetime.utcnow() # Not already expired
            ).group_by(KeyRegistry.key_type).all()
            
            # Reset expiring metrics
            for ktype in ['bbs_issuer', 'jwt_signing']:
                key_registry_expiring_soon.labels(type=ktype).set(0)
                
            for key_type, count in expiring_results:
                key_registry_expiring_soon.labels(type=key_type).set(count)
                
        except Exception as e:
            # Table might not exist yet if migration hasn't run
            logger.warning(f"Error querying KeyRegistry metrics: {e}")
             
        if os.path.exists(bbs_path):
             age = (time.time() - os.path.getmtime(bbs_path)) / 86400
             signing_key_age_days.labels(type='bbs').set(age)
             
    except Exception as e:
        logger.warning(f"Error checking key ages: {e}")
        
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
