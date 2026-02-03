"""Test helper to generate sample metrics for demonstration"""

def generate_sample_metrics():
    """Generate sample metrics data for testing and demonstration"""
    from .metrics import (
        record_credential_issued,
        record_credential_revoked,
        record_credential_verified,
        record_auth_attempt,
        update_active_credentials,
        update_revoked_credentials,
        record_error
    )
    
    # Generate sample credential issuances
    for i in range(15):
        record_credential_issued('StudentIDCard')
    
    for i in range(8):
        record_credential_issued('UniversityDegree')
    
    for i in range(5):
        record_credential_issued('CourseCredential')
    
    # Generate sample revocations
    for i in range(3):
        record_credential_revoked()
    
    # Generate sample verifications
    for i in range(45):
        record_credential_verified('success')
    
    for i in range(5):
        record_credential_verified('failed')
    
    # Generate sample auth attempts
    for i in range(30):
        record_auth_attempt('success')
    
    for i in range(2):
        record_auth_attempt('failed')
    
    # Generate some errors
    for i in range(1):
        record_error('400')
    
    for i in range(2):
        record_error('401')
    
    # Update credential counts
    update_active_credentials(28)  # 15+8+5 = 28 active
    update_revoked_credentials(3)


def init_metrics_demo(app):
    """Initialize demo metrics on app startup"""
    with app.app_context():
        generate_sample_metrics()
        import logging
        logger = logging.getLogger("LOGGER")
        logger.info("✅ Sample metrics generated for demonstration")
