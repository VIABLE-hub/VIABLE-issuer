# VERITAS - Enterprise-Ready Privacy-Preserving Digital Credentials Platform

**Multi-tenant platform for issuing privacy-preserving digital credentials using BBS+ selective-disclosure cryptography**

**Supervisor:** Patrick Herbke (p.herbke@tu-berlin.de)

---

## Project Overview

VERITAS is a multi-tenant platform currently in prototype stage, being developed into a university-ready infrastructure.

---

## Quick Start

### Prerequisites

**Python 3.12**

**Rust**

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
