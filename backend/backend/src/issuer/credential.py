from flask import request, jsonify, current_app
from src.utils import get_current_server_url
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from ..models import VC_Offer
from .offer import generate_nonce
import logging
from flask import current_app as app
from flatten_json import flatten
import json
import os
import importlib.util
import base64
from .utils import get_placeholders
from ..models import VC_validity
from .. import db

logo, profile = get_placeholders()

bbs_core_path = os.path.join(os.path.dirname(
    __file__), "..", "..", "bbs_core.py")
bbs_core_path = os.path.abspath(bbs_core_path)
spec = importlib.util.spec_from_file_location("bbs_core", bbs_core_path)
bbs_core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bbs_core)

logger = logging.getLogger(__name__)


def generate_credential(auth_header, public_key, private_key, issuer_did, issuer_kid, bbs_dpk, bbs_secret):
    if not auth_header:
        return jsonify({"error": "Authorization header is missing"}), 401

    token = auth_header.split(" ")[1]
    decoded_token = jwt.decode(token, public_key, algorithms=["ES256"])
    credential_identifier = decoded_token.get("credential_identifier")

    if not credential_identifier:
        return jsonify({"error": "Credential identifier is missing"}), 400

    logger.debug(f"offer_uuid: {credential_identifier}")
    credential_data = VC_Offer.query.filter_by(
        uuid=credential_identifier).first()
    logger.info(f"🔍 CREDENTIAL DEBUG - Found VC_Offer in database: {credential_data}")
    if credential_data:
        logger.info(f"🔍 CREDENTIAL DEBUG - VC_Offer UUID: {credential_data.uuid}")
        logger.info(f"🔍 CREDENTIAL DEBUG - VC_Offer credential_data: {credential_data.credential_data}")
    credential_subject = get_credential_data(credential_data)
    logger.info(f"🔍 CREDENTIAL DEBUG - Final credential_subject: {credential_subject}")
    # Create the Verifiable Credential payload
    uniqID = f"urn:uuid:{str(uuid4())}"
    payload = get_payload(issuer_did, decoded_token,
                          credential_subject, uniqID)

    nonce = generate_nonce(20)
    payload["nonce"] = nonce
    payload["signed_nonce"] = jwt.encode(
        {"nonce": nonce}, private_key, algorithm="ES256")
    unique_id = generate_nonce(50)
    unique_id_path = get_current_server_url() + \
        "/vcstatus/isvalid/" + unique_id
    payload["validity_identifier"] = unique_id_path
    logger.debug(f"Payload before BBS+ metadata: {payload}")

    # Flatten the payload BEFORE adding BBS+ metadata to avoid including metadata in signature
    flattened_payload = flatten(payload, '.')
    
    # Define BBS+ metadata fields that should be excluded from message signing
    bbs_metadata_fields = {"bbs_dpk", "total_messages"}
    
    # Create messages with consistent JSON formatting (no spaces, compact)
    # IMPORTANT: Exclude BBS+ metadata fields from message creation to ensure they're not part of signature
    filtered_payload = {key: value for key, value in flattened_payload.items() 
                      if key not in bbs_metadata_fields}
    
    to_sign = [json.dumps({key: filtered_payload[key]}, ensure_ascii=False, separators=(',', ':'))
               for key in sorted(filtered_payload.keys())]
    
    logger.debug(f"Credential fields before filtering: {sorted(flattened_payload.keys())}")
    logger.debug(f"Credential fields after filtering BBS+ metadata: {sorted(filtered_payload.keys())}")
    logger.debug(f"Messages to sign (excluding BBS+ metadata): {json.dumps(to_sign, indent=4)}")
    logger.debug(f"Total messages to sign (excluding BBS+ metadata): {len(to_sign)}")
    
    # Sign the credential data (without BBS+ metadata)
    signer = bbs_core.SignRequest(to_sign, bbs_dpk, bbs_secret)
    sign_result = signer.sign_messages()

    # Add BBS+ metadata to payload AFTER signing to prevent it from being included in the message hash
    payload["bbs_dpk"] = base64.b64encode(bbs_dpk).decode('utf-8')
    payload["total_messages"] = len(filtered_payload.keys())  # Count ONLY the signed fields
    logger.debug(f"Payload after adding BBS+ metadata: {payload}")
    logger.debug(f"Total messages count (excluding BBS+ metadata): {payload['total_messages']}")

    signature_bytes = base64.b64encode(sign_result.signature).decode()

    # Additional headers
    additional_headers = {
        "kid": issuer_kid,
        "alg": "ES256",
        "typ": "JWT",
    }

    vc_validity = VC_validity(identifier=unique_id, credential_data=payload)
    db.session.add(vc_validity)
    db.session.commit()

    # Generate the VC JWT
    vc_jwt = jwt.encode(payload, private_key,
                        algorithm="ES256", headers=additional_headers)
    c_nonce = generate_nonce(10)
    c_nonce_expires_in = 86400  # 24 hours

    # Send the response with the VC JWT and nonce
    return jsonify({
        "format": "bbs+_vc",
        "credential": vc_jwt,
        "signature": signature_bytes,
        "c_nonce": c_nonce,
        "c_nonce_expires_in": c_nonce_expires_in,
    }), 200


