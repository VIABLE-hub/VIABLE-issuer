# 🌍 StudentVC Environment Configuration Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Environment Files](#environment-files)
- [Required Variables](#required-variables)
- [Configuration by Scenario](#configuration-by-scenario)
- [Environment Check Tool](#environment-check-tool)
- [Common Issues](#common-issues)

---

## Overview

StudentVC uses environment variables for configuration across different deployment scenarios. This guide explains all environment files, required variables, and how to configure them properly.

### 🎯 Key Principles

1. **`.env` file is NEVER committed** - It's in `.gitignore` and `.cursorignore` for security
2. **Templates are provided** - Copy from `env.example` or scenario-specific templates
3. **Tenant isolation** - Each tenant can have its own configuration
4. **Multiple deployment modes** - Local development, Docker, production

---

## Environment Files

### 📄 File Structure

```
stvc_latest/
├── .env                           # Main environment file (NOT in git)
├── env.example                    # Complete template with all variables
├── deployment.env                 # Multi-tenant production template
├── config/
│   └── production.env.template   # Production-specific template
└── deploy/
    └── configs/
        └── docker.env             # Docker development configuration
```

### 📝 File Descriptions

| File | Purpose | When to Use |
|------|---------|-------------|
| `.env` | Active configuration | Always (create from template) |
| `env.example` | Complete reference | Starting new instance |
| `deployment.env` | Multi-tenant setup | Production with multiple tenants |
| `config/production.env.template` | Production config | Production deployment |
| `deploy/configs/docker.env` | Docker setup | Docker/container development |

---

## Required Variables

### 🔴 CRITICAL (Must be configured)

These variables **MUST** be set for the application to work:

```bash
# Flask Configuration
FLASK_ENV=development          # or 'production'
FLASK_SECRET_KEY=<64-char-hex> # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
FLASK_APP=backend/main.py

# Server Configuration
SERVER_HOST=0.0.0.0           # Use 0.0.0.0 for Docker, localhost for local
SERVER_PORT=8080              # Default port
SERVER_URL=https://your-domain-or-ip:8080

# Database Configuration
DATABASE_URL=sqlite:///backend/instance/studentvc.db

# Tenant Configuration
TENANT_ID=root                # Must be: root, tub, fub, or veritas

# Key Storage
KEY_STORAGE_PATH=backend/instance/keys
```

### 🟡 IMPORTANT (Recommended)

These should be configured for proper operation:

```bash
# Security
SECRET_KEY=<different-64-char-hex>
SESSION_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=backend/logs/studentvc.log

# Multi-tenant
MULTI_TENANT_ENABLED=False

# HTTPS
USE_HTTPS=True
SSL_CERT_PATH=adhoc            # or path to certificate
SSL_KEY_PATH=adhoc             # or path to key
```

### 🟢 OPTIONAL (For specific features)

These are only needed for specific functionality:

```bash
# NGROK (for external access during development)
NGROK_ENABLED=True
NGROK_URL=https://your-subdomain.ngrok.io
NGROK_AUTH_TOKEN=your-token

# Authentication (password protection)
ENABLE_AUTH=False
ACCESS_PASSWORD=studentvc2024
REQUIRE_EMAIL_2FA=False
ADMIN_EMAIL=admin@example.com
SMTP_EMAIL=smtp@gmail.com
SMTP_PASSWORD=app-password

# Docker Mode
DOCKER_MODE=true
USE_EXTERNAL_URL=true
EXTERNAL_SERVER_URL=https://your-external-url

# Performance
CACHE_ENABLED=True
RATE_LIMIT_ENABLED=True

# Monitoring
HEALTH_CHECK_ENABLED=True
METRICS_ENABLED=False
```

---

## Configuration by Scenario

### 🖥️ Local Development (Non-Docker)

**Copy from:** `env.example`

```bash
# 1. Create .env file
cp env.example .env

# 2. Edit with minimum required values
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_SECRET_KEY=<generate-secure-key>
FLASK_APP=backend/main.py

SERVER_HOST=localhost
SERVER_PORT=8080
SERVER_URL=https://localhost:8080

DATABASE_URL=sqlite:///backend/instance/studentvc.db
TENANT_ID=root

USE_HTTPS=True
SSL_CERT_PATH=adhoc
SSL_KEY_PATH=adhoc

# Optional: For mobile wallet testing
NGROK_ENABLED=True
NGROK_URL=https://your-subdomain.ngrok.io
```

**Start server:**
```bash
cd backend
source venv/bin/activate
python main.py
```

---

### 🐳 Docker Development

**Use:** `deploy/configs/docker.env`

This file is pre-configured for Docker with local network access:

```bash
# Already configured in docker.env:
USE_EXTERNAL_URL=true
PUBLIC_DOMAIN=192.168.178.122    # Your local IP

# Tenant-specific ports:
TUB_PUBLIC_PORT=8080
FUB_PUBLIC_PORT=8081
ROOT_PUBLIC_PORT=8082
```

**Start with Docker:**
```bash
# Single tenant
docker-compose up -d

# Multiple tenants
./deploy_all_tenants.sh
```

---

### 🚀 Production Multi-Tenant

**Use:** `deployment.env` or `config/production.env.template`

```bash
# Copy and configure
cp deployment.env .env

# Edit critical values:
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<production-secure-key-64-chars>
JWT_SECRET_KEY=<different-production-key-64-chars>

# Tenant URLs (with real domains or ngrok)
TUB_NGROK_URL=https://tub.yourdomain.com
FUB_NGROK_URL=https://fub.yourdomain.com
ROOT_NGROK_URL=https://yourdomain.com

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
HTTPS_REDIRECT=True
```

**Critical Production Checklist:**
- [ ] `DEBUG=False`
- [ ] `FLASK_ENV=production`
- [ ] Unique `SECRET_KEY` and `JWT_SECRET_KEY` (not from templates)
- [ ] Valid SSL certificates (not 'adhoc')
- [ ] Proper domain names (not localhost)
- [ ] Strong passwords if using `ENABLE_AUTH`

---

### 🏢 Veritas Tenant Configuration

The new Veritas tenant requires specific configuration:

```bash
# In .env:
TENANT_ID=veritas

# Veritas-specific (optional):
VERITAS_PUBLIC_PORT=8083
VERITAS_NGROK_URL=https://veritas.yourdomain.com
VERITAS_EXTERNAL_SERVER_URL=https://veritas.yourdomain.com:8083
```

**Allowed Tenants:**
- `root` - Default tenant
- `tub` - TU Berlin
- `fub` - FU Berlin  
- `veritas` - Veritas tenant

---

## Environment Check Tool

### 🛠️ Using the Check Script

We provide a comprehensive environment validation script:

```bash
# Run the environment check
./scripts/env-check.sh
```

**What it checks:**
- ✅ `.env` file exists
- ✅ Required variables are set
- ✅ Variables have been changed from template values
- ✅ Security issues (default keys, debug in production)
- ✅ Required directories exist
- ✅ BBS+ Core library is built
- ✅ Python virtual environment and dependencies
- ✅ Database file status

**Example Output:**
```
========================================
StudentVC Environment Configuration Check
========================================

✓ .env file found

--- Flask Application Settings ---
✓ CONFIGURED: FLASK_ENV
⚠️  NOT CONFIGURED: FLASK_SECRET_KEY (still has template value)
✓ CONFIGURED: FLASK_APP

🔒 SECURITY ISSUE: FLASK_SECRET_KEY is still set to default value!
   Generate a secure key with: python -c "import secrets; print(secrets.token_hex(32))"
```

### 🔧 Manual Checks

```bash
# Check if .env exists
ls -la .env

# Verify key variables are set (without exposing values)
grep "FLASK_SECRET_KEY=" .env | cut -d'=' -f1
grep "TENANT_ID=" .env

# Check tenant database
ls -la backend/src/tenants/instances/*/database.db

# Verify BBS Core library
ls -la backend/*.dylib backend/*.so
```

---

## Common Issues

### ❌ Problem: "FLASK_SECRET_KEY is required"

**Cause:** `.env` file missing or `FLASK_SECRET_KEY` not set

**Fix:**
```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to .env
echo "FLASK_SECRET_KEY=<your-generated-key>" >> .env
```

---

### ❌ Problem: "Invalid tenant: must be one of..."

**Cause:** `TENANT_ID` not set or invalid value

**Fix:**
```bash
# Check current value
grep TENANT_ID .env

# Set to valid tenant
echo "TENANT_ID=root" >> .env
# Or: tub, fub, veritas
```

---

### ❌ Problem: Mobile wallet can't connect (QR code fails)

**Cause:** Server URL not accessible from mobile device

**Solutions:**

**For Development:**
```bash
# Use ngrok
ngrok http 8080

# Add URL to .env
NGROK_ENABLED=True
NGROK_URL=https://abc123.ngrok.io
```

**For Docker:**
```bash
# Find your local IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Update docker.env
PUBLIC_DOMAIN=<your-local-ip>
USE_EXTERNAL_URL=true
```

**For Production:**
```bash
# Use real domain with SSL
SERVER_URL=https://yourdomain.com
EXTERNAL_SERVER_URL=https://yourdomain.com
```

---

### ❌ Problem: "Database locked" or permission errors

**Cause:** Database file permissions or wrong tenant path

**Fix:**
```bash
# Check tenant database directory
ls -la backend/src/tenants/instances/

# Ensure directory exists for your tenant
mkdir -p backend/src/tenants/instances/root

# Check permissions
chmod 755 backend/src/tenants/instances/root
chmod 644 backend/src/tenants/instances/root/database.db
```

---

### ❌ Problem: BBS+ signature errors

**Cause:** BBS Core library not built or wrong architecture

**Fix:**
```bash
# Build BBS Core for your platform
cd backend/bbs-core
cargo build --release

# Copy library to backend
# macOS:
cp target/release/libuniffi_bbs_core.dylib ../

# Linux:
cp target/release/libuniffi_bbs_core.so ../

# Verify
ls -la backend/*.dylib backend/*.so
```

---

### ❌ Problem: HTTPS certificate errors

**Cause:** Using 'adhoc' SSL in production or invalid certificates

**Solutions:**

**Development (adhoc is OK):**
```bash
SSL_CERT_PATH=adhoc
SSL_KEY_PATH=adhoc
```

**Production (use Let's Encrypt):**
```bash
# Install certbot
certbot certonly --standalone -d yourdomain.com

# Update .env
SSL_CERT_PATH=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/yourdomain.com/privkey.pem
```

**Docker (generate self-signed):**
```bash
# Generate certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout docker-key.pem -out docker-cert.pem -days 365

# Update docker.env
SSL_CERT_PATH=/app/docker-cert.pem
SSL_KEY_PATH=/app/docker-key.pem
```

---

## Quick Reference

### 🔑 Generate Secure Keys

```bash
# Flask Secret Key (64 chars)
python -c "import secrets; print(secrets.token_hex(32))"

# JWT Secret Key (different from Flask)
python -c "import secrets; print(secrets.token_hex(32))"

# Access Password (random password)
python -c "import secrets; import string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16)))"
```

### 🔍 Validate Configuration

```bash
# Run full environment check
./scripts/env-check.sh

# Quick check of critical variables
grep -E "FLASK_SECRET_KEY|TENANT_ID|SERVER_URL|DATABASE_URL" .env

# Check for template values (should return nothing)
grep -E "your-.*-here|change-this" .env
```

### 🚀 Start Application

```bash
# Local development
cd backend
source venv/bin/activate
python main.py

# Docker
docker-compose up -d

# Production
gunicorn -c backend/gunicorn.conf.py backend.main:app
```

### 📊 Check Application Status

```bash
# Health check
curl -k https://localhost:8080/health

# Tenant info
curl -k https://localhost:8080/api/tenant/info

# BBS Core status
python -c "from backend.bbs_core import BbsCore; print('BBS Core OK')"
```

---

## Environment Variables Reference

### Complete Variable List

For a complete, up-to-date list of all 200+ environment variables, see:
- `env.example` - Most comprehensive
- `config/production.env.template` - Production-focused
- `deployment.env` - Multi-tenant setup

### Variable Categories

| Category | Count | Examples |
|----------|-------|----------|
| Flask Core | 5 | `FLASK_ENV`, `FLASK_SECRET_KEY`, `FLASK_DEBUG` |
| Server | 8 | `SERVER_HOST`, `SERVER_PORT`, `SERVER_URL` |
| Database | 12 | `DATABASE_URL`, `DB_POOL_SIZE` |
| Security | 15 | `SECRET_KEY`, `JWT_SECRET_KEY`, `SESSION_TIMEOUT` |
| Tenant | 10 | `TENANT_ID`, `MULTI_TENANT_ENABLED` |
| NGROK | 5 | `NGROK_ENABLED`, `NGROK_URL`, `NGROK_AUTH_TOKEN` |
| Authentication | 7 | `ENABLE_AUTH`, `ACCESS_PASSWORD`, `ADMIN_EMAIL` |
| Docker | 8 | `DOCKER_MODE`, `USE_EXTERNAL_URL` |
| Logging | 6 | `LOG_LEVEL`, `LOG_FILE` |
| Performance | 12 | `CACHE_ENABLED`, `RATE_LIMIT_ENABLED` |
| SSL/HTTPS | 8 | `USE_HTTPS`, `SSL_CERT_PATH`, `SSL_KEY_PATH` |
| Monitoring | 6 | `HEALTH_CHECK_ENABLED`, `METRICS_ENABLED` |

---

## Best Practices

### ✅ DO

- ✅ Use `env.example` as a starting template
- ✅ Generate unique keys for each environment
- ✅ Use different keys for `SECRET_KEY` and `JWT_SECRET_KEY`
- ✅ Set `DEBUG=False` in production
- ✅ Use proper SSL certificates in production
- ✅ Run `./scripts/env-check.sh` before deployment
- ✅ Keep `.env` out of version control
- ✅ Document any custom environment variables

### ❌ DON'T

- ❌ Commit `.env` files to git
- ❌ Use template/example values in production
- ❌ Use the same keys across environments
- ❌ Enable `DEBUG=True` in production
- ❌ Use `adhoc` SSL certificates in production
- ❌ Hardcode secrets in code
- ❌ Share `.env` files via insecure channels

---

## Support

### 📚 Additional Documentation

- [README.md](../README.md) - Main project documentation
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide
- [TENANT_SYSTEM_TEST_RESULTS.md](./TENANT_SYSTEM_TEST_RESULTS.md) - Multi-tenant testing
- [PERFECT_TENANT_IMPLEMENTATION_GUIDE.md](./PERFECT_TENANT_IMPLEMENTATION_GUIDE.md) - Tenant isolation

### 🐛 Issues

If you encounter environment configuration issues:

1. Run `./scripts/env-check.sh` first
2. Check the [Common Issues](#common-issues) section
3. Review logs: `tail -f backend/logs/studentvc.log`
4. Validate tenant: Check `backend/src/tenants/instances/<tenant-id>/`

### 🔧 Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Check what's loaded
python -c "import os; print({k:v for k,v in os.environ.items() if 'FLASK' in k or 'TENANT' in k})"

# Test database connection
python -c "from backend.src.tenants.database import tenant_db_manager; print(tenant_db_manager.get_tenant_from_environment())"
```

---

**Last Updated:** November 8, 2025  
**Version:** 1.0  
**Maintained by:** StudentVC Team

