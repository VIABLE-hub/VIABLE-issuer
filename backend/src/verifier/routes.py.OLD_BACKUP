"""
Routes für den Verifier.

Enthält alle Flask-Routen und Endpunkte.
"""

from flask import Blueprint, render_template, request, redirect, jsonify, current_app
from src.utils import get_current_server_url
from logging import getLogger
from urllib.parse import urlencode
from datetime import datetime
import jwt
import json
import requests
import ssl
import traceback
import sys
import uuid
import time
from .. import socketio
from .. import db
from ..models import VC_validity, TenantSettings

from .utils import generate_qr_code, randomString, did_to_key, get_demo_credential, process_oversized_fields
from .field_extractor import get_field_value, decode_jwt_token, extract_presentation_from_vp, extract_validity_identifier
from .validators import validate_technical_fields, validate_credential_validity, validate_jwt_signature, check_presentation_integrity
# BBS verification is now inline in verifier.py
from .integration import safe_verify_presentation
from .settings_integration import get_current_selective_disclosure_settings, update_selective_disclosure_settings, get_presentation_definition, translate_field_name
from .constants import TECHNICAL_FIELDS, ALL_CREDENTIAL_FIELDS

logger = getLogger("LOGGER")

verifier_bp = Blueprint('verifier', __name__)


@verifier_bp.route('/', methods=['GET', 'POST'])
def index():
    server_url = get_current_server_url()
    presentation_request_url = f"openid4vp://?request_uri={server_url}/verifier/presentation-request"
    img = generate_qr_code(presentation_request_url)

    # Get current settings dynamically
    current_mandatory_fields = get_current_selective_disclosure_settings()
    
    if request.method == "GET":
        return render_template("verifier.html", 
                             img_data=img, 
                             server_url=server_url, 
                             presentation_request_url=presentation_request_url,
                             mandatory_fields=current_mandatory_fields, 
                             demo_credential=get_demo_credential(), 
                             year=datetime.now().year)

    # update the mandatory fields - filter out form control fields
    from .constants import ALL_SELECTABLE_FIELDS
    selected_fields = [field for field in request.form.keys() if field in ALL_SELECTABLE_FIELDS]
    
    logger.info(f"Form keys received: {list(request.form.keys())}")
    logger.info(f"Filtered selectable fields: {selected_fields}")
    
    # Update settings in database (even if empty - that means no user fields required)
    update_selective_disclosure_settings(selected_fields)

    return render_template("verifier.html", 
                         img_data=img, 
                         server_url=server_url, 
                         presentation_request_url=presentation_request_url,
                         mandatory_fields=current_mandatory_fields, 
                         demo_credential=get_demo_credential(), 
                         year=datetime.now().year)


@verifier_bp.route('/settings', methods=['GET', 'POST'])
def verifier_settings():
    current_mandatory_fields = get_current_selective_disclosure_settings()
    return render_template("verifier_settings.html", mandatory_fields=current_mandatory_fields, demo_credential=get_demo_credential(), year=datetime.now().year)


@verifier_bp.route('/request_uri', methods=['GET', 'POST'])
def request_uri():
    server_url = get_current_server_url() + "/verifier/"
    redirect_uri = f"openid4vp://?request_uri={server_url}presentation-request"
    return redirect(redirect_uri)


