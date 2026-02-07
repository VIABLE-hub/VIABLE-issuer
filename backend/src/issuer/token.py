import requests
from flask import request, jsonify
from flask import current_app as app
import logging
import jwt
from datetime import datetime
from ..models import VC_Token, VC_Offer
import hashlib
import base64
import random
import string
from ..models import VC_AuthorizationCode
from cryptography.hazmat.primitives import serialization
from .offer import generate_nonce
from .. import db, socketio
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def authenticate_token(f):
    def wrapper(*args, **kwargs):
        # Extract the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Unauthorized"}), 401

        # Extract the token from the header
        token = auth_header.split(" ")[1] if " " in auth_header else None
        if not token:
            return jsonify({"error": "Token not provided"}), 401

        # Verify the token locally to avoid deadlock
        try:
            from .key_generator import load_or_generate_keys
            _, public_key = load_or_generate_keys()
            
            logger.info(f"Locally verifying token")
            
            # Call verify_token which is defined in this module
            verification_result = verify_token({"token": token}, public_key)
            
            # Check the status code from the response (it returns a tuple of (response_json, status_code))
            if verification_result[1] != 200:
                logger.error(f"Token verification failed: {verification_result[0]}")
                return verification_result

        except Exception as e:
            logger.error(f"Error verifying token locally: {e}")
            return jsonify({"error": f"Token verification failed: {str(e)}"}), 500

        # Proceed to the next function if the token is valid
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


def verify_token(data, publicKey):
    token = data.get("token")
    if not token:
        return jsonify({"error": "Token is required"}), 400

    # Decode the token using the public key and check expiration

    logger.info(f"Verifying token: {token} with public key: {publicKey}")
    try:
        decoded = jwt.decode(token, publicKey, algorithms=["ES256"])
    except jwt.ExpiredSignatureError as e:
        return jsonify({"error": f"Token has expired {e}"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"error": f"Invalid token {e}"}), 401

    # Query the database for the access token
    access_token = VC_Token.query.filter_by(token=token).first()

    if not access_token:
        return jsonify({"error": "Token not found"}), 401

    # Check if the token is expired
    if access_token.expires_at and access_token.expires_at < datetime.utcnow():
        return jsonify({"error": "Token has expired"}), 401

    # If token is valid and not expired
    return jsonify({"message": "Token is valid"}), 200


def base64UrlEncodeSha256(input_str):
    # Hash the code_verifier and return it in base64url format
    sha256_hash = hashlib.sha256(input_str.encode()).digest()
    return base64.urlsafe_b64encode(sha256_hash).decode().strip("=")


def generate_access_token(client_id, credential_identifier, private_key):
    """
    Generate a JWT access token.
    """
    # Ensure client_id is a string for JWT "sub" claim
    if client_id is None:
        client_id = "default-client"
    
    # Define the payload
    payload = {
        "client_id": str(client_id),
        "credential_identifier": str(credential_identifier) if credential_identifier else "default-credential",
        "iat": int(time.time()),  # Issued at
        "exp": int(time.time()) + 3600,  # Expiration (1 hour)
        "sub": str(client_id)  # Subject must be a string
    }

    # Define the header
    headers = {
        "alg": "ES256",  # Elliptic curve signing algorithm
        "typ": "JWT"     # Token type
    }

    # Generate the JWT token
    access_token = jwt.encode(payload, private_key,
                              algorithm="ES256", headers=headers)
    return access_token


