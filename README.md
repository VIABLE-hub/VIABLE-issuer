# VERITAS - Enterprise-Ready Privacy-Preserving Digital Credentials Platform

**Multi-tenant platform for issuing privacy-preserving digital credentials using BBS+ selective-disclosure cryptography**

**Supervisor:** Patrick Herbke (p.herbke@tu-berlin.de)

---

## Project Overview

VERITAS is a multi-tenant platform currently in prototype stage, being developed into a university-ready infrastructure.

---

## Quick Start

### Prerequisites

- **Python 3.12**
- **Rust**
- **For Windows Users:** WSL (Windows Subsystem for Linux) is **required** - see [Windows Setup Guide](#-windows-setup-guide) below

### Setup
```bash
make setup              # Install dependencies
```

### Start/Stop Tenants

**Start all tenants:**
```bash
make start-all          # Starts all tenants on different ports
```

**Stop all tenants:**
```bash
make stop-all           # Stops all running tenant servers
```

**Start single tenant:**
```bash
make dev-root           # Root tenant (port 8083)
make dev-tub            # TU Berlin (port 8081)
make dev-fub            # FU Berlin (port 8082)
make dev-veritas        # Veritas (port 8080)
```

**Stop single tenant:**
```bash
make kill-port          # Kills process on port 8080
```

---

## 🪟 Windows Setup Guide

### **Why WSL is Required for Windows**

The BBS+ core library uses native Linux binaries (`.so` files) that are **not available for Windows**. Therefore, **all Windows users must use WSL (Windows Subsystem for Linux)** to run this project.

### **Complete Setup for Windows Users**

#### **Step 1: Install WSL**
```powershell
# Run in PowerShell as Administrator
wsl --install
```
> **Note:** You may need to restart your computer after installation.

#### **Step 2: Open WSL Terminal**
```powershell
# In PowerShell or Windows Terminal
wsl
```

#### **Step 3: Navigate to Your Project**
```bash
cd /mnt/c/path/to/your/project/stvc
```
> **Note:** Replace with your actual project path. Windows drives are mounted under `/mnt/` in WSL (e.g., `C:\Users\...` becomes `/mnt/c/Users/...`)

#### **Step 4: Update APT and Install Dependencies (One-time Setup)**
```bash
# Update package lists
sudo apt update

# Install make
sudo apt install make

# Install Python virtual environment support
sudo apt install python3.12-venv
```

#### **Step 5: Setup Virtual Environment (One-time Setup)**
```bash
make setup
```

#### **Step 6: Run the Application**
```bash
# Run TU Berlin tenant on port 8081
make dev-tub

# OR run other tenants:
make dev-root     # Root tenant on port 8083
make dev-fub      # FU Berlin on port 8082
make dev-veritas  # Veritas on port 8080
```

---

### **Using IntelliJ IDEA with WSL (Windows)**

1. **Configure WSL Python Interpreter:**
    - Go to `File` → `Settings` → `Project` → `Python Interpreter`
    - Click `Add Interpreter` → `On WSL...`
    - Select your WSL distribution
    - Choose the Python interpreter: `<project_path>/.venv/bin/python`

2. **Create Run Configuration:**
    - Go to `Run` → `Edit Configurations`
    - Click `+` → `Python`
    - **Script path:** `<project_path>/backend/main.py`
    - **Working directory:** `<project_path>/backend`
    - **Environment variables:**
        - `TENANT_ID=tub`
        - `SERVER_PORT=8081`
    - **Python interpreter:** Select the WSL interpreter you configured

3. **Run the application** using the play button or `Shift+F10`

---

### **Quick Reference for Windows Daily Use**
```bash
# Open WSL
wsl

# Navigate to project
cd /mnt/c/path/to/your/project/stvc

# Run application
make dev-tub
```

---

### **Troubleshooting Windows/WSL Issues**

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'flask'` | Run `make setup` to install dependencies |
| `make: command not found` | Install make: `sudo apt install make` |
| Virtual environment creation fails | Install python3-venv: `sudo apt install python3.12-venv` |
| Permission denied errors | Use `sudo` for apt commands (e.g., `sudo apt update`) |
| Unicode/Emoji encoding errors in console | These are display-only warnings in WSL and don't affect functionality |

---

## Project Structure

### Core Backend Modules
```
backend/src/
├── issuer/              # Credential Issuance
│   ├── BBS+ credential signing
│   ├── OID4VC metadata and QR code generation
│   └── Multi-tenant credential templates
│
├── verifier/            # Credential Verification
│   ├── BBS+ proof verification
│   ├── Selective disclosure handling
│   └── OID4VP presentation requests
│
├── auth/                # Authentication System
│   ├── Traditional username/password
│   └── VC-based authentication
│
├── settings/            # System Configuration
│   ├── Tenant configuration and branding
│   ├── Key management (BBS+, JWT, X.509)
│   ├── Selective disclosure settings
│   └── Network API configuration
│
├── tenants/             # Multi-Tenant Management
│   ├── Tenant detection and routing
│   ├── Isolated database per tenant
│   └── Tenant-specific configuration
│
├── validate/            # Credential Validation
│   ├── Credential status management
│   └── Revocation and lifecycle tracking
│
├── plugin_system/       # Plugin Architecture
│   ├── Plugin interface and loader
│   └── Event system for plugins
│
└── models.py            # Database Models
```

### Storage & Crypto Modules
```
plugins/
├── blockchain_storage/  # Blockchain storage plugin
└── ipfs_storage/        # IPFS storage plugin

backend/
├── bbs-core/            # Rust-based BBS+ core library
├── issuer/key_generator.py      # BBS+ key generation
└── issuer/tenant_key_generator.py  # Tenant-specific keys
```

### Mobile Applications

```
mobile/
└── ios/                 # iOS Wallet (existing)
    └── [Android wallet to be developed]
```
---
