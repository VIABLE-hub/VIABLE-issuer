"""
Simple Authentication for StudentVC
Just password protection - no complex stuff!
"""

import os
import smtplib
import secrets
import time
from email.mime.text import MIMEText
from functools import wraps
from flask import session, request, redirect, url_for, render_template, flash, jsonify
import logging

logger = logging.getLogger(__name__)

class SimpleAuth:
    def __init__(self):
        # Get credentials from environment
        self.access_password = os.environ.get('ACCESS_PASSWORD', 'studentvc2024')
        self.require_email = os.environ.get('REQUIRE_EMAIL_2FA', 'false').lower() == 'true'
        self.admin_email = os.environ.get('ADMIN_EMAIL', '')
        
        # Email settings (optional)
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_email = os.environ.get('SMTP_EMAIL', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        
    def is_authenticated(self):
        """Check if user is authenticated"""
        return session.get('authenticated', False)
    
    def login_required(self, f):
        """Decorator to require login"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_authenticated():
                # Save the original URL to redirect back after login
                session['next_url'] = request.url
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def check_password(self, password):
        """Check if password is correct"""
        return password == self.access_password
    
    def send_verification_email(self, code):
        """Send verification code via email (optional)"""
        if not self.admin_email or not self.smtp_email:
            return False
            
        try:
            msg = MIMEText(f"""
StudentVC Access Code: {code}

This code will expire in 10 minutes.
If you didn't request this, please ignore this email.
            """)
            msg['Subject'] = 'StudentVC Access Code'
            msg['From'] = self.smtp_email
            msg['To'] = self.admin_email
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def authenticate_user(self, password, email_code=None):
        """Authenticate user with password and optional email"""
        # Check password first
        if not self.check_password(password):
            return False, "Invalid password"
        
        # If email 2FA is required
        if self.require_email:
            if not email_code:
                # Generate and send code
                code = str(secrets.randbelow(900000) + 100000)  # 6-digit code
                session['email_code'] = code
                session['code_expires'] = time.time() + 600  # 10 minutes
                
                if self.send_verification_email(code):
                    return False, "verification_code_sent"
                else:
                    return False, "Failed to send verification email"
            else:
                # Verify code
                stored_code = session.get('email_code')
                code_expires = session.get('code_expires', 0)
                
                if not stored_code or time.time() > code_expires:
                    return False, "Verification code expired"
                
                if email_code != stored_code:
                    return False, "Invalid verification code"
                
                # Clear the code after successful verification
                session.pop('email_code', None)
                session.pop('code_expires', None)
        
        # Authentication successful
        session['authenticated'] = True
        session.permanent = True  # Keep login for 31 days
        
        return True, "success"

# Global auth instance
auth = SimpleAuth()

def init_auth_routes(app):
    """Initialize authentication routes"""
    from flask import Blueprint
    
    auth_bp = Blueprint('auth', __name__)
    
    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html', require_email=auth.require_email)
        
        # Handle POST
        password = request.form.get('password', '')
        email_code = request.form.get('email_code', '')
        
        success, message = auth.authenticate_user(password, email_code)
        
        if success:
            flash('Login successful!', 'success')
            next_url = session.pop('next_url', url_for('home.index'))
            return redirect(next_url)
        elif message == "verification_code_sent":
            flash('Verification code sent to your email!', 'info')
            return render_template('login.html', require_email=True, show_email_code=True)
        else:
            flash(message, 'error')
            return render_template('login.html', require_email=auth.require_email)
    
    @auth_bp.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully!', 'success')
        return redirect(url_for('auth.login'))
    
    app.register_blueprint(auth_bp)
    
    # Apply login_required to all routes except auth routes
    @app.before_request
    def require_login():
        # Skip auth for static files and auth routes
        if (request.endpoint and 
            (request.endpoint.startswith('static') or 
             request.endpoint.startswith('auth.') or
             request.endpoint == 'health')):
            return
        
        if not auth.is_authenticated():
            session['next_url'] = request.url
            return redirect(url_for('auth.login')) 