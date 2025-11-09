"""
Tenant-Aware Key Generator for StudentVC
Generates unique keys for each tenant to ensure proper isolation
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import os
from flask import current_app as app
import logging
import base58
import base64
import importlib.util
from pathlib import Path
import sys
from datetime import datetime
from ..path_utils import get_backend_path

# Load BBS+ core module dynamically with fallback
try:
    spec = importlib.util.spec_from_file_location("bbs_core", os.path.join(os.path.dirname(__file__), "..", "..", "bbs_core.py"))
    bbs_core = importlib.util.module_from_spec(spec)
    sys.modules["bbs_core"] = bbs_core
    spec.loader.exec_module(bbs_core)
    BBS_CORE_AVAILABLE = True
    print("✅ BBS+ core loaded successfully in tenant_key_generator")
except Exception as e:
    print(f"⚠️ BBS+ core not available in tenant_key_generator: {e}")
    print("🔄 Using fallback key generation (non-BBS+ signatures)")
    BBS_CORE_AVAILABLE = False
    # Create a mock bbs_core for compatibility
    class MockBBSCore:
        def __init__(self):
            pass
    bbs_core = MockBBSCore()

logger = logging.getLogger(__name__)

def get_tenant_keys_path(tenant_id: str) -> Path:
    """Get the tenant-specific keys directory"""
    tenant_path = get_backend_path('src', 'tenants', 'instances', tenant_id, 'keys')
    # Ensure directory exists
    tenant_path.mkdir(parents=True, exist_ok=True)
    return tenant_path

def load_or_generate_tenant_bbs_keys(tenant_id: str):
    """Load or generate BBS+ keys for a specific tenant"""
    keys_path = get_tenant_keys_path(tenant_id)
    private_key_path = keys_path / 'bbs_private.pem'
    public_key_path = keys_path / 'bbs_public.pem'
    
    # Check if the private and public keys already exist
    if private_key_path.exists() and public_key_path.exists():
        return load_existing_tenant_bbs_keys(tenant_id)
    return generate_tenant_bbs_keys(tenant_id)

def generate_tenant_bbs_keys(tenant_id: str):
    """Generate new BBS+ keys for a specific tenant"""
    logger.info(f"🔑 Generating NEW BBS+ keys for tenant: {tenant_id}")
    
    keys_path = get_tenant_keys_path(tenant_id)
    private_key_path = keys_path / 'bbs_private.pem'
    public_key_path = keys_path / 'bbs_public.pem'
    
    key_pair = bbs_core.GenerateKeyPair().generate_key_pair()
    
    # Use cross-platform compatible attribute names (works on both Linux and macOS)
    # Try the Linux attribute names first (from our Docker test)
    if hasattr(key_pair, 'dpub_key_bytes'):
        dpub_key_bytes = key_pair.dpub_key_bytes
        priv_key_bytes = key_pair.priv_key_bytes
        logger.debug("🔑 Using Linux-compatible BBS+ attribute names (dpub_key_bytes, priv_key_bytes)")
    # Fallback to macOS attribute names
    elif hasattr(key_pair, 'public_key'):
        dpub_key_bytes = key_pair.public_key
        priv_key_bytes = key_pair.secret_key
        logger.debug("🔑 Using macOS-compatible BBS+ attribute names (public_key, secret_key)")
    else:
        # Try to find any attribute that might be the keys
        potential_pub_attrs = [attr for attr in dir(key_pair) if 'pub' in attr.lower() and not attr.startswith('__')]
        potential_priv_attrs = [attr for attr in dir(key_pair) if any(x in attr.lower() for x in ['priv', 'secret']) and not attr.startswith('__')]
        
        if potential_pub_attrs and potential_priv_attrs:
            dpub_key_bytes = getattr(key_pair, potential_pub_attrs[0])
            priv_key_bytes = getattr(key_pair, potential_priv_attrs[0])
            logger.warning(f"🔑 Using detected BBS+ attribute names: {potential_pub_attrs[0]}, {potential_priv_attrs[0]}")
        else:
            # Last resort: print all available attributes and raise an error
            all_attrs = [attr for attr in dir(key_pair) if not attr.startswith('__')]
            logger.error(f"🔑 Could not determine BBS+ key attributes. Available: {all_attrs}")
            raise AttributeError(f"Cannot determine BBS+ key attributes in {all_attrs}")
    
    with open(private_key_path, "wb") as private_file:
        private_file.write(base64.b64encode(priv_key_bytes))

    with open(public_key_path, "wb") as public_file:
        public_file.write(base64.b64encode(dpub_key_bytes))

    logger.info(f"🔑 BBS+ keys generated for tenant {tenant_id} at {keys_path}")
    return priv_key_bytes, dpub_key_bytes

def load_existing_tenant_bbs_keys(tenant_id: str):
    """Load existing BBS+ keys for a specific tenant"""
    logger.debug(f"🔑 Loading existing BBS+ keys for tenant: {tenant_id}")
    
    keys_path = get_tenant_keys_path(tenant_id)
    private_key_path = keys_path / 'bbs_private.pem'
    public_key_path = keys_path / 'bbs_public.pem'
    
    # Load the existing private key
    with open(private_key_path, "rb") as private_file:
        private_key = base64.b64decode(private_file.read().decode('utf-8'))

    # Load the existing public key
    with open(public_key_path, "rb") as public_file:
        public_key = base64.b64decode(public_file.read().decode('utf-8'))

    return private_key, public_key

def load_or_generate_tenant_jwt_keys(tenant_id: str):
    """Load or generate JWT signing keys for a specific tenant"""
    keys_path = get_tenant_keys_path(tenant_id)
    private_key_path = keys_path / 'private.pem'
    public_key_path = keys_path / 'public.pem'
    
    # Check if the private and public keys already exist
    if private_key_path.exists() and public_key_path.exists():
        return load_existing_tenant_jwt_keys(tenant_id)
    return generate_tenant_jwt_keys(tenant_id)

def generate_tenant_jwt_keys(tenant_id: str):
    """Generate new JWT signing keys for a specific tenant"""
    logger.info(f"🔑 Generating NEW JWT keys for tenant: {tenant_id}")
    
    keys_path = get_tenant_keys_path(tenant_id)
    private_key_path = keys_path / 'private.pem'
    public_key_path = keys_path / 'public.pem'
    
    # Generate a new EC private key
    private_key = ec.generate_private_key(ec.SECP256R1())

    # Serialize and save the private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(private_key_path, "wb") as private_file:
        private_file.write(private_pem)

    logger.debug(f"🔑 Private key saved to {private_key_path}")

    # Get the public key from the private key
    public_key = private_key.public_key()

    # Serialize and save the public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(public_key_path, "wb") as public_file:
        public_file.write(public_pem)

    logger.debug(f"🔑 Public key saved to {public_key_path}")
    logger.info(f"🔑 JWT keys generated for tenant {tenant_id} at {keys_path}")
    
    return private_key, public_pem.decode("utf-8")

def load_existing_tenant_jwt_keys(tenant_id: str):
    """Load existing JWT signing keys for a specific tenant"""
    logger.debug(f"🔑 Loading existing JWT keys for tenant: {tenant_id}")
    
    keys_path = get_tenant_keys_path(tenant_id)
    private_key_path = keys_path / 'private.pem'
    public_key_path = keys_path / 'public.pem'
    
    # Load the existing private key
    with open(private_key_path, "rb") as private_file:
        private_key = serialization.load_pem_private_key(
            private_file.read(), password=None)

    # Load the existing public key
    with open(public_key_path, "rb") as public_file:
        public_key = public_file.read().decode("utf-8")

    return private_key, public_key

def generate_tenant_did(tenant_id: str, public_key_pem: str):
    """Generate a DID for a specific tenant's public key"""
    public_key_pem = public_key_pem.encode("utf-8")
    logger.info(f"🔑 Generating DID for tenant {tenant_id} from public key")
    
    # Decode the PEM-encoded public key to extract the raw key material
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend

    # Load the public key from PEM
    public_key = serialization.load_pem_public_key(
        public_key_pem, backend=default_backend())

    # Get the raw public key bytes (in uncompressed form)
    raw_key_material = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    # Prepend the multicodec prefix for P-256 keys (0x1200)
    multicodec_prefix = b'\x12\x00'
    multicodec_key = multicodec_prefix + raw_key_material

    # Encode the multicodec key in base58
    encoded_key = base58.b58encode(multicodec_key)

    # Construct the DID key
    did = f'did:key:z{encoded_key.decode()}'
    logger.info(f"🔑 Generated DID for tenant {tenant_id}: {did}")
    return did

