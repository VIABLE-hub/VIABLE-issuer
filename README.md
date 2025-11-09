# VERITAS - Enterprise-Ready Privacy-Preserving Digital Credentials Platform

**Multi-tenant platform for issuing privacy-preserving digital credentials using BBS+ selective-disclosure cryptography**

**Supervisor:** Patrick Herbke (p.herbke@tu-berlin.de)

---

## Project Overview

VERITAS is a multi-tenant platform currently in prototype stage, being developed into a university-ready infrastructure. The project aims to scale the platform, enhance reliability, and increase interoperability through backend modernization, real-time monitoring, automated certificate management, and cross-platform mobile wallet support.

**Current Status:** Prototype → Enterprise-Ready Infrastructure

---

## Quick Start

### Setup
```bash
make setup              # Install dependencies
make test-startup       # Verify installation
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
# Or manually: lsof -ti:8081 | xargs kill -9  # For port 8081, etc.
```

---

## Project Goals

### 1. Backend Refactoring & Monitoring (2 students)
- Refactor core backend modules and enhance code quality
- Add production monitoring with Prometheus and Grafana
- Improve reliability and scalability

### 2. Crypto Standards & PKI (2 students)
- Implement automated X.509 certificate management
- Extend credential support to ECDSA/SD-JWT alongside BBS+
- Support multiple cryptographic standards (W3C VC, IETF SD-JWT, OpenID4VCI)

### 3. Mobile Wallet Development (1-2 students)
- Develop Android wallet support
- Perform cross-platform testing (iOS + Android)
- Ensure interoperability between platforms

### 4. Documentation & Benchmarks
- Provide comprehensive documentation
- Create performance benchmarks
- Prepare final demo

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

## Available Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install dependencies |
| `make start-all` | Start all tenants simultaneously |
| `make stop-all` | Stop all tenant servers |
| `make dev-root` | Start root tenant (port 8083) |
| `make dev-tub` | Start TU Berlin tenant (port 8081) |
| `make dev-fub` | Start FU Berlin tenant (port 8082) |
| `make dev-veritas` | Start Veritas tenant (port 8080) |
| `make test` | Run all tests |
| `make clean` | Clean temporary files |
| `make kill-port` | Kill process on port 8080 |

---

## Technology Stack

### Required Skills
- **Python 3.9+** (Flask, SQLAlchemy, pytest)
- **JavaScript/TypeScript** (Alpine.js, Socket.IO)
- **Git, Docker, REST APIs**
- **Basic cryptography** (JWT, digital signatures)

### Nice to Have
- **Rust** (BBS+ library modifications)
- **Kubernetes** (multi-tenant scaling)
- **Swift/Kotlin** (mobile wallets)
- **W3C VC, IETF SD-JWT, OpenID4VCI** standards
- **PKI concepts** (X.509, OCSP, HSM)

### Standards & Protocols
- **W3C Verifiable Credentials** (VC)
- **IETF SD-JWT** (Selective Disclosure JWT)
- **OpenID4VCI** (OpenID for Verifiable Credential Issuance)
- **OpenID4VP** (OpenID for Verifiable Presentations)
- **BBS+ Signatures** (Zero-knowledge proofs)

---

## Development

### Activate Virtual Environment
```bash
source test_env/bin/activate
```

### View Logs
```bash
tail -f logs/*.log
```

### Database Location
```bash
backend/src/tenants/instances/{tenant_id}/database.db
```

---

## Documentation

- **Project Goals:** [IoSL-Goals.md](IoSL-Goals.md)
- **Deployment:** [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Architecture:** [docs/VC_LOGIN_ARCHITECTURE.md](docs/VC_LOGIN_ARCHITECTURE.md)
- **Module Structure:** [backend/src/README.md](backend/src/README.md)
- **Blueprint Structure:** [backend/src/BLUEPRINT_STRUCTURE.md](backend/src/BLUEPRINT_STRUCTURE.md)

---

**Focus Label:** Software Development/Engineering
