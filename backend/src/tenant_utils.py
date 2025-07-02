import os
from flask import request

def detect_current_tenant():
    """
    Detect the current tenant/university based on environment variable or domain
    Returns: dict with tenant info or None if no specific tenant
    """
    
    # Check environment variable first
    tenant_env = os.environ.get('TENANT_ID', '').lower()
    
    # Define tenant configurations
    tenants = {
        'tub': {
            'id': 'tub',
            'name': 'Technische Universität Berlin',
            'short_name': 'TU Berlin',
            'logo': 'tub_logo.png',
            'color': '#c50e1f',  # TU Red
            'domain_patterns': ['tu-berlin', 'tub']
        },
        'fub': {
            'id': 'fub', 
            'name': 'Freie Universität Berlin',
            'short_name': 'FU Berlin',
            'logo': 'fub-logo.png',
            'color': '#007a3e',  # FU Green
            'domain_patterns': ['fu-berlin', 'fub']
        }
    }
    
    # If environment variable is set, use it
    if tenant_env in tenants:
        return tenants[tenant_env]
    
    # Try to detect from request domain/host
    try:
        if request:
            host = request.host.lower()
            for tenant_id, tenant_info in tenants.items():
                for pattern in tenant_info['domain_patterns']:
                    if pattern in host:
                        return tenant_info
    except:
        pass  # Ignore if no request context
    
    # No specific tenant detected
    return None

def get_tenant_logos():
    """
    Get the appropriate logos to display
    Returns: dict with logo information
    """
    tenant = detect_current_tenant()
    
    logos = {
        'main_logo': 'studentVC-logo-sora-cropped.png',
        'university_logo': None,
        'university_name': None,
        'tenant_color': '#003f7f'  # Default Berlin Blue
    }
    
    if tenant:
        logos.update({
            'university_logo': tenant['logo'],
            'university_name': tenant['short_name'],
            'tenant_color': tenant['color']
        })
    
    return logos 