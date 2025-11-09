# 🎓 Modular Authentication Architecture
**Educational Guide for Students**

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Module Structure](#module-structure)
4. [Authentication Flow](#authentication-flow)
5. [Security Considerations](#security-considerations)
6. [Testing Strategy](#testing-strategy)
7. [Extension Guide](#extension-guide)
8. [Learning Objectives](#learning-objectives)

---

## 🎯 Overview

The StudentVC authentication system is designed as a **modular, extensible platform** that supports multiple authentication methods:

- ✅ **Traditional Auth:** Username/Password
- ✅ **VC Auth:** Verifiable Credentials (BBS+ Signatures)
- 🔄 **2FA:** Two-Factor Authentication (extensible)
- 🔄 **OAuth:** Social login (extensible)

### Why Modular Architecture?

**Benefits:**
- **Maintainability:** Each auth method is isolated
- **Testability:** Modules can be tested independently
- **Extensibility:** New auth methods can be added easily
- **Security:** Clear separation of concerns
- **Educational:** Students learn design patterns

---

## 🏗️ Architecture Principles

### 1. Single Responsibility Principle (SRP)

Each module has ONE clear responsibility:

```
/auth/
├── __init__.py           # Module initialization
├── traditional_auth.py   # ONLY username/password
├── vc_auth.py           # ONLY verifiable credentials
└── two_factor.py        # ONLY 2FA (future)
```

**Why?** Changes to VC auth don't affect traditional auth.

### 2. Dependency Inversion

High-level modules don't depend on low-level modules. Both depend on abstractions:

```python
# Abstract interface (high-level)
class AuthenticationMethod(ABC):
    @abstractmethod
    def authenticate(self, credentials: Dict) -> Optional[User]:
        pass

# Concrete implementations (low-level)
class TraditionalAuth(AuthenticationMethod):
    def authenticate(self, credentials: Dict) -> Optional[User]:
        # Implementation details
        pass

class VCAuth(AuthenticationMethod):
    def authenticate(self, credentials: Dict) -> Optional[User]:
        # Implementation details
        pass
```

**Why?** Easy to swap implementations without breaking code.

### 3. Open/Closed Principle

Modules are **open for extension, closed for modification**:

```python
# Adding new auth method doesn't require modifying existing code
class BiometricAuth(AuthenticationMethod):
    def authenticate(self, credentials: Dict) -> Optional[User]:
        # New implementation
        pass
```

### 4. Interface Segregation

Don't force modules to implement unused methods:

```python
# Good: Specific interfaces
class PasswordAuth:
    def verify_password(self, user, password): pass

class VCAuth:
    def verify_credential(self, vp_token): pass

# Bad: One bloated interface
class Auth:
    def verify_password(self, user, password): pass  # VC doesn't need this!
    def verify_credential(self, vp_token): pass      # Password doesn't need this!
```

---

## 📁 Module Structure

### Directory Layout

```
backend/src/auth/
├── __init__.py              # Module exports and initialization
├── traditional_auth.py      # Username/Password authentication
├── vc_auth.py              # Verifiable Credential authentication
├── interfaces.py           # Abstract base classes (future)
├── utils.py                # Shared utilities (future)
└── tests/                  # Unit tests
    ├── test_traditional.py
    ├── test_vc_auth.py
    └── test_integration.py
```

### Module Dependencies

```
                      ┌─────────────┐
                      │   Flask     │
                      │  App Core   │
                      └──────┬──────┘
                             │
                ┌────────────┴────────────┐
                │                         │
         ┌──────▼──────┐           ┌─────▼──────┐
         │ Traditional │           │  VC Auth   │
         │    Auth     │           │  Blueprint │
         └──────┬──────┘           └─────┬──────┘
                │                         │
                └────────────┬────────────┘
                             │
                      ┌──────▼──────┐
                      │   Models    │
                      │  (User DB)  │
                      └─────────────┘
```

---

## 🔐 Authentication Flow

### Traditional Auth Flow

```
1. User visits /login
   ↓
2. GET /login → render login_vc.html
   ↓
3. User enters username + password
   ↓
4. POST /login
   ↓
5. Validate CSRF token
   ↓
6. Query User.query.filter_by(name=username)
   ↓
7. Verify: check_password_hash(user.password_hash, password)
   ↓
8. If valid: login_user(user, remember=True)
   ↓
9. Redirect to home or next URL
```

**Code Location:** `backend/src/auth/traditional_auth.py`

**Key Functions:**
- `@auth.route('/login')` - Main login handler
- `login_error_handler()` - Error display
- `check_password_hash()` - Security module

### VC Auth Flow

```
1. User clicks "Login with VC" tab
   ↓
2. JavaScript calls POST /auth/vc-login/request
   ↓
3. Backend creates VCSession with unique session_id
   ↓
4. Generate presentation request URL
   ↓
5. Return QR code data to frontend
   ↓
6. QRCode.js renders QR code
   ↓
7. User scans with StudentVC Wallet app
   ↓
8. Wallet sends VP to POST /auth/vc-login/callback
   ↓
9. Backend decodes JWT token (vp_token)
   ↓
10. Verify BBS+ signatures using safe_verify_presentation()
    ↓
11. Extract user info from VC values
    ↓
12. Create/authenticate user in database
    ↓
13. Emit Socket.IO event: vc_login_{session_id}
    ↓
14. Frontend receives event → redirect to home
```

**Code Location:** `backend/src/auth/vc_auth.py`

**Key Functions:**
- `create_vc_login_request()` - Generate QR code
- `handle_vc_callback()` - Verify VP token
- `extract_user_info_from_vc()` - Parse credential
- `authenticate_with_vc()` - User creation/login

### Sequence Diagram

```
┌──────┐     ┌─────────┐     ┌────────┐     ┌────────┐
│Client│     │ Backend │     │Verifier│     │ Wallet │
└──┬───┘     └────┬────┘     └───┬────┘     └───┬────┘
   │              │               │              │
   │ GET /login   │               │              │
   ├─────────────>│               │              │
   │              │               │              │
   │ login_vc.html│               │              │
   │<─────────────┤               │              │
   │              │               │              │
   │ Switch to VC │               │              │
   │ tab          │               │              │
   ├──────┐       │               │              │
   │      │       │               │              │
   │<─────┘       │               │              │
   │              │               │              │
   │POST vc/request               │              │
   ├─────────────>│               │              │
   │              │               │              │
   │  QR code URL │               │              │
   │<─────────────┤               │              │
   │              │               │              │
   │              │               │ Scan QR      │
   │              │               │<─────────────┤
   │              │               │              │
   │              │               │GET request   │
   │              │               │<─────────────┤
   │              │               │              │
   │              │               │VP definition │
   │              │               ├─────────────>│
   │              │               │              │
   │              │               │   Build VP   │
   │              │               │   + Sign     │
   │              │               │<──────┐      │
   │              │               │       │      │
   │              │               │<──────┘      │
   │              │               │              │
   │              │POST vc/callback (vp_token)   │
   │              │<──────────────┼──────────────┤
   │              │               │              │
   │  Decode JWT  │               │              │
   │  Verify BBS+ │               │              │
   │<─────┐       │               │              │
   │      │       │               │              │
   │<─────┘       │               │              │
   │              │               │              │
   │Socket.IO:    │               │              │
   │ verified     │               │              │
   │<─────────────┤               │              │
   │              │               │              │
   │ Redirect home│               │              │
   │──────┐       │               │              │
   │      │       │               │              │
   │<─────┘       │               │              │
```

---

## 🔒 Security Considerations

### 1. Password Security

**Hashing Algorithm:** Werkzeug's `generate_password_hash()`
- Uses **PBKDF2** with SHA-256
- Automatic salt generation
- Configurable iterations

```python
from werkzeug.security import generate_password_hash, check_password_hash

# On registration
password_hash = generate_password_hash('user_password')
# Generates: pbkdf2:sha256:260000$salt$hash

# On login
is_valid = check_password_hash(stored_hash, input_password)
```

**Why PBKDF2?**
- Slow by design (prevents brute force)
- Industry standard (NIST approved)
- Built into Python (no external dependencies)

### 2. CSRF Protection

Every form includes a CSRF token:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token }}">
```

**Validation:**
```python
csrf_token = request.form.get('csrf_token')
if csrf_token != session.get('csrf_token'):
    return error("Invalid CSRF token")
```

**Why?** Prevents Cross-Site Request Forgery attacks.

### 3. Session Security

```python
login_user(user, remember=True, duration=timedelta(hours=1))
```

**Features:**
- Server-side sessions (Flask-Login)
- Secure cookies (HTTPS only in production)
- Automatic timeout (1 hour)
- Remember me functionality

### 4. BBS+ Signature Verification

**Zero-Knowledge Proofs:**
- User proves credential ownership
- WITHOUT revealing all data
- Selective disclosure supported

```python
# Verify without seeing all fields
valid, details = safe_verify_presentation(decoded_vp, presentation_def)
```

**Security Properties:**
- **Unforgeable:** Only issuer can create valid signatures
- **Selective Disclosure:** Reveal only required fields
- **Unlinkable:** Different presentations aren't correlatable

### 5. Input Validation

**Always validate user input:**

```python
# Bad
username = request.form.get('username')
User.query.filter_by(name=username).first()  # SQL injection risk!

# Good
username = request.form.get('username')
if not username or len(username) > 150:
    return error("Invalid username")
User.query.filter_by(name=username).first()  # Parameterized query
```

### 6. Error Messages

**Don't leak information:**

```python
# Bad
if not user:
    return "User doesn't exist"  # Helps attackers enumerate users!
if not check_password_hash(...):
    return "Wrong password"       # Confirms username exists!

# Good
if not user or not check_password_hash(...):
    return "Invalid credentials"  # Ambiguous message
```

---

## 🧪 Testing Strategy

### Test Pyramid

```
           /\
          /  \
         / E2E\     End-to-End (10%)
        /______\
       /        \
      /Integration\ Integration (30%)
     /____________\
    /              \
   /  Unit Tests    \  Unit Tests (60%)
  /__________________\
```

### Unit Tests

**Test individual functions:**

```python
# tests/test_traditional_auth.py
def test_password_hashing():
    """Test that passwords are hashed correctly"""
    password = "test_password_123"
    hashed = generate_password_hash(password)
    
    assert hashed != password  # Never store plaintext!
    assert check_password_hash(hashed, password)  # Can verify
    assert not check_password_hash(hashed, "wrong")  # Rejects wrong password

def test_csrf_validation():
    """Test CSRF token validation"""
    with app.test_client() as client:
        # Get login page (generates CSRF token)
        rv = client.get('/login')
        
        # Try to login without CSRF token
        rv = client.post('/login', data={
            'username': 'test',
            'password': 'test'
        })
        assert rv.status_code == 400  # Should reject
```

### Integration Tests

**Test module interactions:**

```python
# tests/test_integration.py
def test_full_login_flow():
    """Test complete login process"""
    with app.test_client() as client:
        # Create test user
        user = create_test_user('testuser', 'testpass')
        
        # Get login page
        rv = client.get('/login')
        assert rv.status_code == 200
        
        # Extract CSRF token
        csrf_token = extract_csrf(rv.data)
        
        # Login
        rv = client.post('/login', data={
            'name': 'testuser',
            'password': 'testpass',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        # Should be logged in
        assert b'Welcome' in rv.data
        assert session['user_id'] == user.id
```

### E2E Tests

**Test with real browser:**

```python
# tests/test_e2e.py (using Selenium)
def test_vc_login_with_wallet():
    """Test VC login with mobile wallet"""
    driver = webdriver.Chrome()
    driver.get('https://localhost:8080/login')
    
    # Click VC tab
    vc_tab = driver.find_element_by_id('tab-vc')
    vc_tab.click()
    
    # QR code should appear
    qr_code = driver.find_element_by_id('qr-code')
    assert qr_code.is_displayed()
    
    # Simulate wallet scan (mock)
    mock_wallet_presentation(driver)
    
    # Should redirect to home
    WebDriverWait(driver, 10).until(
        EC.url_contains('/home')
    )
    
    driver.quit()
```

---

## 🔧 Extension Guide

### Adding a New Auth Method

**Example: Biometric Authentication**

**Step 1: Create Module**

```python
# backend/src/auth/biometric_auth.py
"""
Biometric Authentication Module

Supports fingerprint and face recognition authentication.
"""

from flask import Blueprint, request, jsonify
from ..models import User, db
import logging

logger = logging.getLogger(__name__)

biometric_auth_bp = Blueprint('biometric_auth', __name__, 
                               url_prefix='/auth/biometric')

@biometric_auth_bp.route('/enroll', methods=['POST'])
def enroll_biometric():
    """
    Enroll user's biometric data
    
    Expected payload:
        {
            "user_id": 123,
            "biometric_type": "fingerprint",
            "biometric_data": "base64_encoded_data"
        }
    """
    data = request.get_json()
    
    # Validate input
    if not all(k in data for k in ['user_id', 'biometric_type', 'biometric_data']):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Store biometric template (hashed, not raw!)
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Hash the biometric template
    template_hash = hash_biometric_template(data['biometric_data'])
    
    # Store in database (extend User model)
    user.biometric_hash = template_hash
    user.biometric_type = data['biometric_type']
    db.session.commit()
    
    logger.info(f"✅ Enrolled biometric for user: {user.name}")
    
    return jsonify({"message": "Biometric enrolled successfully"})

@biometric_auth_bp.route('/authenticate', methods=['POST'])
def authenticate_biometric():
    """
    Authenticate user with biometric
    """
    data = request.get_json()
    
    # Extract biometric sample
    biometric_data = data.get('biometric_data')
    
    # Find matching user
    user = find_user_by_biometric(biometric_data)
    
    if user:
        login_user(user, remember=True)
        return jsonify({"success": True, "redirect": url_for('home.index')})
    
    return jsonify({"error": "Authentication failed"}), 401

def hash_biometric_template(biometric_data):
    """Convert biometric data to searchable hash"""
    # Use locality-sensitive hashing for biometrics
    # (allows fuzzy matching while maintaining security)
    pass

def find_user_by_biometric(biometric_data):
    """Find user by matching biometric template"""
    # Compare against stored hashes
    # Allow for slight variations (fingers/face change)
    pass
```

**Step 2: Register Blueprint**

```python
# backend/src/auth/__init__.py
from .biometric_auth import biometric_auth_bp

__all__ = ['auth', 'vc_auth_bp', 'biometric_auth_bp']
```

```python
# backend/src/__init__.py
from .auth import auth, vc_auth_bp, biometric_auth_bp

app.register_blueprint(biometric_auth_bp)
```

**Step 3: Add UI**

```html
<!-- In login_vc.html -->
<button id="tab-biometric" onclick="switchTab('biometric')">
  <i class="fas fa-fingerprint mr-2"></i>
  Biometric Login
</button>

<div id="form-biometric" class="hidden">
  <button onclick="captureFingerprint()">
    <i class="fas fa-fingerprint"></i>
    Touch Sensor
  </button>
</div>
```

**Step 4: Add Tests**

```python
# tests/test_biometric_auth.py
def test_biometric_enrollment():
    """Test biometric enrollment process"""
    # Create test user
    user = create_test_user('bio_user', 'password')
    
    # Enroll fingerprint
    rv = client.post('/auth/biometric/enroll', json={
        'user_id': user.id,
        'biometric_type': 'fingerprint',
        'biometric_data': generate_test_fingerprint()
    })
    
    assert rv.status_code == 200
    assert user.biometric_hash is not None

def test_biometric_authentication():
    """Test biometric authentication"""
    # Enroll user
    user = enroll_biometric_user()
    
    # Authenticate
    rv = client.post('/auth/biometric/authenticate', json={
        'biometric_data': user.test_fingerprint
    })
    
    assert rv.status_code == 200
    assert session['user_id'] == user.id
```

---

## 🎓 Learning Objectives

### For Students

After studying this authentication system, you should understand:

**1. Software Architecture**
- ✅ Modular design principles
- ✅ Separation of concerns
- ✅ SOLID principles
- ✅ Design patterns (Strategy, Factory)

**2. Web Security**
- ✅ Password hashing and salting
- ✅ CSRF protection
- ✅ Session management
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ XSS prevention

**3. Authentication Protocols**
- ✅ Traditional username/password
- ✅ OAuth 2.0 / OpenID Connect
- ✅ Verifiable Credentials (W3C standard)
- ✅ BBS+ signatures

**4. Testing**
- ✅ Unit testing
- ✅ Integration testing
- ✅ End-to-end testing
- ✅ Test-driven development (TDD)

**5. Python & Flask**
- ✅ Flask blueprints
- ✅ Flask-Login
- ✅ SQLAlchemy ORM
- ✅ Socket.IO
- ✅ Type hints
- ✅ Documentation

### Exercises

**Exercise 1: Add Rate Limiting**
```python
# Prevent brute force attacks
# Limit to 5 login attempts per minute per IP

from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@auth.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Your code here
    pass
```

**Exercise 2: Implement Password Reset**
```python
# Add email-based password reset
# 1. Generate secure token
# 2. Send email with reset link
# 3. Validate token
# 4. Allow password change
```

**Exercise 3: Add Login History**
```python
# Track login attempts
class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    success = db.Column(db.Boolean)
    method = db.Column(db.String(50))  # 'password', 'vc', 'biometric'
```

**Exercise 4: Multi-Factor Authentication**
```python
# Require both password AND VC
# 1. User enters password (factor 1)
# 2. System requests VC (factor 2)
# 3. Both must succeed for login
```

---

## 📚 Further Reading

### Books
- "Authentication and Authorization" by Eric Richards
- "OAuth 2.0 Simplified" by Aaron Parecki
- "Clean Architecture" by Robert C. Martin
- "Test-Driven Development" by Kent Beck

### Standards
- [W3C Verifiable Credentials](https://www.w3.org/TR/vc-data-model/)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/)

### Security
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [BBS+ Signatures](https://identity.foundation/bbs-signature/draft-bbs-signatures.html)

### Python & Flask
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## ✅ Summary

You now have:
- ✅ Modular authentication architecture
- ✅ Support for multiple auth methods
- ✅ Security best practices
- ✅ Comprehensive testing
- ✅ Extension framework
- ✅ Educational documentation

**Next Steps:**
1. Implement exercises
2. Add more auth methods
3. Improve security
4. Write more tests
5. Deploy to production

---

**Author:** StudentVC Team  
**Version:** 2.0.0  
**Last Updated:** November 2025  
**License:** MIT (Educational Use)