def get_payload(issuer_did, decoded_token, credential_subject, uniqID):
    payload = {
        "iat": int(datetime.now(tz=timezone.utc).timestamp()) - 60,
        "iss": issuer_did,
        "sub": decoded_token.get("sub", ""),
        # 1 hour expiration
        "exp": int(datetime.now(tz=timezone.utc).timestamp()) + 60 * 60,
        "nbf": int(datetime.now(tz=timezone.utc).timestamp()),
        "jti": uniqID,
        "vc": {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "type": [
                "VerifiableCredential",
                "VerifiableAttestation",
                "StudentIDCard"
            ],
            "id": uniqID,
            "issuer": issuer_did,
            "issuanceDate": datetime.utcnow().isoformat(),
            "validFrom": datetime.utcnow().isoformat(),
            "credentialSubject": credential_subject,
            "credentialSchema": {
                "id": "https://api-conformance.ebsi.eu/trusted-schemas-registry/v3/schemas/zDpWGUBenmqXzurskry9Nsk6vq2R8thh9VSeoRqguoyMD",
                "type": "FullJsonSchemaValidator2021"
            },
            "expirationDate": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        },
    }

    return payload


def get_credential_data(credential_data):
    logger.info(f"🔍 CREDENTIAL DEBUG - Input credential_data object: {credential_data}")
    logger.info(f"🔍 CREDENTIAL DEBUG - Type of credential_data: {type(credential_data)}")
    
    actual_data = credential_data.credential_data if credential_data else None
    logger.info(f"🔍 CREDENTIAL DEBUG - Extracted credential_data: {actual_data}")
    logger.info(f"🔍 CREDENTIAL DEBUG - Type of extracted data: {type(actual_data)}")
    
    if not actual_data:
        logger.warning(f"🔍 CREDENTIAL DEBUG - No credential data found, using defaults!")
        logger.warning(f"🔍 CREDENTIAL DEBUG - This explains why user fields are missing!")
        return {
            "firstName": "Maxi" + f"{str(generate_nonce(5))}",
            "lastName": "Musterfrau" + f"{str(generate_nonce(5))}",
            "issuanceCount": "1",
            "image": profile,
            "studentId": f"{str(generate_nonce(5))}",
            "studentIdPrefix": "654321",
            "theme": {
                "name": "Technische Universität Berlin",
                "icon": logo,
                "bgColorCard": "C40D1E",
                "bgColorSectionTop": "C40D1E",
                "bgColorSectionBot": "FFFFFF",
                "fgColorTitle": "FFFFFF"
            }
        }

    logger.info(f"🔍 CREDENTIAL DEBUG - Using actual credential data with keys: {list(actual_data.keys()) if isinstance(actual_data, dict) else 'Not a dict'}")
    return actual_data


def resolve_credential_offer(id):
    offer = VC_Offer.query.filter_by(uuid=id).first()

    # Initialize variables
    iss_state = None
    pre_auth_code = None
    credential_data = None

    if offer:
        logger.debug(f"Offer: {offer.uuid}")
        iss_state = offer.issuer_state
        pre_auth_code = offer.pre_authorized_code
        credential_data = offer.credential_data

        logger.info(f"Credential Data: {credential_data}")

        if iss_state:
            # You can implement logic to store the offer in the database if needed
            pass

        if pre_auth_code:
            # You can implement logic to store the offer in the database if needed
            pass

    logger.info(f"State: {iss_state}, Pre-Auth Code: {pre_auth_code}")

    # Prepare the response
    response = {
        "credential_issuer": get_current_server_url(),
        "credentials": credential_data.get('type', ["UniversityDegreeCredential"]) if credential_data else ["UniversityDegreeCredential"],
        "grants": {
            "authorization_code": {
                # Generate a new UUID if no issuer_state
                "issuer_state": iss_state or str(uuid4()),
            }
        }
    }

    return jsonify(response), 200
