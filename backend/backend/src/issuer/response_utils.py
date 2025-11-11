"""
Response-Utilities für alle Issuer-Endpoints.
Stellt konsistente JSON-Antworten mit iOS-Kompatibilität sicher.
"""

from flask import jsonify, Response
import json
import logging

logger = logging.getLogger(__name__)

def create_json_response(data, status_code=200):
    """
    Erstellt eine konsistente JSON-Antwort mit korrekten Content-Type-Headern.
    Führt Validierung durch und stellt sicher, dass alle Felder gültig sind.
    
    Args:
        data (dict): Die Daten für die JSON-Antwort
        status_code (int): Der HTTP-Statuscode (default: 200)
    
    Returns:
        Response: Ein Flask-Response-Objekt mit JSON-Inhalt und korrekten Headern
    """
    # Format für iOS-Kompatibilität garantieren (wenn für VC-Antworten)
    if "credential" in data and "format" not in data:
        data["format"] = "bbs+_vc"  # Standardformat für iOS
    
    # None-Werte durch leere Strings oder 0 ersetzen
    for key, value in list(data.items()):
        if value is None:
            if key in ["credential", "signature", "signed_nonce", "c_nonce"]:
                data[key] = ""
            elif key == "c_nonce_expires_in":
                data[key] = 0
    
    try:
        # JSON serialisieren mit strikter Validierung
        json_response = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        
        # Doppelt prüfen, dass die Serialisierung valid ist
        json.loads(json_response)
        
        logger.debug(f"✅ JSON-Response validiert: {len(json_response)} Zeichen")
        return Response(
            json_response,
            status=status_code,
            mimetype='application/json',
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
    except Exception as e:
        logger.error(f"❌ JSON-Serialisierungsfehler: {e}")
        # Fallback für Fehlerfälle
        fallback_data = {
            "error": "Interner JSON-Serialisierungsfehler",
            "details": str(e)
        }
        if "format" in data:
            fallback_data["format"] = "bbs+_vc"
        
        return jsonify(fallback_data), 500


def create_error_response(message, details=None, status_code=400):
    """
    Erstellt eine konsistente Fehlerantwort.
    
    Args:
        message (str): Die Hauptfehlermeldung
        details (str, optional): Details zum Fehler
        status_code (int): Der HTTP-Statuscode (default: 400)
    
    Returns:
        Response: Ein Flask-Response-Objekt mit Fehlerinformationen
    """
    error_data = {
        "error": message,
        "format": "bbs+_vc"  # Für iOS-Kompatibilität immer mitgeben
    }
    
    if details:
        error_data["details"] = details
    
    return create_json_response(error_data, status_code)
