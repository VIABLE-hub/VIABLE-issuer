"""
JWT-Hilfsfunktionen für iOS-kompatible Zeitstempel und Datumswerte.
"""

from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

def create_ios_compatible_timestamps(offset_seconds=0, expiry_hours=1):
    """
    Erstellt iOS-kompatible Zeitstempel als Float-Werte.
    
    Args:
        offset_seconds (int): Versatz in Sekunden für iat (Default: 0)
        expiry_hours (int): Gültigkeitsdauer in Stunden (Default: 1)
    
    Returns:
        dict: Dictionary mit iat, exp, nbf als Float-Werten
    """
    current_timestamp = datetime.now(tz=timezone.utc).timestamp()
    
    return {
        "iat": float(current_timestamp - offset_seconds),  # Float für iOS Double
        "exp": float(current_timestamp + (expiry_hours * 3600)),  # Float für iOS Double
        "nbf": float(current_timestamp),  # Float für iOS Double
    }

def create_ios_compatible_iso_dates(offset_hours=0, expiry_hours=1):
    """
    Erstellt iOS-kompatible ISO8601-Datumswerte mit Z-Suffix.
    
    Args:
        offset_hours (int): Versatz in Stunden (Default: 0)
        expiry_hours (int): Gültigkeitsdauer in Stunden (Default: 1)
    
    Returns:
        dict: Dictionary mit issuanceDate, validFrom, expirationDate als ISO8601-Strings mit Z
    """
    now = datetime.now(tz=timezone.utc)
    offset_time = now + timedelta(hours=offset_hours)
    expiry_time = now + timedelta(hours=expiry_hours)
    
    return {
        "issuanceDate": offset_time.isoformat().replace("+00:00", "Z"),
        "validFrom": offset_time.isoformat().replace("+00:00", "Z"),
        "expirationDate": expiry_time.isoformat().replace("+00:00", "Z"),
    }

def verify_ios_jwt_compatibility(payload):
    """
    Überprüft, ob ein JWT-Payload iOS-kompatibel ist.
    
    Args:
        payload (dict): Der zu prüfende JWT-Payload
        
    Returns:
        tuple: (bool, str) - (ist_kompatibel, fehlermeldung_oder_leer)
    """
    # Prüfe Timestamp-Formate
    for field in ["iat", "exp", "nbf"]:
        if field not in payload:
            return False, f"Feld '{field}' fehlt im JWT-Payload"
        if not isinstance(payload[field], float):
            return False, f"Feld '{field}' ist kein Float sondern {type(payload[field]).__name__}"
    
    # Prüfe VC und Datumsformate
    if "vc" not in payload:
        return False, "'vc'-Feld fehlt im JWT-Payload"
    
    vc = payload["vc"]
    for field in ["issuanceDate", "validFrom", "expirationDate"]:
        if field not in vc:
            return False, f"Feld '{field}' fehlt im VC-Teil"
        if not isinstance(vc[field], str):
            return False, f"Feld '{field}' ist kein String"
        if not vc[field].endswith("Z"):
            return False, f"Feld '{field}' endet nicht mit 'Z': {vc[field]}"
    
    return True, ""
