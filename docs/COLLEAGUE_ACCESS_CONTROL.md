# Colleague Access Control for StudentVC

## Option 1: Basic Authentication (Quick & Simple)

### Setup Basic Auth with NGINX

1. **Create password file with colleague emails as usernames:**
```bash
# Install apache2-utils for htpasswd
sudo apt-get install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd john.doe@university.edu
sudo htpasswd /etc/nginx/.htpasswd jane.smith@university.edu
sudo htpasswd /etc/nginx/.htpasswd colleague3@university.edu
```

2. **Update NGINX configuration:**
```nginx
server {
    listen 443 ssl;
    server_name studentvc.yourdomain.com;
    
    # Basic authentication
    auth_basic "StudentVC - Authorized Personnel Only";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    # Optional: Whitelist specific paths
    location /public {
        auth_basic off;  # No auth for public endpoints
    }
    
    location / {
        proxy_pass https://localhost:8082;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Option 2: Cloudflare Access (Recommended for Production)

### Free email-based access control

1. **Setup Cloudflare Access:**
```bash
# Add your domain to Cloudflare (free plan)
# Go to Zero Trust → Access → Applications
```

2. **Create Access Policy:**
```yaml
Application name: StudentVC
Session duration: 24 hours

Policy Rules:
- Name: Allowed Colleagues
- Action: Allow
- Include:
  - Emails: 
    - john.doe@university.edu
    - jane.smith@university.edu
    - colleague3@university.edu
```

3. **Benefits:**
- No passwords to manage
- Email verification via one-time PIN
- Works with any email provider
- Session management included
- Audit logs

## Option 3: Flask-Login with Email Whitelist

### Add authentication to the application

1. **Create login blueprint:**
```python
# backend/src/auth/colleague_auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# Whitelist of allowed emails
ALLOWED_COLLEAGUES = {
    'john.doe@university.edu',
    'jane.smith@university.edu',
    'colleague3@university.edu'
}

# Temporary tokens storage (use Redis in production)
login_tokens = {}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        
        if email not in ALLOWED_COLLEAGUES:
            flash('Access denied. Contact administrator.')
            return redirect(url_for('auth.login'))
        
        # Generate login token
        token = secrets.token_urlsafe(32)
        login_tokens[token] = {
            'email': email,
            'expires': datetime.now() + timedelta(minutes=30)
        }
        
        # Send email with login link
        send_login_email(email, token)
        flash('Check your email for login link')
        return redirect(url_for('auth.login'))
    
    return render_template('login.html')

@auth_bp.route('/verify/<token>')
def verify_token(token):
    if token in login_tokens:
        token_data = login_tokens[token]
        if datetime.now() < token_data['expires']:
            # Create user session
            login_user(User(token_data['email']))
            del login_tokens[token]
            return redirect(url_for('home'))
    
    flash('Invalid or expired link')
    return redirect(url_for('auth.login'))
```

2. **Protect routes:**
```python
# backend/src/issuer/issuer.py
from flask_login import login_required

@issuer_bp.route('/')
@login_required
def index():
    # Existing issuer code
```

## Option 4: OAuth with Google Workspace

### If colleagues use Google/Microsoft work emails

1. **Install dependencies:**
```bash
pip install authlib
```

2. **Configure OAuth:**
```python
# backend/src/auth/oauth_config.py
from authlib.integrations.flask_client import OAuth

oauth = OAuth()

google = oauth.register(
    name='google',
    client_id='your-client-id',
    client_secret='your-client-secret',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    client_kwargs={'scope': 'openid email profile'},
)

@auth_bp.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback/google')
def google_callback():
    token = google.authorize_access_token()
    user_info = token['userinfo']
    
    if user_info['email'] not in ALLOWED_COLLEAGUES:
        flash('Access denied')
        return redirect(url_for('auth.login'))
    
    # Create session
    login_user(User(user_info['email']))
    return redirect(url_for('home'))
```

## Option 5: Simple IP + Email Whitelist

### Combine IP restrictions with email verification

1. **NGINX IP whitelist:**
```nginx
# Allow university network and specific IPs
geo $allowed_ip {
    default 0;
    10.0.0.0/8 1;          # University network
    192.168.1.100 1;       # Colleague home IP
    203.0.113.0/24 1;      # Office network
}

