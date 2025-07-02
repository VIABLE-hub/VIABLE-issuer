"""
Modul zur Validierung und Konversion von kryptografischen Schlüsseln für die Issuer Anwendung.
Stellt Hilfsfunktionen für die Überprüfung und Umwandlung von Schlüsseln in verschiedene Formate bereit.
"""

import logging
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
import os
import base64

logger = logging.getLogger(__name__)

def load_private_key(filepath_or_env_var):
    """
    Lädt einen privaten Schlüssel aus einer Datei oder einer Umgebungsvariable.
    
    Args:
        filepath_or_env_var: Entweder ein Dateipfad zu einer PEM-Datei oder der Name einer Umgebungsvariable
                          die den PEM-String enthält
                          
    Returns:
        Der private Schlüssel als PEM-String, oder None wenn der Schlüssel nicht geladen werden konnte
        
    Raises:
        ValueError: Wenn der private Schlüssel nicht im PEM-Format ist oder nicht geladen werden kann
    """
    pem_content = None
    
    # Versuche zuerst, es als Umgebungsvariable zu interpretieren
    if filepath_or_env_var in os.environ:
        logger.info(f"Lade privaten Schlüssel aus Umgebungsvariable {filepath_or_env_var}")
        pem_content = os.environ.get(filepath_or_env_var)
    # Dann als Dateipfad
    elif os.path.exists(filepath_or_env_var):
        logger.info(f"Lade privaten Schlüssel aus Datei {filepath_or_env_var}")
        with open(filepath_or_env_var, 'rb') as key_file:
            pem_content = key_file.read().decode('utf-8')
    else:
        raise ValueError(f"Konnte privaten Schlüssel nicht laden: {filepath_or_env_var} ist weder eine existierende Datei noch eine Umgebungsvariable")
    
    # Validiere, dass der geladene Inhalt ein PEM-String ist
    validate_pem_key(pem_content)
    
    return pem_content

def validate_pem_key(key):
    """
    Überprüft, ob ein Schlüssel im PEM-Format vorliegt.
    
    Args:
        key: Der zu überprüfende Schlüssel
        
    Raises:
        ValueError: Wenn der Schlüssel nicht im PEM-Format ist
    """
    if not isinstance(key, str):
        raise ValueError(f"Erwarte einen PEM-formatierten Schlüssel als String, erhalten: {type(key)}")
    
    if not key.startswith('-----BEGIN'):
        raise ValueError("Schlüssel beginnt nicht mit einem PEM-Header")
    
    if not key.strip().endswith('-----'):
        raise ValueError("Schlüssel endet nicht mit einem PEM-Footer")
    
    if '-----END' not in key:
        raise ValueError("Schlüssel enthält keinen PEM-Footer")

def ensure_pem_format(private_key):
    """
    Stellt sicher, dass ein privater Schlüssel im PEM-Format vorliegt.
    Konvertiert bei Bedarf ein EllipticCurvePrivateKey-Objekt in einen PEM-String.
    
    Args:
        private_key: Entweder ein EllipticCurvePrivateKey-Objekt oder ein PEM-String
        
    Returns:
        Der private Schlüssel als PEM-String
        
    Raises:
        TypeError: Wenn der Eingabeschlüssel nicht unterstützt wird
    """
    # Fall 1: Der Schlüssel ist bereits ein PEM-String
    if isinstance(private_key, str):
        # Validiere den PEM-String
        try:
            validate_pem_key(private_key)
            logger.debug("Private key is already a valid PEM string")
            return private_key
        except ValueError as e:
            logger.error(f"Invalid PEM string: {e}")
            raise
    
    # Fall 2: Der Schlüssel ist ein EllipticCurvePrivateKey-Objekt
    elif isinstance(private_key, EllipticCurvePrivateKey):
        logger.debug("Converting EllipticCurvePrivateKey to PEM string")
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
    
    # Fall 3: Nicht unterstütztes Format
    else:
        logger.error(f"Unsupported key type: {type(private_key)}")
        raise TypeError(f"Unsupported private key type: {type(private_key)}. Expected a PEM string or EllipticCurvePrivateKey.")
