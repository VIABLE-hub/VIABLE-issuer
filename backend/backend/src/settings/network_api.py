"""
Modernized Network Settings API
Uses the new unified tenant system for perfect isolation
"""

from flask import Blueprint, jsonify, request
import logging

from ..tenants import (
    get_current_tenant as get_current_tenant_id, 
    get_tenant_config, 
    update_tenant_network_config,
    get_tenant_urls,
    clear_tenant_config_cache
)

logger = logging.getLogger(__name__)

network_api = Blueprint('network_api', __name__)

@network_api.route('/api/network', methods=['GET'])
def get_network_settings():
    """
    🚀 PERFECTION: Get network settings using new unified tenant system
    """
    try:
        # Get current tenant and complete configuration
        tenant_id = get_current_tenant_id()
        tenant_config = get_tenant_config(tenant_id)
        tenant_urls = get_tenant_urls(tenant_id)
        
        logger.info(f"🔧 ✅ Network API GET - tenant: {tenant_id}")
        
        # Extract network settings
        network_settings = tenant_config.get('network_settings', {})
        
        return jsonify({
            'status': 'success',
            'tenant_id': tenant_id,
            'tenant_name': tenant_config.get('display_name'),
            'tenant_color': tenant_config.get('primary_color'),
            'network_settings': network_settings,
            'computed_urls': {
                'server_url': tenant_config.get('server_url'),
                'ngrok_url': tenant_config.get('ngrok_url'),
                'issuer_url': tenant_urls.get('issuer_url'),
                'verifier_url': tenant_urls.get('verifier_url'),
                'vcstatus_url': tenant_urls.get('vcstatus_url'),
                'well_known_issuer': tenant_urls.get('well_known_issuer'),
                'well_known_config': tenant_urls.get('well_known_config')
            },
            'network_info': {
                'use_ngrok': network_settings.get('use_ngrok', False),
                'connection_mode': network_settings.get('connection_mode', 'local'),
                'use_https': network_settings.get('use_https', True)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Network API GET error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@network_api.route('/api/network', methods=['POST'])
def update_network_settings():
    """
    🚀 PERFECTION: Update network settings using new unified tenant system
    """
    try:
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        tenant_id = get_current_tenant_id()
        logger.info(f"🔧 ✅ Network API POST - tenant: {tenant_id}, data: {data}")
        
        # Validate ngrok URL if provided
        if data.get('use_ngrok') and data.get('ngrok_url'):
            ngrok_url = data['ngrok_url'].strip()
            if not ngrok_url.startswith(('http://', 'https://')):
                data['ngrok_url'] = f"https://{ngrok_url}"
        
        # Update network configuration using new system
        success = update_tenant_network_config(data, tenant_id)
        
        if success:
            # Get updated configuration
            updated_config = get_tenant_config(tenant_id)
            updated_urls = get_tenant_urls(tenant_id)
            
            return jsonify({
                'status': 'success',
                'message': 'Network settings updated successfully',
                'tenant_id': tenant_id,
                'updated_config': {
                    'network_settings': updated_config.get('network_settings', {}),
                    'server_url': updated_config.get('server_url'),
                    'urls': updated_urls
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update network settings'
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Network API POST error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@network_api.route('/api/network/test', methods=['POST'])
def test_network_connection():
    """
    🚀 PERFECTION: Test network connection for current tenant
    Tests actual health check endpoints for issuer and verifier
    """
    try:
        tenant_id = get_current_tenant_id()
        tenant_config = get_tenant_config(tenant_id)
        
        logger.info(f"🔧 ✅ Network test - tenant: {tenant_id}")
        
        # Get the base server URL
        server_url = tenant_config.get('server_url', 'http://localhost:8080')
        
        # Test the current tenant's health endpoints
        import requests
        import time
        import urllib3
        
        # Disable SSL warnings for local testing
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        test_results = {}
        
        # Test issuer health endpoint
        try:
            issuer_health_url = f"{server_url}/issuer/healthcheck"
            logger.info(f"Testing issuer health: {issuer_health_url}")
            
            start_time = time.time()
            response = requests.get(issuer_health_url, timeout=10, verify=False)
            latency = (time.time() - start_time) * 1000
            
            test_results['issuer'] = {
                'status': 'success' if response.status_code == 200 else 'error',
                'latency_ms': round(latency, 2),
                'url_tested': issuer_health_url,
                'status_code': response.status_code
            }
            
            if response.status_code != 200:
                test_results['issuer']['error'] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            test_results['issuer'] = {
                'status': 'error',
                'error': 'Connection timeout',
                'url_tested': f"{server_url}/issuer/healthcheck"
            }
        except requests.exceptions.ConnectionError as e:
            test_results['issuer'] = {
                'status': 'error',
                'error': f'Connection failed: {str(e)[:100]}',
                'url_tested': f"{server_url}/issuer/healthcheck"
            }
        except Exception as e:
            test_results['issuer'] = {
                'status': 'error',
                'error': str(e),
                'url_tested': f"{server_url}/issuer/healthcheck"
            }
        
        # Test verifier health endpoint
        try:
            verifier_health_url = f"{server_url}/verifier/healthcheck"
            logger.info(f"Testing verifier health: {verifier_health_url}")
            
            start_time = time.time()
            response = requests.get(verifier_health_url, timeout=10, verify=False)
            latency = (time.time() - start_time) * 1000
            
            test_results['verifier'] = {
                'status': 'success' if response.status_code == 200 else 'error',
                'latency_ms': round(latency, 2),
                'url_tested': verifier_health_url,
                'status_code': response.status_code
            }
            
            if response.status_code != 200:
                test_results['verifier']['error'] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            test_results['verifier'] = {
                'status': 'error',
                'error': 'Connection timeout',
                'url_tested': f"{server_url}/verifier/healthcheck"
            }
        except requests.exceptions.ConnectionError as e:
            test_results['verifier'] = {
                'status': 'error',
                'error': f'Connection failed: {str(e)[:100]}',
                'url_tested': f"{server_url}/verifier/healthcheck"
            }
        except Exception as e:
            test_results['verifier'] = {
                'status': 'error',
                'error': str(e),
                'url_tested': f"{server_url}/verifier/healthcheck"
            }
        
        # Calculate overall status
        successful_tests = sum(1 for result in test_results.values() if result.get('status') == 'success')
        total_tests = len(test_results)
        
        overall_status = 'healthy' if successful_tests == total_tests else ('partial' if successful_tests > 0 else 'unhealthy')
        
        logger.info(f"🔧 ✅ Network test results: {successful_tests}/{total_tests} passed")
        
        return jsonify({
            'status': 'success',
            'tenant_id': tenant_id,
            'server_url': server_url,
            'test_results': test_results,
            'overall_status': overall_status,
            'tests_passed': successful_tests,
            'tests_total': total_tests
        })
        
    except Exception as e:
        logger.error(f"❌ Network test error: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@network_api.route('/api/network/cache/clear', methods=['POST'])
def clear_network_cache():
    """
    🚀 PERFECTION: Clear network configuration cache for current tenant
    """
    try:
        tenant_id = get_current_tenant_id()
        clear_tenant_config_cache()
        
        logger.info(f"🔧 ✅ Cache cleared for tenant: {tenant_id}")
        
        return jsonify({
            'status': 'success',
            'message': f'Configuration cache cleared for tenant {tenant_id}'
        })
        
    except Exception as e:
        logger.error(f"❌ Cache clear error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def register_network_api(app):
    """Register the modernized network API"""
    app.register_blueprint(network_api)
    logger.info("🔧 ✅ Modernized Network API registered") 