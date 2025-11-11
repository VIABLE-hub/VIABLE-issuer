"""
Response Formatter für Backend-iOS Kompatibilität
Standardisiert API-Antworten zwischen Backend und iOS
"""

from flask import jsonify
from typing import Dict, Any, Optional

def success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Standardisierte Erfolgsantwort für iOS"""
    return {
        "success": True,
        "message": message,
        "data": data
    }

def error_response(message: str, code: int = 400, details: Optional[Dict] = None) -> Dict[str, Any]:
    """Standardisierte Fehlerantwort für iOS"""
    response = {
        "success": False,
        "message": message,
        "error_code": code
    }
    if details:
        response["details"] = details
    return response

def format_credential_response(credential_jwt: str, signature: str, c_nonce: str, c_nonce_expires_in: int) -> Dict[str, Any]:
    """Formatiert Credential-Antwort für iOS-Kompatibilität"""
    return success_response({
        "format": "bbs+_vc",
        "credential": credential_jwt,
        "signature": signature,
        "c_nonce": c_nonce,
        "c_nonce_expires_in": c_nonce_expires_in
    }, "Credential issued successfully")

def format_presentation_request(redirect_uri: str, state: str, nonce: str) -> Dict[str, Any]:
    """Formatiert Presentation Request für iOS-Kompatibilität"""
    return success_response({
        "redirect_uri": redirect_uri,
        "state": state,
        "nonce": nonce
    }, "Presentation request created")
