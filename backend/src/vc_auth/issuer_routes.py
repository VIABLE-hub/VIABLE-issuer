"""
Admin routes for issuing login credentials

This module handles the issuance of LoginCredentials by administrators.
Reuses existing issuer infrastructure (BBS+, OID4VCI) to create login VCs.

Routes:
- GET /admin/vc-auth/issue - Show issuance form
- POST /admin/vc-auth/issue - Issue new login credential
- GET /admin/vc-auth/download/<credential_id> - Download credential offer
"""

from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from logging import getLogger
from . import vc_admin_bp
from .models import LoginCredential
from ..models import VC_Offer, db, AuditLog
from ..issuer.offer import get_offer_url
from ..issuer.qr_codes import generate_qr_code
from src.utils import get_current_server_url
import json
from uuid import uuid4

logger = getLogger("VC_AUTH")


@vc_admin_bp.route('/issue', methods=['GET', 'POST'])
@login_required
def issue_login_credential():
    """
    Admin interface for issuing login credentials
    
    GET: Show issuance form with user selection
    POST: Issue new login credential and generate QR code
    """
    
    # GET: Show the form
    if request.method == 'GET':
        # Get list of existing credentials for reference
        existing_creds = LoginCredential.query.filter_by(is_active=True).all()
        
        # Get available tenants (from tenant registry)
        try:
            from ..tenants.registry import get_all_tenant_ids
            available_tenants = get_all_tenant_ids()
        except:
            available_tenants = ['root', 'tuberlin', 'fuberlin']
        
        return render_template(
            'vc_auth/issue_login_credential.html',
            existing_credentials=existing_creds,
            available_tenants=available_tenants
        )
    
    # POST: Issue the credential
    try:
        # Extract form data
        user_email = request.form.get('user_email')
        user_name = request.form.get('user_name')
        user_role = request.form.get('user_role', 'user')
        primary_tenant = request.form.get('primary_tenant', 'root')
        allowed_tenants = request.form.getlist('allowed_tenants')
        expires_days = int(request.form.get('expires_days', 365))
        
        # Build permissions based on role
        permissions = build_permissions_from_role(user_role)
        
        # Create the LoginCredential record
        login_credential = LoginCredential.create(
            user_email=user_email,
            user_name=user_name,
            user_role=user_role,
            tenant_id=primary_tenant,
            issued_by=current_user.name,
            expires_days=expires_days,
            allowed_tenants=allowed_tenants if allowed_tenants else [primary_tenant],
            permissions=permissions
        )
        
        # Create the credential subject for the VC
        credential_subject = {
            "id": login_credential.subject_did,
            "email": user_email,
            "name": user_name,
            "role": user_role,
            "tenant": primary_tenant,
            "allowedTenants": login_credential.allowed_tenants,
            "permissions": permissions
        }
        
        # Create credential data (similar to student ID card)
        credential_data = {
            "type": ["VerifiableCredential", "LoginCredential"],
            "credentialSubject": credential_subject,
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1"
            ]
        }
        
        # Generate credential offer using existing infrastructure
        credential_offer_uri = get_offer_url(credential_data)
        
        # Generate QR code
        qr_code_data = generate_qr_code(credential_offer_uri)
        
        # Log the issuance
        AuditLog.log(
            tenant_id=primary_tenant,
            user_email=current_user.name,
            action='issue',
            resource_type='login_credential',
            resource_id=login_credential.credential_id,
            new_value=f"Issued login credential to {user_email}"
        )
        
        flash(f'✅ Login credential issued successfully to {user_email}!', 'success')
        
        # Return JSON response with QR code and offer URI
        return jsonify({
            'success': True,
            'credential_id': login_credential.credential_id,
            'qr_code': qr_code_data,
            'offer_uri': credential_offer_uri,
            'message': 'Login credential issued successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to issue login credential: {e}")
        flash(f'❌ Failed to issue login credential: {str(e)}', 'error')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def build_permissions_from_role(role):
    """
    Build permission dict based on user role
    
    Args:
        role: User role (admin, user, student)
    
    Returns:
        dict: Permissions dictionary
    """
    if role == 'admin':
        return {
            'issuer': ['create', 'read', 'update', 'delete'],
            'verifier': ['create', 'read', 'update', 'delete'],
            'vcstatus': ['read', 'update', 'delete'],
            'settings': ['read', 'update']
        }
    elif role == 'user':
        return {
            'issuer': ['create', 'read'],
            'verifier': ['create', 'read'],
            'vcstatus': ['read'],
            'settings': ['read']
        }
    else:  # student
        return {
            'issuer': ['read'],
            'verifier': ['read'],
            'vcstatus': ['read'],
            'settings': []
        }


@vc_admin_bp.route('/credentials', methods=['GET'])
@login_required
def list_credentials():
    """
    List all issued login credentials
    
    Returns JSON list of all credentials with their status
    """
    try:
        credentials = LoginCredential.query.all()
        return jsonify({
            'success': True,
            'credentials': [cred.to_dict() for cred in credentials]
        }), 200
    except Exception as e:
        logger.error(f"Failed to list credentials: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vc_admin_bp.route('/revoke/<credential_id>', methods=['POST'])
@login_required
def revoke_credential(credential_id):
    """
    Revoke a login credential
    
    Args:
        credential_id: ID of credential to revoke
    
    Returns:
        JSON response with revocation status
    """
    try:
        credential = LoginCredential.query.filter_by(credential_id=credential_id).first()
        
        if not credential:
            return jsonify({
                'success': False,
                'error': 'Credential not found'
            }), 404
        
        reason = request.json.get('reason', 'Revoked by administrator')
        credential.revoke(revoked_by=current_user.name, reason=reason)
        
        return jsonify({
            'success': True,
            'message': 'Credential revoked successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to revoke credential: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vc_admin_bp.route('/sessions', methods=['GET'])
@login_required
def list_sessions():
    """
    List all active login sessions
    
    Returns JSON list of active sessions
    """
    try:
        from .models import LoginSession
        sessions = LoginSession.query.filter(LoginSession.ended_at.is_(None)).all()
        
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        }), 200
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

