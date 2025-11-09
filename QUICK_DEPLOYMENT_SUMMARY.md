# 🎯 Quick Deployment Summary - StudentVC

**Last Updated:** 2025-11-09

---

## ⚡ Quick Answers

### Q: What happens with `make dev`?
❌ **NOT RECOMMENDED** - This is the old default command that only starts ONE tenant (root) on port 8080. Use `make dev-all` instead.

### Q: What happens with `make dev-tub` / `make dev-fub` / `make dev-veritas` / `make dev-root`?
✅ Starts a **single tenant** in **foreground** mode (you see all logs). Useful for debugging.

```bash
make dev-tub       # Starts TUB on port 8081 (foreground)
make dev-veritas   # Starts Veritas on port 8080 (foreground)
```

### Q: What happens with `make dev-all`?
✅ **RECOMMENDED** - Starts **all 4 tenants** simultaneously as **background processes** with logging.

```bash
make dev-all
# Starts:
#   - Veritas on port 8080
#   - TUB on port 8081
#   - FUB on port 8082
#   - Root on port 8083
```

### Q: Is ngrok default when started?
❌ **NO** - Ngrok is **NOT** default!

**Default behavior:**
- System uses local IP address (e.g., `https://192.168.178.156:8080`)
- Works for devices on same WiFi
- **Does NOT work** for external mobile devices

### Q: Can students configure ngrok?
✅ **YES** - Two ways:

**Method 1: Settings UI** (Easiest)
```bash
# 1. Start ngrok manually
ngrok http 8080

# 2. Copy URL (e.g., https://abc123.ngrok-free.app)

# 3. Open browser
https://localhost:8080/veritas/login

# 4. Go to Settings → Network
# Enter: abc123.ngrok-free.app
# Click: Save Network Settings

# Done! System now uses ngrok URL
```

**Method 2: Makefile**
```bash
make dev-ngrok
# Auto-starts ngrok and shows URL
# Still need to configure in Settings UI
```

### Q: How does production deployment work?
✅ **Use environment variables:**

```bash
# Production deployment
export EXTERNAL_SERVER_URL=https://studentvc.university.edu
export USE_EXTERNAL_URL=true

# Start servers
make dev-all

# System automatically uses EXTERNAL_SERVER_URL
# No ngrok configuration needed
```

---

## 📊 URL Priority System

The system resolves server URLs in this order:

```
1. EXTERNAL_SERVER_URL (if USE_EXTERNAL_URL=true)
   └─> Used for production
   
2. Tenant NGROK URL (if configured in Settings)
   └─> Used for development/testing
   
3. Local IP address (fallback)
   └─> Used by default
```

**Code Location:** `backend/src/utils.py` → `get_current_server_url()`

---

## 🎓 For Students

### **Development Environment Setup**

```bash
# 1. Start all servers
make dev-all

# 2. Access locally
https://localhost:8080/veritas/

# 3. For mobile testing, configure ngrok:
#    - Start: ngrok http 8080
#    - Configure in Settings UI
#    - Access: https://your-ngrok-url.ngrok-free.app/veritas/
```

### **What Students Need to Know**

✅ **Default = Local IP (same WiFi only)**
- No ngrok needed for local testing
- Works on same network

✅ **Ngrok = Optional (for remote access)**
- Only needed for mobile wallet testing
- Configure via Settings UI
- Each tenant can have different ngrok URL

✅ **Production = Environment Variable**
- Set EXTERNAL_SERVER_URL
- No Settings UI configuration needed
- Works on real servers

---

## 🔧 Configuration Storage

### **Ngrok URLs are stored PER TENANT:**

```
Database: backend/src/tenants/instances/{tenant}/database.db
Table: tenant_settings
Column: network_settings

JSON Structure:
{
  "use_ngrok": true,
  "ngrok_url": "https://abc123.ngrok-free.app"
}
```

### **Verification:**

```bash
# Check what URL veritas tenant uses
python3 scripts/check_tenant_network.py veritas

# Or via API
curl -k https://localhost:8080/api/network/status | jq
```

---

## 🚀 Deployment Scenarios

### **Scenario 1: Local Development (Student)**
```bash
make dev-all
# Uses: https://192.168.x.x:8080
# Perfect for: Same WiFi testing
```

### **Scenario 2: Mobile Testing (Student)**
```bash
ngrok http 8080
# Copy URL, configure in Settings UI
# Uses: https://your-ngrok.ngrok-free.app
# Perfect for: Mobile wallet testing
```

### **Scenario 3: Production Server (University)**
```bash
export EXTERNAL_SERVER_URL=https://studentvc.uni.edu
export USE_EXTERNAL_URL=true
make dev-all
# Uses: https://studentvc.uni.edu
# Perfect for: Production deployment
```

---

## 📝 Common Commands

```bash
# Start development
make dev-all              # All tenants (recommended)
make dev-veritas          # Single tenant (debugging)

# Stop servers
make stop-all             # Stop all tenants

# Check status
lsof -i :8080            # Check port
tail -f logs/veritas.log # Watch logs

# Ngrok
ngrok http 8080          # Start ngrok
make dev-ngrok           # Auto-start ngrok
```

---

## ✅ Key Points

1. **`make dev-all` is the recommended command** ✅
2. **Ngrok is NOT default** - Local IP is default ✅
3. **Students CAN configure ngrok** via Settings UI ✅
4. **Production uses environment variables** not Settings UI ✅
5. **Each tenant can have different ngrok URL** ✅
6. **Settings are stored in tenant database** not config files ✅

---

## 🎯 Student Workflow

```
┌─────────────────────────────────────────┐
│ Step 1: Start Servers                   │
│   make dev-all                          │
└─────────────────────────────────────────┘
                 │
                 ├─ For LOCAL testing
                 │   └─> Use: https://localhost:8080
                 │       (or local IP for mobile on same WiFi)
                 │
                 └─ For REMOTE testing
                     ├─> Start: ngrok http 8080
                     ├─> Copy ngrok URL
                     ├─> Configure in Settings UI
                     └─> Use: https://your-ngrok.ngrok-free.app
```

---

## 📚 Full Documentation

See `DEPLOYMENT_GUIDE.md` for complete details including:
- Detailed command explanations
- Troubleshooting guide
- Production deployment steps
- Docker configuration
- System architecture

---

**Status:** ✅ Verified Working  
**Version:** 2.0  
**Date:** 2025-11-09

