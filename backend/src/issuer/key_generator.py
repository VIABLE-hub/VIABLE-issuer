from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import os
from flask import current_app as app
import logging
import base58
import base64
import importlib.util
import sys
from datetime import datetime

# Load BBS+ core module dynamically
try:
    spec = importlib.util.spec_from_file_location("bbs_core", os.path.join(os.path.dirname(__file__), "..", "..", "bbs_core.py"))
    bbs_core = importlib.util.module_from_spec(spec)
    sys.modules["bbs_core"] = bbs_core
    spec.loader.exec_module(bbs_core)
    BBS_CORE_AVAILABLE = True
    print("✅ BBS+ core loaded successfully")
except Exception as e:
    print(f"⚠️ BBS+ core not available: {e}")
    print("🔄 Using fallback key generation (non-BBS+ signatures)")
    BBS_CORE_AVAILABLE = False
    # Create a mock bbs_core for compatibility
    class MockBBSCore:
        def __init__(self):
            pass
    bbs_core = MockBBSCore()

logger = logging.getLogger(__name__)


def load_or_generate_bbs_keys():
    private_key_path = os.path.join(
        app.config['INSTANCE_FOLDER_PATH'], 'bbs_private.pem')
    public_key_path = os.path.join(
        app.config['INSTANCE_FOLDER_PATH'], 'bbs_public.pem')
    # Check if the private and public keys already exist
    if os.path.exists(private_key_path) and os.path.exists(public_key_path):
        return load_existing_bbs_keys()
    return generate_bbs_keys()


def generate_bbs_keys():
    """Generate BBS+ keys with cross-platform compatibility"""
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

    with open(os.path.join(app.config['INSTANCE_FOLDER_PATH'], 'bbs_private.pem'), "wb") as private_file:
        private_file.write(base64.b64encode(priv_key_bytes))

    with open(os.path.join(app.config['INSTANCE_FOLDER_PATH'], 'bbs_public.pem'), "wb") as public_file:
        public_file.write(base64.b64encode(dpub_key_bytes))

    return priv_key_bytes, dpub_key_bytes


def load_existing_bbs_keys():
    private_key_path = os.path.join(
        app.config['INSTANCE_FOLDER_PATH'], 'bbs_private.pem')
    public_key_path = os.path.join(
        app.config['INSTANCE_FOLDER_PATH'], 'bbs_public.pem')
    logger.debug("Keys exist. Loading keys...")
    # Load the existing private key
    with open(private_key_path, "rb") as private_file:
        private_key = base64.b64decode(private_file.read().decode('utf-8'))

    # Load the existing public key
    with open(public_key_path, "rb") as public_file:
        public_key = base64.b64decode(public_file.read().decode('utf-8'))

    return private_key, public_key


def load_or_generate_keys():
    private_key_path = os.path.join(
        app.config['INSTANCE_FOLDER_PATH'], 'private.pem')
    public_key_path = os.path.join(
        app.config['INSTANCE_FOLDER_PATH'], 'public.pem')
    # Check if the private and public keys already exist
    if os.path.exists(private_key_path) and os.path.exists(public_key_path):
        return load_existing_keys()
    return generate_keys()


def generate_keys():
    private_key_path = os.path.join(
        app.config['INSTANCE_FOLDER_PATH'], 'private.pem')
    public_key_path = os.path.join(
        app.config['INSTANCE_FOLDER_PATH'], 'public.pem')
    logger.debug("Keys do not exist. Generating keys...")
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

    logger.debug(f"Private key saved to {private_key_path}")

    # Get the public key from the private key
    public_key = private_key.public_key()

    # Serialize and save the public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(public_key_path, "wb") as public_file:
        public_file.write(public_pem)

    logger.debug(f"Public key saved to {public_key_path}")
    return private_key, public_pem.decode("utf-8")


def load_existing_keys():
    private_key_path = os.path.join(
        app.config['INSTANCE_FOLDER_PATH'], 'private.pem')
    public_key_path = os.path.join(
        app.config['INSTANCE_FOLDER_PATH'], 'public.pem')
    logger.debug("Keys exist. Loading keys...")
    # Load the existing private key
    with open(private_key_path, "rb") as private_file:
        private_key = serialization.load_pem_private_key(
            private_file.read(), password=None)

    # Load the existing public key
    with open(public_key_path, "rb") as public_file:
        public_key = public_file.read().decode("utf-8")

    return private_key, public_key


def generate_did(tenant_id='root'):
    """Generate a DID for the issuer"""
    if BBS_CORE_AVAILABLE:
        try:
            # Use BBS+ core for DID generation
            kp = bbs_core.GenerateKeyPair().generate_key_pair()
            
            # Use cross-platform compatible attribute names
            if hasattr(kp, 'dpub_key_bytes'):
                public_key_bytes = kp.dpub_key_bytes
            elif hasattr(kp, 'public_key'):
                public_key_bytes = kp.public_key
            else:
                # Try to find any attribute that might be the public key
                potential_attrs = [attr for attr in dir(kp) if 'pub' in attr.lower() and not attr.startswith('__')]
                if potential_attrs:
                    public_key_bytes = getattr(kp, potential_attrs[0])
                else:
                    raise AttributeError("Cannot determine BBS+ public key attribute")
                
            public_key_base64 = base64.b64encode(public_key_bytes).decode('utf-8')
            
            # Create did:key from public key
            did = f"did:key:{public_key_base64}"
            logger.info(f"✅ Generated BBS+ DID for tenant {tenant_id}: {did}")
            return did
        except Exception as e:
            logger.warning(f"⚠️ BBS+ DID generation failed: {e}, using fallback")
    
    # Fallback RSA key generation
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    public_key_base64 = base64.b64encode(public_key_bytes).decode('utf-8')
    did = f"did:key:rsa:{public_key_base64}"
    logger.info(f"✅ Generated RSA fallback DID for tenant {tenant_id}: {did}")
    return did


def generate_kid(tenant_id='root'):
    """Generate a key identifier (kid) for the issuer"""
    if BBS_CORE_AVAILABLE:
        try:
            # Use BBS+ core for kid generation
            kp = bbs_core.GenerateKeyPair().generate_key_pair()
            
            # Use cross-platform compatible attribute names
            if hasattr(kp, 'dpub_key_bytes'):
                public_key_bytes = kp.dpub_key_bytes
            elif hasattr(kp, 'public_key'):
                public_key_bytes = kp.public_key
            else:
                # Try to find any attribute that might be the public key
                potential_attrs = [attr for attr in dir(kp) if 'pub' in attr.lower() and not attr.startswith('__')]
                if potential_attrs:
                    public_key_bytes = getattr(kp, potential_attrs[0])
                else:
                    raise AttributeError("Cannot determine BBS+ public key attribute")
                
            kid = base64.b64encode(public_key_bytes).decode('utf-8')[:16]  # First 16 chars
            logger.info(f"✅ Generated BBS+ kid for tenant {tenant_id}: {kid}")
            return kid
        except Exception as e:
            logger.warning(f"⚠️ BBS+ kid generation failed: {e}, using fallback")
    
    # Fallback - generate random kid
    import secrets
    kid = secrets.token_urlsafe(16)
    logger.info(f"✅ Generated fallback kid for tenant {tenant_id}: {kid}")
    return kid
