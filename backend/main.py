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
    import logging
    logger = logging.getLogger(__name__)

    # Docker mode: use Docker-specific SSL certificates
    if os.environ.get('DOCKER_MODE') == 'true':
        ssl_cert_path = os.environ.get('SSL_CERT_PATH', '/app/docker-cert.pem')
        ssl_key_path = os.environ.get('SSL_KEY_PATH', '/app/docker-key.pem')
        if os.path.exists(ssl_cert_path) and os.path.exists(ssl_key_path):
            logger.info(f"Using Docker SSL certificates: {ssl_cert_path}")
            return (ssl_cert_path, ssl_key_path)
        else:
            logger.warning("Docker SSL certificates not found, falling back to adhoc")
            return "adhoc"

    # Development mode: prefer a persistent self-signed certificate so the
    # browser only needs to trust it once (adhoc regenerates on every restart,
    # which breaks fetch() calls after a server restart).
    instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
    dev_cert = os.path.join(instance_dir, 'ssl_cert.pem')
    dev_key  = os.path.join(instance_dir, 'ssl_key.pem')

    if os.path.exists(dev_cert) and os.path.exists(dev_key):
        logger.info(f"Using persistent dev SSL certificate: {dev_cert}")
        return (dev_cert, dev_key)

    # Generate a persistent cert if none exists yet
    try:
        import subprocess
        os.makedirs(instance_dir, exist_ok=True)
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-keyout', dev_key, '-out', dev_cert,
            '-days', '3650', '-nodes',
            '-subj', '/CN=localhost/O=VERITAS Dev',
            '-addext', 'subjectAltName=DNS:localhost,IP:127.0.0.1',
        ], check=True, capture_output=True)
        logger.info(f"Generated persistent dev SSL certificate: {dev_cert}")
        return (dev_cert, dev_key)
    except Exception as e:
        logger.warning(f"Could not generate persistent SSL cert ({e}), falling back to adhoc")
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
        ssl_context = get_ssl_context()
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
    
def main():
    app = create_app()

    # DOCKER COMPATIBILITY: Set debug mode based on environment
    app.config['DEBUG'] = os.environ.get('DOCKER_MODE') != 'true'

    import logging
    logger = logging.getLogger(__name__)
    
    # Get server configuration
    server_config = get_server_configuration()

    logger.info("Starting StudentVC server...")
    logger.info("")
    logger.info("MOBILE WALLET ACCESS:")
    logger.info(f"   - Local network: https://{server_config['local_ip']}:{server_config['port']}")
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
if __name__ == "__main__":
    main()
