# 🚀 StudentVC Deployment Guide

**Complete guide for development and production deployment**

---

## 📋 Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Makefile Commands Explained](#makefile-commands-explained)
3. [Ngrok Configuration](#ngrok-configuration)
4. [Production Deployment](#production-deployment)
5. [Troubleshooting](#troubleshooting)

---

## 🛠️ Development Environment Setup

### Prerequisites

```bash
# Required
- Python 3.12+
- Virtual environment (test_env)
- ngrok account (for mobile wallet testing)

# Optional
- Docker (for production testing)
```

### Quick Start

```bash
# 1. Clone repository
cd /path/to/studentvc_backups/stvc_latest

# 2. Setup virtual environment (if not exists)
make setup

# 3. Start development servers
make dev-all
```

---

## 🎯 Makefile Commands Explained

### `make dev` (DEFAULT - NOT RECOMMENDED)

**⚠️ DEPRECATED - Use `make dev-all` instead**

- Starts ONLY ONE tenant (historically root)
- Port: 8080
- **NOT suitable for multi-tenant testing**

### `make dev-all` ✅ **RECOMMENDED**

**What it does:**
- Starts ALL 4 tenants simultaneously
- Each tenant runs on separate port
- Background processes with logging

**Ports:**
```
Veritas:  https://localhost:8080  (Port 8080)
TUB:      https://localhost:8081  (Port 8081)
FUB:      https://localhost:8082  (Port 8082)
Root:     https://localhost:8083  (Port 8083)
```

**Command:**
```bash
make dev-all
```

**What happens:**
1. Checks for existing servers and stops them
2. Starts each tenant as background process
3. Creates PID files in `logs/*.pid`
4. Logs to `logs/*.log`

**Process:**
```
scripts/start-all-tenants.sh
    ↓
Starts 4 separate Python processes:
    1. TENANT_ID=veritas SERVER_PORT=8080 python main.py &
    2. TENANT_ID=tub SERVER_PORT=8081 python main.py &
    3. TENANT_ID=fub SERVER_PORT=8082 python main.py &
    4. TENANT_ID=root SERVER_PORT=8083 python main.py &
```

### `make dev-veritas` / `make dev-tub` / `make dev-fub` / `make dev-root`

**What it does:**
- Starts SINGLE tenant in foreground
- Useful for debugging specific tenant

**Example:**
```bash
# Start only Veritas tenant
make dev-veritas
# Runs: TENANT_ID=veritas SERVER_PORT=8080 python main.py

# Start only TUB tenant
make dev-tub
# Runs: TENANT_ID=tub SERVER_PORT=8081 python main.py
```

### `make stop-all`

**What it does:**
- Stops all running tenant servers
- Kills processes on ports 8080-8083
- Removes PID files

**Command:**
```bash
make stop-all
```

---

## 🌐 Ngrok Configuration

### Understanding URL Priority

The system uses this priority order for server URLs:

```
1. EXTERNAL_SERVER_URL (production)
   ↓ (if not set)
2. Tenant NGROK URL (development/testing)
   ↓ (if not set)
3. Local IP (fallback)
```

### ❌ **Ngrok is NOT default!**

**By default, the system uses:**
- Local IP address (e.g., `https://192.168.178.156:8080`)
- Works for devices on same WiFi network
- **DOES NOT work** for mobile wallets outside your network

### ✅ **How to Enable Ngrok** (For Students)

#### **Method 1: Using Settings UI** (Recommended)

1. **Start ngrok manually:**
   ```bash
   # In separate terminal
   ngrok http 8080
   ```

2. **Copy the ngrok URL:**
   ```
   https://abc123def456.ngrok-free.app
   ```

3. **Configure in StudentVC:**
   - Open: `https://localhost:8080/veritas/login`
   - Login with credentials
   - Navigate to: **Settings → Network**
   - Enter ngrok domain: `abc123def456.ngrok-free.app`
   - Click "Save Network Settings"

4. **Done!** The system now uses ngrok URL for:
   - QR codes in Issuer
   - QR codes in Verifier
   - All mobile wallet communication

#### **Method 2: Using Makefile** (Advanced)

```bash
# Start ngrok automatically
make dev-ngrok

# Output:
# ✅ ngrok tunnel established:
# 🌐 Public URL: https://abc123.ngrok-free.app
# 🔧 Dashboard: http://localhost:4040
```

Then configure the URL in Settings UI as above.

#### **Method 3: Environment Variable** (CI/CD)

```bash
# Set before starting server
export NGROK_URL=https://your-ngrok-url.ngrok-free.app
make dev-all
```

### **Ngrok Storage Location**

Ngrok URLs are stored **per tenant** in database:

```
Database: backend/src/tenants/instances/{tenant}/database.db
Table: tenant_settings
Column: network_settings
JSON: { "use_ngrok": true, "ngrok_url": "https://..." }
```

### **Verifying Ngrok Configuration**

```bash
# Check what URL is being used
curl -k https://localhost:8080/api/network/status | jq

# Output shows:
# {
#   "server_url": "https://your-ngrok.ngrok-free.app",
#   "use_ngrok": true,
#   "ngrok_url": "https://your-ngrok.ngrok-free.app"
# }
```

---

## 📱 Development Workflow (For Students)

### **Scenario 1: Testing on Same WiFi**

```bash
# 1. Start all tenants
make dev-all

# 2. Find your local IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# 3. Open on mobile device (same WiFi)
https://192.168.178.156:8080/veritas/issuer
```

**No ngrok needed!**

### **Scenario 2: Testing with Remote Device**

```bash
# 1. Start ngrok
ngrok http 8080

# 2. Start all tenants
make dev-all

# 3. Configure ngrok URL in Settings UI
# Navigate to: https://localhost:8080/veritas/settings
# Enter ngrok domain in Network section

# 4. Use from anywhere
https://abc123.ngrok-free.app/veritas/issuer
```

### **Scenario 3: Debugging Single Tenant**

```bash
# Stop all servers
make stop-all

# Start only one tenant in foreground
make dev-veritas

# See all logs in real-time
# Press Ctrl+C to stop
```

---

## 🏭 Production Deployment

### **Option 1: Docker Deployment**

```bash
# 1. Set environment variables
export EXTERNAL_SERVER_URL=https://your-domain.com
export USE_EXTERNAL_URL=true
export DOCKER_MODE=true

# 2. Build and run
docker-compose up -d

# 3. Verify
curl https://your-domain.com/health
```

### **Option 2: Server Deployment (Ubuntu/Nginx)**

```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3 python3-pip nginx certbot

# 2. Clone repository
git clone <repo-url> /var/www/studentvc
cd /var/www/studentvc

# 3. Setup virtual environment
python3 -m venv test_env
source test_env/bin/activate
pip install -r backend/requirements.txt

# 4. Configure systemd services
# Create: /etc/systemd/system/studentvc-{tenant}.service
# See: deploy/configs/systemd/*.service

# 5. Start services
sudo systemctl start studentvc-veritas
sudo systemctl start studentvc-tub
sudo systemctl start studentvc-fub
sudo systemctl start studentvc-root

# 6. Configure Nginx reverse proxy
# Copy: deploy/configs/nginx/studentvc.conf
sudo systemctl restart nginx

# 7. Setup SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

### **Environment Variables for Production**

```bash
# Required
EXTERNAL_SERVER_URL=https://your-domain.com
USE_EXTERNAL_URL=true

# Optional
DOCKER_MODE=true              # If using Docker
SERVER_PORT=8080              # Default port
TENANT_ID=veritas             # Tenant to run
```

---

## 🔍 URL Resolution Logic

### Code Location: `backend/src/utils.py`

```python
def get_current_server_url():
    # Priority 1: EXTERNAL_SERVER_URL (production)
    if os.environ.get('USE_EXTERNAL_URL') == 'true':
        return os.environ.get('EXTERNAL_SERVER_URL')
    
    # Priority 2: Tenant NGROK URL (development)
    tenant_settings = TenantSettings.get_or_create_default(tenant_id)
    if tenant_settings.network_settings.get('use_ngrok'):
        return tenant_settings.network_settings['ngrok_url']
    
    # Priority 3: Local IP (fallback)
    return f"https://{get_local_ip()}:{port}"
```

### **When Each URL is Used:**

| Scenario | URL Used | Set Via |
|----------|----------|---------|
| Local WiFi testing | `https://192.168.x.x:8080` | Automatic |
| Ngrok testing | `https://xxx.ngrok-free.app` | Settings UI |
| Production | `https://your-domain.com` | Environment variable |

---

## 🧪 Testing Checklist

### **Before Students Start:**

- [ ] Virtual environment setup: `make setup`
- [ ] All dependencies installed: `pip list`
- [ ] Ngrok account created (optional)
- [ ] Can access `https://localhost:8080`

### **Development Testing:**

- [ ] All tenants start: `make dev-all`
- [ ] Can access each tenant URL
- [ ] Settings page loads
- [ ] Can configure ngrok URL
- [ ] QR codes generate correctly

### **Mobile Wallet Testing:**

- [ ] Ngrok configured and running
- [ ] Can access issuer from mobile
- [ ] Can scan QR code
- [ ] Credential issuance works
- [ ] Credential verification works

---

## 🐛 Troubleshooting

### **Problem: "Address already in use"**

```bash
# Check what's using the port
lsof -i :8080

# Stop all servers
make stop-all

# Restart
make dev-all
```

### **Problem: "Ngrok URL not working"**

```bash
# 1. Check ngrok is running
curl http://localhost:4040/api/tunnels

# 2. Verify configuration
curl -k https://localhost:8080/api/network/status | jq

# 3. Update in Settings UI
# Go to: Settings → Network → Enter ngrok domain
```

### **Problem: "Selective disclosure not working"**

```bash
# 1. Check database
python3 scripts/check_selective_disclosure_db.py

# 2. Restart servers
make stop-all
make dev-all

# 3. Check logs
tail -f logs/veritas.log | grep "SELECTIVE DISCLOSURE"
```

### **Problem: "Import error: get_current_tenant_id"**

```bash
# Fixed in: backend/src/tenants/__init__.py
# Restart servers to apply fix
make stop-all
make dev-all
```

---

## 📊 Server Status Check

### **Check Running Servers:**

```bash
# List all processes
lsof -i :8080 -i :8081 -i :8082 -i :8083 | grep LISTEN

# Check logs
tail -f logs/*.log
```

### **Check Configuration:**

```bash
# Database settings
python3 scripts/check_selective_disclosure_db.py

# Network settings
curl -k https://localhost:8080/api/network/status
```

---

## 📚 Quick Reference

### **Start Development:**

```bash
make dev-all              # Start all tenants
make dev-veritas          # Start single tenant
make stop-all             # Stop all tenants
```

### **Configure Ngrok:**

```bash
ngrok http 8080           # Start ngrok
# Then: Settings UI → Network → Enter domain
```

### **Check Status:**

```bash
lsof -i :8080             # Check port
tail -f logs/veritas.log  # Watch logs
python3 scripts/check_selective_disclosure_db.py  # Check DB
```

### **Access URLs:**

```
Local:   https://localhost:8080/veritas/
         https://localhost:8081/tub/
         https://localhost:8082/fub/
         https://localhost:8083/root/

Mobile:  https://your-ngrok.ngrok-free.app/veritas/
```

---

## ✅ Summary for Students

### **To Run Development Environment:**

1. **Start all servers:**
   ```bash
   make dev-all
   ```

2. **For local testing (same WiFi):**
   - Open `https://localhost:8080` in browser
   - Use local IP on mobile devices

3. **For remote testing (mobile wallet):**
   ```bash
   # Terminal 1: Start ngrok
   ngrok http 8080
   
   # Copy ngrok URL, then:
   # Browser: Settings → Network → Enter ngrok domain → Save
   ```

4. **To stop:**
   ```bash
   make stop-all
   ```

### **Ngrok is NOT Default:**
- System uses local IP by default
- Configure ngrok URL in Settings UI
- Ngrok is optional (only needed for remote access)

### **For Production:**
- Set `EXTERNAL_SERVER_URL` environment variable
- Use reverse proxy (Nginx)
- No ngrok needed

---

**Last Updated:** 2025-11-09  
**Version:** 2.0  
**Status:** ✅ Production Ready

