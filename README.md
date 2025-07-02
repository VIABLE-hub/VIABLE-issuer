# StudentVC - Digital Student Credentials

Privacy-preserving digital student credentials platform with BBS+ selective disclosure and mobile wallet support.

[![Demo](https://img.shields.io/badge/Demo-Available-brightgreen)](https://github.com/pherbke/stvc) [![Multi-Tenant](https://img.shields.io/badge/Multi--Tenant-Supported-blue)](https://github.com/pherbke/stvc) [![BBS+](https://img.shields.io/badge/BBS%2B-Selective%20Disclosure-purple)](https://github.com/pherbke/stvc)

## Features

- **Selective Disclosure**: Share only required information using BBS+ zero-knowledge signatures
- **Mobile Wallet**: iOS app for secure credential storage and presentation
- **Multi-Tenant**: Support for multiple universities with isolated databases and branding
- **Real-time Verification**: Instant QR code verification with WebSocket updates
- **Custom Branding**: University-specific themes, logos, and colors
- **Production Ready**: Docker and Kubernetes deployment with auto-scaling

## Prerequisites

- **Python 3.9+** with pip
- **Docker** (for containerized deployment)
- **kubectl** (for Kubernetes deployment)
- **NGROK** (optional, for mobile wallet testing)

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd stvc

# Setup virtual environment and install dependencies
make setup

# Start development server (ROOT tenant, port 8080, HTTPS)
make dev
```

**What `make dev` does:**
1. Kills any existing processes on port 8080
2. Verifies `test_env` virtual environment exists
3. Starts HTTPS server on `https://localhost:8080`
4. Loads ROOT tenant (default StudentVC branding)
5. Uses isolated tenant database and configuration

Access at: **https://localhost:8080**

## Multi-Tenant Development

StudentVC supports multiple university tenants with **isolated databases, keys, and branding**:

```bash
# ROOT tenant (default StudentVC branding)
make dev-root    # https://localhost:8080

# TU Berlin tenant (red branding, TUB logo)
make dev-tub     # https://localhost:8080

# FU Berlin tenant (green branding, FUB logo)  
make dev-fub     # https://localhost:8080
```

Each tenant has:
- **Separate database** (`backend/src/tenants/instances/{tenant}/database.db`)
- **Unique BBS+ keys** (`backend/src/tenants/instances/{tenant}/keys/`)
- **Custom branding** (logos, colors, themes)
- **Isolated configuration** (`backend/src/tenants/instances/{tenant}/config.json`)

## Core Endpoints

| Endpoint | Description |
|----------|-------------|
| `/issuer` | Issue digital credentials with BBS+ signatures |
| `/verifier` | Verify credentials with selective disclosure |
| `/vcstatus` | Check credential validity and revocation status |
| `/settings` | Configure tenant settings, network, and keys |

## Deployment

### Local Development

```bash
# First-time setup
make setup

# Development server
make dev        # Default ROOT tenant
make dev-tub    # TU Berlin tenant  
make dev-fub    # FU Berlin tenant
```

### Docker Deployment

#### Multi-Tenant Deployment (All Universities)
```bash
# Deploy all tenants with load balancing
./deploy.sh

# This starts:
# - TUB tenant: https://localhost:8080
# - FUB tenant: https://localhost:8081  
# - ROOT tenant: https://localhost:8082
```

#### Single-Tenant Deployment
```bash
# Deploy specific tenant only
SINGLE_TENANT=tub ./deploy.sh   # TUB only on port 8080
SINGLE_TENANT=fub ./deploy.sh   # FUB only on port 8080
SINGLE_TENANT=root ./deploy.sh  # ROOT only on port 8080
```

#### Manual Docker Commands
```bash
# Using individual deployment scripts
./deploy/scripts/deploy-docker-all.sh   # All tenants
./deploy/scripts/deploy-docker-tub.sh   # TUB only
./deploy/scripts/deploy-docker-fub.sh   # FUB only
./deploy/scripts/deploy-docker-root.sh  # ROOT only
```

### Kubernetes Deployment

```bash
# Prerequisites: kubectl + cluster + NGINX ingress
docker build -t studentvc:latest ./backend
./deploy.sh kubernetes

# Access via port-forwarding
kubectl port-forward -n studentvc svc/studentvc-tub 8080:80
kubectl port-forward -n studentvc svc/studentvc-fub 8081:80  
kubectl port-forward -n studentvc svc/studentvc-root 8082:80
```

## Available Commands

```bash
# Development
make dev         # Start development server (ROOT tenant)
make dev-root    # Start ROOT tenant explicitly
make dev-tub     # Start TU Berlin tenant
make dev-fub     # Start FU Berlin tenant

# Setup & Maintenance  
make setup       # Create virtual environment and install dependencies
make install     # Install dependencies in existing test_env
make clean       # Clean cache files and reset database
make kill-port   # Kill processes on port 8080

# Testing
make test        # Run all tests in test_env environment
make setup-test  # Install additional testing packages

# Help
make help        # Show all available commands
```

## Mobile Wallet Integration

1. **Start development server** with ngrok for mobile access:
   ```bash
   # Configure ngrok URL in Settings
   make dev
   # Visit: https://localhost:8080/settings
   ```

2. **Generate QR code** at `/issuer` endpoint

3. **Scan with iOS StudentVC wallet** app

4. **Verify credentials** at `/verifier` with selective disclosure

## Configuration

### Environment Variables
- `TENANT_ID`: Set tenant (root, tub, fub)
- `PORT`: Server port (default: 8080)
- `HOST`: Server host (default: 0.0.0.0)

### Tenant Configuration
Each tenant configuration in `backend/src/tenants/instances/{tenant}/config.json`:
```json
{
  "name": "TU Berlin",
  "issuer_name": "TU Berlin Credential Service",
  "primary_color": "#c50e1f",
  "logo_path": "/static/tub_logo.png",
  "vc_logo_path": "/static/tub-vc-logo.png"
}
```

## Contributing

See [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for development guidelines and contribution process.

## License

MIT License - see [LICENSE](./LICENSE) for details.

---

**StudentVC** - Empowering universities with privacy-preserving digital credentials using BBS+ selective disclosure and zero-knowledge proofs. 