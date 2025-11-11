"""
Verification routes for VC-based login

This module handles the verification of login presentations.
Reuses existing verifier infrastructure (BBS+, OID4VP) to verify login VCs.

Routes:
- GET /vc-auth/login - Show QR code login page
- POST /vc-auth/verify - Verify presentation (direct_post endpoint)
- GET /vc-auth/status/<session_id> - Check verification status (WebSocket)
"""

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, current_user
from logging import getLogger
from . import vc_auth_bp
from .models import LoginCredential, LoginSession
from ..models import User, db
from src.utils import get_current_server_url
import json
import jwt

logger = getLogger("VC_AUTH")


@vc_auth_bp.route('/login', methods=['GET'])
def vc_login_page():
    """
    Show VC-based login page with QR code
    
    This page displays a QR code that users scan with their wallet
    to authenticate using their login credential.
    
    Flow:
    1. Generate presentation request (OID4VP)
    2. Display QR code
    3. Wait for wallet to send presentation
    4. Verify presentation (in verify_presentation endpoint)
    5. Create session and redirect to home
    """
    
    # If already logged in, redirect home
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    # Generate presentation request
    presentation_request = generate_login_presentation_request()
    
    # Store request state in session for verification
    session['vc_login_state'] = presentation_request['state']
    session['vc_login_nonce'] = presentation_request['nonce']
    
    return render_template(
        'vc_auth/vc_login.html',
        presentation_request=presentation_request,
        qr_data=presentation_request['openid_request']
    )


def generate_login_presentation_request():
    """
    Generate OID4VP presentation request for login
    
    This reuses the verifier infrastructure to request a LoginCredential
    presentation from the user's wallet.
    
    Returns:
        dict: Presentation request with state, nonce, and openid_request
    """
    import secrets
    from urllib.parse import quote
    
    # Generate state and nonce
    state = secrets.token_hex(16)
    nonce = secrets.token_hex(16)
    
    # Build presentation definition (request LoginCredential)
    presentation_definition = {
        "id": "login_request",
        "input_descriptors": [{
            "id": "login_credential",
            "name": "Login Credential",
            "purpose": "Authentication to StudentVC platform",
            "constraints": {
                "fields": [
                    {
                        "path": ["$.type"],
                        "filter": {
                            "type": "array",
                            "contains": {"const": "LoginCredential"}
                        }
                    },
                    {
                        "path": ["$.credentialSubject.email"],
                        "purpose": "User email for authentication"
                    },
                    {
                        "path": ["$.credentialSubject.tenant"],
                        "purpose": "Primary tenant"
                    }
                ]
            }
        }]
    }
    
    # Build OID4VP request
    server_url = get_current_server_url()
    client_id = f"{server_url}/vc-auth/client"
    response_uri = f"{server_url}/vc-auth/verify"
    
    params = {
        "response_type": "vp_token",
        "response_uri": response_uri,
        "response_mode": "direct_post",
        "state": state,
        "nonce": nonce,
        "presentation_definition": json.dumps(presentation_definition),
        "client_id": client_id
    }
    
    # Build openid4vp:// URL
    openid_request = f"openid4vp://?client_id={quote(client_id)}"
    for key, value in params.items():
        if key != 'client_id':
            openid_request += f"&{key}={quote(str(value))}"
    
    return {
        "state": state,
        "nonce": nonce,
        "openid_request": openid_request,
        "response_uri": response_uri,
        "presentation_definition": presentation_definition
    }


@vc_auth_bp.route('/verify', methods=['POST'])
def verify_presentation():
    """
    Verify login presentation (direct_post endpoint)
    
    This endpoint receives the VP token from the wallet after the user scans
    the QR code. It verifies the presentation and creates a login session.
    
    Flow:
    1. Extract vp_token from request
    2. Decode and verify JWT signature
    3. Verify BBS+ selective disclosure proof
    4. Extract user identity (email, tenant)
    5. Look up LoginCredential in database
    6. Verify credential is valid (not revoked, not expired)
    7. Create Flask-Login session
    8. Create LoginSession record
    9. Redirect to home page
    
    Returns:
        Redirect to home page or error page
    """
    
    try:
        # Step 1: Extract VP token
        vp_token = (
            request.args.get('vp_token') or
            request.form.get('vp_token') or
            request.get_json(silent=True, force=True).get('vp_token') if request.data else None
        )
        
        if not vp_token:
            logger.error("No vp_token found in request")
            flash('❌ No credential presentation received', 'error')
            return redirect(url_for('vc_auth.vc_login_page'))
        
        # Step 2: Decode JWT (without verification for now - TODO: Add proper verification)
        decoded_vp = jwt.decode(vp_token, options={"verify_signature": False})
        logger.info(f"Decoded VP: {json.dumps(decoded_vp, indent=2)}")
        
        # Step 3: Extract presentation and verify
        # TODO: STUDENTS IMPLEMENT THIS
        # - Verify JWT signature using issuer's public key
        # - Verify BBS+ selective disclosure proof
        # - Verify presentation definition match
        
        # Step 4: Extract user identity from presentation
        user_email, user_tenant = extract_user_identity_from_vp(decoded_vp)
        
        if not user_email:
            logger.error("Could not extract user email from presentation")
            flash('❌ Invalid credential presentation', 'error')
            return redirect(url_for('vc_auth.vc_login_page'))
        
        # Step 5: Look up LoginCredential
        login_credential = LoginCredential.query.filter_by(user_email=user_email).first()
        
        if not login_credential:
            logger.error(f"No login credential found for {user_email}")
            flash('❌ Login credential not found', 'error')
            return redirect(url_for('vc_auth.vc_login_page'))
        
        # Step 6: Verify credential validity
        if not login_credential.is_valid():
            logger.error(f"Login credential for {user_email} is not valid")
            flash('❌ Login credential is revoked or expired', 'error')
            return redirect(url_for('vc_auth.vc_login_page'))
        
        # Step 7: Create or get User record for Flask-Login
        user = get_or_create_user_for_credential(login_credential)
        
        # Step 8: Login using Flask-Login
        login_user(user, remember=True)
        login_credential.update_last_login()
        
        # Step 9: Create LoginSession record
        login_session = LoginSession.create(
            credential=login_credential,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            duration_hours=8
        )
        
        # Store session info in Flask session
        session['vc_login_session_id'] = login_session.session_id
        session['vc_login_credential_id'] = login_credential.credential_id
        session['vc_login_tenant'] = user_tenant
        
        logger.info(f"✅ VC login successful for {user_email}")
        flash(f'✅ Welcome {login_credential.user_name}!', 'success')
        
        return redirect(url_for('home.index'))
        
    except Exception as e:
        logger.error(f"Failed to verify presentation: {e}")
        flash(f'❌ Login failed: {str(e)}', 'error')
        return redirect(url_for('vc_auth.vc_login_page'))