server {
    if ($allowed_ip = 0) {
        return 403;
    }
    
    # Rest of config
}
```

2. **Add email verification on first access**

## Option 6: VPN + Basic Auth

### Most secure for sensitive environments

1. **Setup WireGuard VPN:**
```bash
# Install WireGuard
sudo apt-get install wireguard

# Generate configs for each colleague
wg genkey | tee colleague1.key | wg pubkey > colleague1.pub
```

2. **Configure VPN access per colleague:**
```ini
# /etc/wireguard/wg0.conf
[Interface]
Address = 10.0.0.1/24
PrivateKey = <server-private-key>
ListenPort = 51820

# John Doe
[Peer]
PublicKey = <colleague1-public-key>
AllowedIPs = 10.0.0.2/32

# Jane Smith
[Peer]
PublicKey = <colleague2-public-key>
AllowedIPs = 10.0.0.3/32
```

## Implementation Examples

### Quick Setup Script
```bash
#!/bin/bash
# setup-colleague-access.sh

echo "Setting up colleague access control..."

# Option 1: Basic Auth
read -p "Enter colleague email: " email
read -s -p "Enter password: " password
echo
sudo htpasswd -b /etc/nginx/.htpasswd "$email" "$password"

# Option 2: Email whitelist in app
cat >> backend/src/config.py << EOF
ALLOWED_COLLEAGUES = [
    'john.doe@university.edu',
    'jane.smith@university.edu',
    'colleague3@university.edu'
]
EOF

echo "Access control configured!"
```

### Docker Compose with Auth
```yaml
# deployment/docker-compose.yml
services:
  nginx-auth:
    image: nginx:alpine
    volumes:
      - ./nginx-auth.conf:/etc/nginx/nginx.conf
      - ./htpasswd:/etc/nginx/.htpasswd
    ports:
      - "443:443"
    depends_on:
      - studentvc-tub
      - studentvc-fub
      - studentvc-root
```

## Email Notification Template

```python
def send_access_granted_email(email, tenant):
    """Send access credentials to colleague"""
    subject = "StudentVC Access Granted"
    body = f"""
    Hello,
    
    You have been granted access to StudentVC {tenant} tenant.
    
    Access URL: https://studentvc.yourdomain.com/{tenant}
    Username: {email}
    Password: [sent separately]
    
    This access is restricted and monitored.
    
    Best regards,
    StudentVC Admin
    """
    # Send email
```

## Monitoring Access

### Audit logging
```python
# backend/src/auth/audit.py
def log_access(email, tenant, action):
    """Log colleague access for audit trail"""
    with open('access.log', 'a') as f:
        f.write(f"{datetime.now()},{email},{tenant},{action}\n")
```

### Access dashboard
```python
@admin_bp.route('/access-control')
@admin_required
def access_control():
    """Show who has access and recent activity"""
    return render_template('access_control.html',
        allowed_users=ALLOWED_COLLEAGUES,
        recent_logins=get_recent_logins()
    )
```

## Best Practices

1. **Use HTTPS always** - Never send credentials over HTTP
2. **Rotate credentials** - Change passwords periodically
3. **Monitor access** - Log all authentication attempts
4. **Limit session duration** - Auto-logout after inactivity
5. **Use 2FA if possible** - Add TOTP for sensitive data
6. **Regular audits** - Review access list monthly

## Quick Decision Guide

| Method | Setup Time | Security | User Experience | Best For |
|--------|------------|----------|-----------------|----------|
| Basic Auth | 5 min | Low | Password prompt | Quick demos |
| Cloudflare Access | 30 min | High | Email PIN | Production |
| Flask-Login | 2 hours | Medium | Email links | Custom needs |
| OAuth | 1 day | High | Single sign-on | Corporate env |
| VPN | 1 day | Highest | VPN client | Sensitive data |

## Emergency Access Revocation

```bash
# Remove Basic Auth user
sudo htpasswd -D /etc/nginx/.htpasswd colleague@university.edu

# Block IP immediately
sudo iptables -A INPUT -s 192.168.1.100 -j DROP

# Revoke all sessions
redis-cli FLUSHDB
``` 