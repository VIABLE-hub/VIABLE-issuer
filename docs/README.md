# StudentVC Documentation

## Overview
StudentVC is a production-ready Verifiable Credentials system for educational institutions, providing secure digital identity management for students.

## Documentation Structure

### 📚 API Documentation
- [Issuer API](./api/issuer/) - Credential issuance endpoints
- [Verifier API](./api/verifier/) - Credential verification endpoints  
- [Settings API](./api/settings/) - System configuration endpoints
- [VC Status API](./api/vcstatus/) - Credential status management

### 🛠️ Development Documentation
- [Getting Started](./development/README.md) - Setup and development guide
- [Troubleshooting](./development/troubleshooting/) - Common issues and solutions
- [Deployment](./development/deployment/) - Production deployment guides
- [Testing](./development/testing/) - Test suite documentation

## Quick Start

```bash
# Setup environment
make setup

# Start development server
make dev

# Access the application
https://localhost:8080
```

## Project Structure

```
├── backend/          # Flask backend application
├── mobile/ios/       # iOS wallet application
├── tests/            # Test suites
├── docs/             # Documentation
├── scripts/          # Development scripts
└── config/           # Configuration files
``` 