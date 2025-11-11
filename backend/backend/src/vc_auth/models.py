"""
Database models for VC-based authentication

Models:
- LoginCredential: Verifiable Credentials issued for login purposes
- LoginSession: Active login sessions from VC authentication
"""

from .. import db
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import relationship
import datetime
import logging

logger = logging.getLogger(__name__)


class LoginCredential(db.Model):
    """
    Login credentials issued to users for VC-based authentication.
    
    This model stores metadata about issued login VCs. The actual VC is
    stored in the user's wallet, and this record is used for validation.
    
    Usage:
        # Create new login credential
        cred = LoginCredential.create(
            user_email='student@example.com',
            user_name='Max Mustermann',
            user_role='admin',
            tenant_id='tuberlin',
            issued_by='admin@example.com'
        )
        
        # Check if valid
        if cred.is_valid():
            print("Credential is active")
    """
    __tablename__ = 'login_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Credential identification
    credential_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    subject_did = db.Column(db.String(512), nullable=False, index=True)
    
    # User information
    user_email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    user_name = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.String(50), nullable=False, default='user')  # 'admin', 'user', 'student'
    
    # Tenant isolation and access control
    tenant_id = db.Column(db.String(255), nullable=False, index=True)
    allowed_tenants = db.Column(JSON, nullable=False, default=list)  # List of accessible tenants
    
    # Permissions and scopes (module-level access control)
    permissions = db.Column(JSON, nullable=False, default=dict)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Lifecycle timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    issued_by = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # Revocation fields
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)
    revoked_by = db.Column(db.String(255), nullable=True)
    revocation_reason = db.Column(db.String(255), nullable=True)
    
    # Link to User model for hybrid auth (optional)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)
    user = relationship("User", backref="login_credentials")
    
    def __repr__(self):
        return f'<LoginCredential {self.user_email} tenant={self.tenant_id} active={self.is_active}>'
    
    @classmethod
    def create(cls, user_email, user_name, user_role, tenant_id, issued_by, 
               credential_id=None, subject_did=None, expires_days=365, 
               allowed_tenants=None, permissions=None):
        """
        Create a new login credential
        
        Args:
            user_email: User's email address
            user_name: User's full name
            user_role: Role (admin, user, student)
            tenant_id: Primary tenant ID
            issued_by: Email of issuing admin
            credential_id: Optional credential ID (generated if not provided)
            subject_did: Optional DID (generated if not provided)
            expires_days: Days until expiration (default 365)
            allowed_tenants: List of accessible tenants (default: [tenant_id])
            permissions: Dict of module permissions (default: read-only)
        
        Returns:
            LoginCredential: The created credential
        """
        import uuid
        
        # Generate IDs if not provided
        if not credential_id:
            credential_id = f"urn:uuid:{uuid.uuid4()}"
        if not subject_did:
            subject_did = f"did:key:{uuid.uuid4().hex[:32]}"
        
        # Default allowed tenants to primary tenant
        if allowed_tenants is None:
            allowed_tenants = [tenant_id]
        
        # Default permissions (read-only access)
        if permissions is None:
            permissions = {
                'issuer': ['read'],
                'verifier': ['read'],
                'vcstatus': ['read'],
                'settings': ['read']
            }
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = datetime.datetime.now() + datetime.timedelta(days=expires_days)
        
        # Create the credential
        credential = cls(
            credential_id=credential_id,
            subject_did=subject_did,
            user_email=user_email,
            user_name=user_name,
            user_role=user_role,
            tenant_id=tenant_id,
            allowed_tenants=allowed_tenants,
            permissions=permissions,
            issued_by=issued_by,
            expires_at=expires_at,
            is_active=True
        )
        
        db.session.add(credential)
        db.session.commit()
        
        logger.info(f"✅ Created login credential for {user_email} (tenant: {tenant_id})")
        return credential
    
    def is_valid(self):
        """
        Check if credential is currently valid
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not self.is_active:
            logger.debug(f"Credential {self.credential_id} is not active")
            return False
        
        if self.revoked_at:
            logger.debug(f"Credential {self.credential_id} is revoked")
            return False
        
        if self.expires_at and self.expires_at < datetime.datetime.now():
            logger.debug(f"Credential {self.credential_id} is expired")
            return False
        
        return True
    
    def revoke(self, revoked_by, reason=None):
        """
        Revoke this login credential
        
        Args:
            revoked_by: Email of person revoking the credential
            reason: Optional reason for revocation
        """
        self.is_active = False
        self.revoked_at = func.now()
        self.revoked_by = revoked_by
        self.revocation_reason = reason
        
        # Log the revocation
        from ..models import AuditLog
        AuditLog.log(
            tenant_id=self.tenant_id,
            user_email=revoked_by,
            action='revoke',
            resource_type='login_credential',
            resource_id=self.credential_id,
            new_value=f"Revoked login credential for {self.user_email}: {reason}"
        )
        
        db.session.commit()
        logger.info(f"🚫 Revoked login credential {self.credential_id}: {reason}")
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = func.now()
        db.session.commit()
    
    def has_permission(self, module, action):
        """
        Check if credential has permission for a specific action
        
        Args:
            module: Module name ('issuer', 'verifier', etc.)
            action: Action ('read', 'create', 'update', 'delete')
        
        Returns:
            bool: True if permitted, False otherwise
        """
        if not self.permissions:
            return False
        
        module_perms = self.permissions.get(module, [])
        return action in module_perms or 'admin' in module_perms
    
    def can_access_tenant(self, tenant_id):
        """
        Check if credential can access a specific tenant
        
        Args:
            tenant_id: Tenant ID to check
        
        Returns:
            bool: True if access allowed, False otherwise
        """
        return tenant_id in self.allowed_tenants
    
    def to_dict(self):
        """
        Convert to dictionary for API responses
        
        Returns:
            dict: Credential information (safe for API)
        """
        return {
            'credential_id': self.credential_id,
            'user_email': self.user_email,
            'user_name': self.user_name,
            'user_role': self.user_role,
            'tenant_id': self.tenant_id,
            'allowed_tenants': self.allowed_tenants,
            'permissions': self.permissions,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None,
            'revoked_by': self.revoked_by,
            'revocation_reason': self.revocation_reason
        }


class LoginSession(db.Model):
    """
    Active login sessions from VC authentication.
    
    Tracks active sessions for security and audit purposes.
    Each VC login creates a new session record.
    
    Usage:
        # Create session
        session = LoginSession.create(
            credential=login_credential,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # Check if session is valid
        if session.is_valid():
            print("Session is active")
    """
    __tablename__ = 'login_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    credential_id = db.Column(db.String(255), ForeignKey('login_credentials.credential_id'))
    
    # Session metadata
    user_email = db.Column(db.String(255), nullable=False, index=True)
    tenant_id = db.Column(db.String(255), nullable=False, index=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Lifecycle
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    last_activity = db.Column(db.DateTime(timezone=True), default=func.now())
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # Relationships
    credential = relationship("LoginCredential", backref="sessions")
    
    def __repr__(self):
        return f'<LoginSession {self.session_id} user={self.user_email} tenant={self.tenant_id}>'
    
    @classmethod
    def create(cls, credential, session_id=None, ip_address=None, user_agent=None, duration_hours=8):
        """
        Create a new login session
        
        Args:
            credential: LoginCredential instance
            session_id: Optional session ID (generated if not provided)
            ip_address: Client IP address
            user_agent: Client user agent string
            duration_hours: Session duration in hours (default 8)
        
        Returns:
            LoginSession: The created session
        """
        import uuid
        
        # Generate session ID if not provided
        if not session_id:
            session_id = uuid.uuid4().hex
        
        # Calculate expiration
        expires_at = datetime.datetime.now() + datetime.timedelta(hours=duration_hours)
        
        # Create session
        session = cls(
            session_id=session_id,
            credential_id=credential.credential_id,
            user_email=credential.user_email,
            tenant_id=credential.tenant_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        db.session.add(session)
        db.session.commit()
        
        logger.info(f"✅ Created login session {session_id} for {credential.user_email}")
        return session
    
    def is_valid(self):
        """
        Check if session is currently valid
        
        Returns:
            bool: True if valid, False otherwise
        """
        if self.ended_at:
            logger.debug(f"Session {self.session_id} has ended")
            return False
        
        if self.expires_at < datetime.datetime.now():
            logger.debug(f"Session {self.session_id} has expired")
            return False
        
        return True
    
    def update_activity(self):
        """Update last activity timestamp (keep session alive)"""
        self.last_activity = func.now()
        db.session.commit()
    
    def end_session(self):
        """End this session (logout)"""
        self.ended_at = func.now()
        db.session.commit()
        logger.info(f"🚪 Ended session {self.session_id}")
    
    def to_dict(self):
        """
        Convert to dictionary for API responses
        
        Returns:
            dict: Session information
        """
        return {
            'session_id': self.session_id,
            'user_email': self.user_email,
            'tenant_id': self.tenant_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'is_valid': self.is_valid()
        }