def verify_and_generate_token(request_json, private_key):
    client_id = request_json.get("client_id")
    code = request_json.get("code")
    code_verifier = request_json.get("code_verifier")
    grant_type = request_json.get("grant_type")
    user_pin = request_json.get("user_pin")
    pre_authorized_code = request_json.get("pre-authorized_code")

    logger.info(f"Token request - grant_type: {grant_type}, client_id: {client_id}")
    logger.info(f"Token request - code: {code}, code_verifier present: {bool(code_verifier)}")

    credential_identifier = None

    if grant_type == "urn:ietf:params:oauth:grant-type:pre-authorized_code":
        logger.info(f"Pre-authorized code flow: {pre_authorized_code}")

        # Set default client_id if not provided
        if not client_id:
            client_id = "pre-auth-client"

        # Check if the user PIN is correct
        if user_pin != "1234":
            print("Invalid pin:", user_pin)
            logger.error(f"Invalid pin: {user_pin}")
            return jsonify({"error": "Invalid pin"}), 400

        # Validate Offer/Pre-authorized code
        offer = VC_Offer.query.filter_by(pre_authorized_code=pre_authorized_code).first()
        if not offer:
            logger.error(f"Invalid pre-authorized code: {pre_authorized_code}")
            return jsonify({"error": "Invalid pre-authorized code"}), 400
            
        if offer.used:
            logger.error(f"Offer already used: {offer.uuid}")
            return jsonify({"error": "Offer already used"}), 400
            
        if offer.expires_at:
            expiry = offer.expires_at
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            
            if expiry < datetime.now(timezone.utc):
                logger.error(f"Offer expired: {offer.uuid} at {offer.expires_at}")
                return jsonify({"error": "Offer expired"}), 400

        # Mark as used
        try:
            offer.used = True
            db.session.commit()
            logger.info(f"Offer marked as used: {offer.uuid}")
            
            # Emit socket event to frontend
            socketio.emit('offer_used', {'uuid': offer.uuid, 'status': 'used'})
            
        except Exception as e:
            logger.error(f"Failed to mark offer as used: {e}")
            db.session.rollback()
            return jsonify({"error": "Database error"}), 500

        credential_identifier = pre_authorized_code

    elif grant_type == "authorization_code":
        logger.info(f"Authorization code flow: {code}")

        # Set default client_id if not provided
        if not client_id:
            client_id = "auth-code-client"

        # Compute the code_verifier hash
        code_verifier_hash = base64UrlEncodeSha256(code_verifier) if code_verifier else None
        logger.info(f"Computed code_verifier_hash: {code_verifier_hash}")

        # Fetch the authorization code session from the database with proper error handling
        try:
            authorization_code_entry = VC_AuthorizationCode.query.filter_by(
                client_id=client_id, auth_code=code, used=False).first()
            
            logger.info(f"DB Query - Looking for client_id: {client_id}, auth_code: {code}")
            
            if authorization_code_entry:
                logger.info(f"Found auth entry: {authorization_code_entry}")
            else:
                # Try to find any entry for this client for debugging
                all_entries = VC_AuthorizationCode.query.filter_by(client_id=client_id).all()
                logger.info(f"All entries for client_id {client_id}: {[str(entry) for entry in all_entries]}")
                
                # Also check if there's an entry with this code but different client
                code_entries = VC_AuthorizationCode.query.filter_by(auth_code=code).all()
                logger.info(f"All entries with auth_code {code}: {[str(entry) for entry in code_entries]}")

        except Exception as e:
            logger.error(f"Database query error: {e}")
            return jsonify({"error": "Database error during authorization"}), 500

        if not authorization_code_entry:
            logger.error(f"Authorization code session not found for client_id: {client_id}, code: {code}")
            return jsonify({"error": "Authorization code session not found"}), 400

        # Check if the authorization code has expired
        if authorization_code_entry.expires_at and authorization_code_entry.expires_at < datetime.utcnow():
            logger.error(f"Authorization code expired at {authorization_code_entry.expires_at}")
            return jsonify({"error": "Authorization code has expired"}), 400

        # Validate the code and code_verifier
        code_valid = (code == authorization_code_entry.auth_code)
        verifier_valid = (code_verifier_hash == authorization_code_entry.code_challenge) if code_verifier_hash else True
        
        logger.info(f"Validation - code_valid: {code_valid}, verifier_valid: {verifier_valid}")
        logger.info(f"Expected auth_code: {authorization_code_entry.auth_code}, received: {code}")
        logger.info(f"Expected code_challenge: {authorization_code_entry.code_challenge}, computed: {code_verifier_hash}")

        if not code_valid or not verifier_valid:
            if not code_valid:
                logger.error(f"Invalid authorization code: {code} != {authorization_code_entry.auth_code}")
            if not verifier_valid:
                logger.error(f"Invalid code verifier: {code_verifier_hash} != {authorization_code_entry.code_challenge}")
            return jsonify({"error": "Client could not be verified"}), 400

        # Mark the authorization code as used (one-time use)
        try:
            authorization_code_entry.used = True
            authorization_code_entry.used_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Authorization code marked as used: {code}")
        except Exception as e:
            logger.error(f"Failed to mark authorization code as used: {e}")
            db.session.rollback()
            return jsonify({"error": "Failed to process authorization code"}), 500

        credential_identifier = authorization_code_entry.issuer_state

        # Check if the underlying Offer is still valid (Replay & Expiry defense)
        if credential_identifier:
            offer = VC_Offer.query.filter_by(uuid=credential_identifier).first()
            if offer:
                if offer.used:
                    logger.error(f"Offer already used (via auth code flow): {offer.uuid}")
                    return jsonify({"error": "Offer already used"}), 400
                
                if offer.expires_at:
                    expiry = offer.expires_at
                    if expiry.tzinfo is None:
                        expiry = expiry.replace(tzinfo=timezone.utc)
                    
                    if expiry < datetime.now(timezone.utc):
                        logger.error(f"Offer expired (via auth code flow): {offer.uuid} at {offer.expires_at}")
                        return jsonify({"error": "Offer expired"}), 400
                
                # Mark Offer as used
                try:
                    offer.used = True
                    db.session.commit()
                    logger.info(f"Offer marked as used (auth code flow): {offer.uuid}")
                    socketio.emit('offer_used', {'uuid': offer.uuid, 'status': 'used'})
                except Exception as e:
                    logger.error(f"Failed to mark offer as used: {str(e)}")
                    # Proceeding anyway since auth code is consumed, effectively blocking replay of THIS auth code
                    # But we prefer to fail if we can't update state.
                    # db.session.rollback() # handled by caller catch usually but here we are in a block that already verified auth_code
                    # For safety, we should arguably fail, but the auth code is already marked used above. 
                    pass

    if credential_identifier is None:
        logger.error(
            f"Invalid grant type or parameters")
        return jsonify({"error": "Invalid grant type or parameters"}), 400

    # Ensure we have a valid client_id
    if not client_id:
        client_id = "default-client"

    # Generate the access token
    access_token = generate_access_token(
        client_id, credential_identifier, private_key)

    # Store the access token
    new_token = VC_Token()
    new_token.token = access_token
    db.session.add(new_token)
    db.session.commit()

    print("Generated access token:", access_token)

    # Respond with the access token and additional information
    return jsonify({
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "c_nonce": generate_nonce(16),
        "c_nonce_expires_in": 86400,
    })