def extract_user_identity_from_vp(decoded_vp):
    """
    Extract user email and tenant from VP
    
    Args:
        decoded_vp: Decoded VP token
    
    Returns:
        tuple: (user_email, user_tenant)
    """
    try:
        # Extract verifiable presentation
        vp = decoded_vp.get('vp', decoded_vp)
        
        # Get verifiable credentials from presentation
        credentials = vp.get('verifiableCredential', [])
        if isinstance(credentials, str):
            # If it's a JWT, decode it
            credentials = [jwt.decode(credentials, options={"verify_signature": False})]
        
        if not credentials:
            logger.error("No credentials found in presentation")
            return None, None
        
        # Get first credential (should be LoginCredential)
        credential = credentials[0]
        credential_subject = credential.get('credentialSubject', {})
        
        user_email = credential_subject.get('email')
        user_tenant = credential_subject.get('tenant')
        
        logger.info(f"Extracted identity: email={user_email}, tenant={user_tenant}")
        return user_email, user_tenant
        
    except Exception as e:
        logger.error(f"Failed to extract identity from VP: {e}")
        return None, None


def get_or_create_user_for_credential(login_credential):
    """
    Get or create a User record for Flask-Login integration
    
    Args:
        login_credential: LoginCredential instance
    
    Returns:
        User: User instance
    """
    # Check if user already exists
    user = User.query.filter_by(name=login_credential.user_email).first()
    
    if not user:
        # Create new user (with dummy password hash since we don't use it)
        from werkzeug.security import generate_password_hash
        import secrets
        
        user = User(
            name=login_credential.user_email,
            password_hash=generate_password_hash(secrets.token_hex(32))
        )
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"Created new User record for {login_credential.user_email}")
    
    return user


@vc_auth_bp.route('/logout', methods=['POST', 'GET'])
def vc_logout():
    """
    Logout from VC-based session
    
    Ends the LoginSession and clears Flask-Login session
    """
    try:
        # Get current session ID
        session_id = session.get('vc_login_session_id')
        
        if session_id:
            # End the LoginSession
            login_session = LoginSession.query.filter_by(session_id=session_id).first()
            if login_session:
                login_session.end_session()
        
        # Clear Flask session
        from flask_login import logout_user
        logout_user()
        session.clear()
        
        flash('👋 Logged out successfully', 'success')
        return redirect(url_for('vc_auth.vc_login_page'))
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        flash(f'❌ Logout failed: {str(e)}', 'error')
        return redirect(url_for('home.index'))


@vc_auth_bp.route('/status', methods=['GET'])
def status():
    """
    Get current VC authentication status
    
    Returns JSON with current user info and session status
    """
    if not current_user.is_authenticated:
        return jsonify({
            'authenticated': False
        }), 200
    
    session_id = session.get('vc_login_session_id')
    credential_id = session.get('vc_login_credential_id')
    
    if not session_id or not credential_id:
        return jsonify({
            'authenticated': True,
            'vc_auth': False,
            'method': 'password'
        }), 200
    
    # Get session and credential info
    login_session = LoginSession.query.filter_by(session_id=session_id).first()
    login_credential = LoginCredential.query.filter_by(credential_id=credential_id).first()
    
    return jsonify({
        'authenticated': True,
        'vc_auth': True,
        'method': 'verifiable_credential',
        'user_email': current_user.name,
        'session': login_session.to_dict() if login_session else None,
        'credential': login_credential.to_dict() if login_credential else None
    }), 200