def generate_tenant_kid(tenant_id: str, did: str):
    """Generate a Key ID for a specific tenant's DID"""
    # Append a fragment identifier to the DID
    kid = f"{did}#key-1"
    logger.debug(f"🔑 Generated KID for tenant {tenant_id}: {kid}")
    return kid

# Compatibility functions that route to tenant-aware versions
def get_current_tenant_keys():
    """Get keys for the current tenant"""
    try:
        from ..tenants import get_current_tenant as get_current_tenant_id
        current_tenant = get_current_tenant_id()
        
        # Load both BBS+ and JWT keys for current tenant
        bbs_private, bbs_public = load_or_generate_tenant_bbs_keys(current_tenant)
        jwt_private, jwt_public = load_or_generate_tenant_jwt_keys(current_tenant)
        
        # Generate DID for current tenant
        tenant_did = generate_tenant_did(current_tenant, jwt_public)
        tenant_kid = generate_tenant_kid(current_tenant, tenant_did)
        
        logger.info(f"🔑 Loaded keys for tenant {current_tenant}, DID: {tenant_did}")
        
        return {
            'tenant_id': current_tenant,
            'bbs_private': bbs_private,
            'bbs_public': bbs_public,
            'jwt_private': jwt_private,
            'jwt_public': jwt_public,
            'did': tenant_did,
            'kid': tenant_kid
        }
    except Exception as e:
        logger.error(f"🔑 Error loading tenant keys: {e}")
        # Fallback to root tenant
        return get_tenant_keys('root')

def get_tenant_keys(tenant_id: str):
    """Get keys for a specific tenant"""
    bbs_private, bbs_public = load_or_generate_tenant_bbs_keys(tenant_id)
    jwt_private, jwt_public = load_or_generate_tenant_jwt_keys(tenant_id)
    
    tenant_did = generate_tenant_did(tenant_id, jwt_public)
    tenant_kid = generate_tenant_kid(tenant_id, tenant_did)
    
    return {
        'tenant_id': tenant_id,
        'bbs_private': bbs_private,
        'bbs_public': bbs_public,
        'jwt_private': jwt_private,
        'jwt_public': jwt_public,
        'did': tenant_did,
        'kid': tenant_kid
    } 