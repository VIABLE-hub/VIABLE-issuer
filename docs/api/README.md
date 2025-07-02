# StudentVC API Documentation

## Overview
This section contains detailed API documentation for all StudentVC endpoints.

## Available APIs

### 🎓 [Issuer API](./issuer/)
Handles credential issuance, student registration, and credential management.

**Key Endpoints:**
- `POST /issuer/issue` - Issue new credentials
- `GET /issuer/status` - Check issuer status
- `POST /issuer/register` - Register new students

### 🔍 [Verifier API](./verifier/)
Handles credential verification and presentation requests.

**Key Endpoints:**
- `POST /verifier/verify` - Verify credentials
- `GET /verifier/request` - Get presentation requests
- `POST /verifier/callback` - Handle verification callbacks

### ⚙️ [Settings API](./settings/)
System configuration and network settings management.

**Key Endpoints:**
- `GET /settings/network` - Network configuration
- `POST /settings/update` - Update settings
- `GET /settings/system` - System status

### 📊 [VC Status API](./vcstatus/)
Credential status tracking and revocation management.

**Key Endpoints:**
- `GET /vcstatus/{id}` - Check credential status
- `POST /vcstatus/revoke` - Revoke credentials
- `GET /vcstatus/list` - List credential statuses

## Authentication
All API endpoints require proper authentication headers. See individual API documentation for details.

## Response Format
All APIs return JSON responses with consistent error handling and status codes. 