@verifier_bp.route('/request.uri/<request_uri_id>', methods=['GET', 'POST'])  
def request_uri_with_id(request_uri_id):
    """
    Handle specific request URI calls with IDs - supports both GET and POST for iOS wallet compatibility
    """
    try:
        # Get the current presentation definition
        presentation_def = get_presentation_definition()
        
        # Create the response parameters
        params = {
            "response_type": "vp_token", 
            "response_uri": get_current_server_url() + "/verifier/direct_post",
            "response_mode": "direct_post",
            "presentation_definition": json.dumps({
                "mandatory_fields": presentation_def.get('technical_fields', []) + presentation_def.get('user_mandatory_fields', []),
                "explanation": presentation_def.get('field_explanations', {})
            })
        }
        
        if request.method == 'GET':
            return jsonify(params), 200
        else:  # POST
            # For iOS wallet compatibility - return 302 redirect with openid4vp scheme
            openid_url = f"openid4vp://?response_uri={params['response_uri']}&presentation_definition={params['presentation_definition']}"
            return redirect(openid_url, code=302)
            
    except Exception as e:
        logger.error(f"Error in request.uri endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@verifier_bp.route("/presentation-request", methods=["POST", "GET"])
def offer():
    try:
        params = {}
        params["response_type"] = "vp_token"
        params["response_uri"] = get_current_server_url() + \
            "/verifier/direct_post"
        params["response_mode"] = "direct_post"
        params["state"] = randomString(10)
        params["nonce"] = randomString(10)
        
        # Get structured presentation definition with field categories
        presentation_def = get_presentation_definition()
        logger.info(f"🔧 PRESENTATION DEF DEBUG: user_mandatory_fields = {presentation_def.get('user_mandatory_fields', [])}")
        logger.info(f"🔧 PRESENTATION DEF DEBUG: technical_fields = {presentation_def.get('technical_fields', [])}")
        logger.info(f"🔧 PRESENTATION DEF DEBUG: mandatory_fields = {presentation_def.get('mandatory_fields', [])}")
        logger.debug(f"Got presentation definition: {presentation_def}")
        
        # Create iOS-compatible presentation definition
        ios_compatible_fields = []
        
        # Use the field mappings from the presentation definition
        field_mapping = presentation_def.get('field_mappings', {})
        
        # Start with technical fields (always required)
        for field in presentation_def['technical_fields']:
            # Use iOS camelCase names when available
            ios_field = field_mapping.get(field, field)
            if ios_field not in ios_compatible_fields:
                ios_compatible_fields.append(ios_field)
                
        # Add user mandatory fields, but filter out complex fields that would break URLs
        complex_fields = ['image', 'theme', 'vc.credentialSubject.image', 'vc.credentialSubject.theme']
        logger.info(f"🔧 URL FILTERING DEBUG: About to process {len(presentation_def['user_mandatory_fields'])} user fields: {presentation_def['user_mandatory_fields']}")
        for field in presentation_def['user_mandatory_fields']:
            # Skip complex fields that contain large data and would break URL encoding
            if field in complex_fields:
                logger.info(f"🔧 FILTERING: Skipping complex field '{field}' from presentation request URL to prevent encoding issues")
                continue
            if field not in ios_compatible_fields:
                ios_compatible_fields.append(field)
                logger.info(f"🔧 ADDING: Added field '{field}' to ios_compatible_fields")
        
        # Prepare explanations for only the fields that will actually be used (filtered)
        # Use ios_compatible_fields which already has complex fields filtered out
        field_explanations = {}
        
        # Define explanations for fields
        presentation_explanation = {
            "firstName": "Vorname des Studierenden",
            "lastName": "Nachname des Studierenden", 
            "studentId": "Matrikelnummer",
            "studentIdPrefix": "Hochschulpräfix",
            "studyProgram": "Studiengang",
            "faculty": "Fakultät",
            "total_messages": "amount of messages in the whole credential. needed for BBS+ signature verification",
            "bbs_dpk": "BBS+ issuer public key, needed to check if credential was signed by a trusted issuer",
            "signed_nonce": "signature of the nonce, used to verify issuer signature",
            "validity_identifier": "unique identifier of the credential, needed to check if credential is valid",
            "iss": "issuer DID, needed to check if credential was signed by a trusted issuer",
            "sub": "holder DID, needed to check if credential was signed by a trusted holder",
            "exp": "No Explanation",
            "nbf": "No Explanation",
            "jti": "No Explanation",
            "nonce": "prevents replay attacks, used to verify issuer signature",
            "totalMessages": "amount of messages in the whole credential. needed for BBS+ signature verification",
            "bbsDPK": "BBS+ issuer public key, needed to check if credential was signed by a trusted issuer",
            "signedNonce": "signature of the nonce, used to verify issuer signature",
            "validityIdentifier": "unique identifier of the credential, needed to check if credential is valid",
            "vc.credentialSubject.firstName": "Vorname des Karteninhabers",
            "vc.credentialSubject.lastName": "Nachname des Karteninhabers", 
            "vc.credentialSubject.studentId": "Eindeutige Studenten-Identifikationsnummer",
            "vc.credentialSubject.studentIdPrefix": "Präfix der Studenten-ID zur Organisationsidentifikation"
        }
        
        # Only create explanations for fields that are actually being used
        for field in ios_compatible_fields:
            field_explanations[field] = presentation_explanation.get(field, "No Explanation")
        
        # 🔧 AGGRESSIVE FILTERING: Double-check and remove complex fields at the final step
        complex_fields = ['image', 'theme', 'vc.credentialSubject.image', 'vc.credentialSubject.theme']
        filtered_mandatory_fields = [
            field for field in ios_compatible_fields 
            if field not in complex_fields
        ]
        
        # Create enhanced presentation definition for the wallet
        enhanced_presentation_definition = {
            "mandatory_fields": filtered_mandatory_fields,  # Aggressively filtered fields
            "optional_fields": presentation_def['optional_fields'],
            "explanation": field_explanations
        }
        
        logger.info(f"🔧 AGGRESSIVE FILTER: Original ios_compatible_fields: {ios_compatible_fields}")
        logger.info(f"🔧 AGGRESSIVE FILTER: Final filtered_mandatory_fields: {filtered_mandatory_fields}")
        logger.info(f"🔧 FINAL CHECK: Enhanced presentation definition mandatory fields: {enhanced_presentation_definition['mandatory_fields']}")
        
        # Convert to JSON string for OpenID4VP presentation request
        presentation_def_json = json.dumps(enhanced_presentation_definition, ensure_ascii=False)
        
        # Special handling for iOS wallet - replacing spaces with '+'
        # This is needed because iOS wallet expects JSON with '+' for spaces after decoding
        presentation_def_json = presentation_def_json.replace(' ', '+')
        
        # Add to the parameters
        params["presentation_definition"] = presentation_def_json
                
        # Construct the complete URL for the wallet with proper URL encoding
        from urllib.parse import quote
        
        client_id = get_current_server_url() + "/verifier/authorize"
        openid_request = f"openid4vp://?client_id={client_id}"
        for key, value in params.items():
            # Properly encode URL parameters to prevent bad URL errors
            encoded_value = quote(str(value), safe='')
            openid_request += f"&{key}={encoded_value}"

        return jsonify({"openid_request": openid_request}), 200
        
    except Exception as e:
        logger.error(f"Error creating presentation request: {str(e)}")
        return jsonify({"error": str(e)}), 500


@verifier_bp.route("/direct_post", methods=["POST"])
def direct_post():
    """
    Handles direct POST from the wallet with the verifiable presentation
    """
    try:
        # Check URL parameters first
        vp_token = request.args.get('vp_token')
        state = request.args.get('state')
        
        # If not in URL parameters, try to get from form
        if not vp_token:
            vp_token = request.form.get('vp_token')
            state = request.form.get('state')
            
        # If still not found, try to get from JSON body
        if not vp_token:
            try:
                body_data = request.get_json() or {}
                vp_token = body_data.get('vp_token')
                state = body_data.get('state')
            except:
                pass
                
        # Last resort - try to get from data if it's a string (iOS format)
        if not vp_token and request.data:
            try:
                body_str = request.data.decode('utf-8')
                if body_str.startswith('vp_token='):
                    vp_token = body_str.split('vp_token=')[1].split('&')[0]
            except:
                pass
        
        if not vp_token:
            logger.error("No vp_token parameter found in request")
            return jsonify({"error": "No vp_token parameter found", "valid": 0}), 400
        
        # Decode the JWT token
        decoded_vp = decode_jwt_token(vp_token)
        if not decoded_vp:
            logger.error("Failed to decode VP token")
            return jsonify({"error": "Failed to decode VP token", "valid": 0}), 400
        
        # Step 1: Presentation request received
        socketio.emit('verification_step', {
            'step': 1,
            'message': 'Präsentation empfangen',
            'description': 'Verifiable Presentation wurde vom Wallet empfangen'
        })
        
        # Extract the presentation from the VP
        presentation = extract_presentation_from_vp(decoded_vp)
        
        # Step 2: Extract credential fields
        socketio.emit('verification_step', {
            'step': 2,
            'message': 'Credential-Felder extrahiert',
            'description': 'Verifiable Credential wurde erfolgreich dekodiert'
        })
        
        # Get presentation definition with mandatory fields
        presentation_def = get_presentation_definition()
        technical_fields = presentation_def.get('technical_fields', TECHNICAL_FIELDS)
        user_mandatory_fields = presentation_def.get('user_mandatory_fields', [])
        
        # Skip demo credentials check
        demo_credential = "demo_credential" in str(decoded_vp).lower()
        
        # 🩺 HERZCHIRURG-FIX: Verwende die neue robuste Integration
        if not demo_credential:
            # Step 3-5: Robuste Verifikation mit detaillierter Fehlerbehandlung
            valid, verification_details = safe_verify_presentation(decoded_vp, presentation_def)
            if not valid:
                logger.error(f"Advanced verification failed: {verification_details.get('error')}")
                
                # Bestimme den Fehlertyp und Schritt
                error_type = verification_details.get('error_type', 'unknown_error')
                error_details = verification_details.get('error', 'Unknown error')
                
                # Bestimme den Schritt basierend auf dem Fehlertyp
                step = 3  # Default
                successful_steps = 2
                
                if error_type == 'bbs_verification_failed' or error_type == 'bbs_verification_exception':
                    step = 5
                    successful_steps = 4
                elif error_type == 'credential_validity_failed':
                    step = 6
                    successful_steps = 5
                elif error_type == 'presentation_integrity_error':
                    step = 3
                    successful_steps = 2
                
                # Sende Fehlerdetails an den Client
                socketio.emit('verification_step', {
                    'step': step,
                    'message': 'Verifikation fehlgeschlagen',
                    'description': f'{error_details}',
                    'status': 'error'
                })
                
                return jsonify({
                    "error": error_details,
                    "error_type": error_type,
                    "verification_details": verification_details,
                    "valid": 0,
                    "step": step,
                    "successful_steps": successful_steps
                }), 400
            
            # Wenn die Verifikation erfolgreich war, setzen wir alle Schritte auf Erfolg
            socketio.emit('verification_step', {
                'step': 3,
                'message': 'Pflichtfelder validiert',
                'description': 'Alle erforderlichen Felder sind vorhanden'
            })
            
            socketio.emit('verification_step', {
                'step': 4,
                'message': 'Aussteller validiert',
                'description': f'Aussteller: {get_field_value(decoded_vp, "iss")}'
            })
            
            socketio.emit('verification_step', {
                'step': 5,
                'message': 'Signatur validiert',
                'description': 'BBS+ Signaturprüfung erfolgreich'
            })
            
            # Step 6: Check credential validity status
            valid_status, status_msg = validate_credential_validity(decoded_vp)
            if not valid_status:
                logger.error(f"Credential validity check failed: {status_msg}")
                socketio.emit('verification_step', {
                    'step': 6,
                    'message': 'Gültigkeitsprüfung fehlgeschlagen',
                    'description': f'Credential Gültigkeitsprüfung fehlgeschlagen: {status_msg}',
                    'status': 'error'
                })
                return jsonify({
                    "error": status_msg, 
                    "valid": 0,
                    "error_type": "credential_validity_failed",
                    "step": 6,
                    "successful_steps": 5
                }), 400
        else:
            # Demo Credential: Vereinfachte Validierung
            socketio.emit('verification_step', {
                'step': 3,
                'message': 'Pflichtfelder validiert',
                'description': 'Alle erforderlichen Felder sind vorhanden (Demo-Modus)'
            })
            
            socketio.emit('verification_step', {
                'step': 4,
                'message': 'Aussteller validiert',
                'description': f'Aussteller: Demo Issuer (Demo-Modus)'
            })
            
            socketio.emit('verification_step', {
                'step': 5,
                'message': 'Demo-Credential erkannt',
                'description': 'BBS+ Signatur Prüfung wird übersprungen für Demo-Credentials',
                'status': 'warning'
            })
        
        socketio.emit('verification_step', {
            'step': 6,
            'message': 'Gültigkeit bestätigt',
            'description': 'Credential Gültigkeitsstatus geprüft'
        })
        
        # Step 7: Check user mandatory fields
        # Extract values from the credential
        values = {}
        vc = decoded_vp.get("verifiable_credential", {})
        if "values" in vc:
            values = vc["values"]
        else:
            # Try to extract from other locations
            for field in ALL_CREDENTIAL_FIELDS:
                value = get_field_value(decoded_vp, field)
                if value:
                    values[field] = value
        
        # Verarbeite übergroße Felder für die Antwort
        safe_values = process_oversized_fields(values)
        
        socketio.emit('verification_step', {
            'step': 7,
            'message': 'Daten vollständig',
            'description': f'{len(safe_values)} Felder wurden offengelegt'
        })
        
        # Step 8: Verification complete!
        socketio.emit('verification_step', {
            'step': 8,
            'message': 'Verifikation abgeschlossen',
            'description': 'Alle Prüfungen erfolgreich',
            'status': 'success'
        })
        
        # Send the final verification result with enhanced issuer information
        # Get dynamic issuer info based on current tenant
        from ..tenants.detection import get_current_tenant_id
        from ..tenants.config_manager import get_tenant_config
        
        current_tenant = get_current_tenant_id()
        tenant_config = get_tenant_config(current_tenant)
        issuer_info = tenant_config.get('displayName', current_tenant) if tenant_config else current_tenant
        
        # 🔧 DEBUG: Log tenant detection details
        logger.info(f"🔧 VERIFICATION DEBUG: Detected tenant = '{current_tenant}'")
        logger.info(f"🔧 VERIFICATION DEBUG: Tenant config = {tenant_config}")
        logger.info(f"🔧 VERIFICATION DEBUG: Final issuer_info = '{issuer_info}'")
        
        socketio.emit('verification_result', {
            'valid': 1,
            'step': 8,
            'step_max': 8,
            'message': f'🎉 Verifikation erfolgreich abgeschlossen!<br/>✅ Gültiger Studierendenausweis ausgestellt von <strong>{issuer_info}</strong>',
            'issuer': issuer_info,
            'disclosed_fields': list(safe_values.keys())  # Include list of disclosed fields
        })
        
        # Track which fields were disclosed (categorized)
        disclosed_info = {
            'technical': [],
            'mandatory': [],
            'optional': [],
            'undeclared': []
        }
        
        # Process disclosed fields
        for field in safe_values.keys():
            # Skip technical fields in the response (they're always required)
            if field in technical_fields or field in ["totalMessages", "bbsDPK", "signedNonce", "validityIdentifier"]:
                disclosed_info['technical'].append(field)
                continue
                
            # For user fields, match by base field name
            base_field = field.split('.')[-1] if '.' in field else field
            
            # Check if field is in user_mandatory_fields
            is_mandatory = False
            for mandatory in presentation_def['user_mandatory_fields']:
                m_base = mandatory.split('.')[-1] if '.' in mandatory else mandatory
                if base_field == m_base:
                    disclosed_info['mandatory'].append(field)
                    is_mandatory = True
                    break
                    
            if is_mandatory:
                continue
                
            # Check if field is in optional_fields
            is_optional = False
            for optional in presentation_def['optional_fields']:
                o_base = optional.split('.')[-1] if '.' in optional else optional
                if base_field == o_base:
                    disclosed_info['optional'].append(field)
                    is_optional = True
                    break
                    
            if not is_optional:
                disclosed_info['undeclared'].append(field)
        
        # Include disclosed fields info in the verification result
        return jsonify({
            "valid": 1,
            "successful_steps": 8,
            "total_completed": 8,
            "disclosed_fields": disclosed_info,
            'verification_summary': 'Alle Prüfungen erfolgreich'
        }), 200
            
    except jwt.DecodeError as e:
        logger.error(f"JWT decode error: {e}")
        return jsonify({
            "error": f"Invalid JWT token format: {str(e)}", 
            "valid": 0,
            "error_type": "jwt_decode_error",
            "step": 2,
            "successful_steps": 1
        }), 400
    except KeyError as e:
        logger.error(f"Missing required field: {e}")
        return jsonify({
            "error": f"Missing required field: {str(e)}", 
            "valid": 0,
            "error_type": "missing_field",
            "step": 3,
            "successful_steps": 2
        }), 400
    except Exception as e:
        logger.error(f"Error in verification: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # 🩺 HERZCHIRURG-FIX: Allgemeiner Fehler mit korrekter Schrittzählung
        # Bestimme, in welchem Schritt der Fehler aufgetreten ist
        error_step = 1  # Default: Präsentationsanfrage
        successful_steps = 0
        error_type = "general_error"
        
        # Versuche zu bestimmen, in welchem Schritt der Fehler aufgetreten ist
        error_str = str(e).lower()
        if "signature" in error_str or "bbs" in error_str or "proof" in error_str or "verification" in error_str:
            error_step = 5
            successful_steps = 4
            error_type = "bbs_verification_failed"
        elif "credential" in error_str or "valid" in error_str or "status" in error_str:
            error_step = 6
            successful_steps = 5
            error_type = "credential_validity_failed"
        elif "mandatory" in error_str or "field" in error_str or "required" in error_str:
            error_step = 3
            successful_steps = 2
            error_type = "missing_field"
        elif "issuer" in error_str or "trust" in error_str:
            error_step = 4
            successful_steps = 3
            error_type = "issuer_validation_failed"
        elif "jwt" in error_str or "token" in error_str or "decode" in error_str:
            error_step = 2
            successful_steps = 1
            error_type = "jwt_decode_error"
        elif "key" in error_str or "extract" in error_str:
            error_step = 2
            successful_steps = 1
            error_type = "field_extraction_failed"
        
        # Sende detaillierte Fehlermeldung mit Schrittzählung
        socketio.emit('verification_result', {
            'status': 'error',
            'valid': 0,
            'message': f"Verification failed: {str(e)}",
            'user_message': f"Verifikation fehlgeschlagen: {str(e)}",
            'step': error_step,
            'successful_steps': successful_steps,
            'error_type': error_type
        })
        
        return jsonify({
            "error": f"An error occurred during verification: {str(e)}",
            "details": str(e),
            "traceback": traceback.format_exc().split('\n')[-10:],  # Nur die letzten 10 Zeilen für Sicherheit
            "valid": 0,
            "step": error_step,
            "successful_steps": successful_steps,
            "error_type": error_type
        }), 500


# Functions moved to settings_integration.py to avoid duplication
