# 🎓 VERITAS - Verifiable Credential Platform

**VERITAS** is a comprehensive, multi-tenant platform for issuing, managing, and verifying digital credentials using **BBS+ selective disclosure** and **zero-knowledge proofs**.

---

## 📖 What is VERITAS?

VERITAS is a **production-ready credential platform** that provides:

- 🔐 **Privacy-preserving credential issuance** with BBS+ signatures
- 🎯 **Selective disclosure** - users choose which information to share
- 🏢 **Multi-tenant architecture** - isolated instances per organization
- 🔌 **Plugin system** - extensible architecture for custom integrations
- 📱 **Mobile wallet integration** - QR code-based credential exchange
- 🌐 **OID4VC/OID4VP compliance** - industry-standard protocols

---

## 🎓 StudentVC: An Instance of VERITAS

**StudentVC** is a specific deployment of the VERITAS platform, configured for **educational institutions** to issue digital student credentials.

### StudentVC Features

- **University credential issuance** - Issue verifiable student credentials
- **Multi-tenant support** - Multiple universities on one platform
  - `root` - Default tenant
  - `tuberlin` - TU Berlin
  - `fuberlin` - FU Berlin  
  - `veritas` - Veritas University
- **VC-based authentication** - Login with verifiable credentials
- **Credential lifecycle management** - Issue, verify, revoke, re-enable
- **Selective disclosure** - Students control what information to share

### Relationship to VERITAS

```
VERITAS (Platform)
    └── StudentVC (Instance)
        ├── Tenant: root
        ├── Tenant: tuberlin
        ├── Tenant: fuberlin
        └── Tenant: veritas
```

**VERITAS** provides the core infrastructure:
- Multi-tenant architecture
- BBS+ cryptographic operations
- Plugin system (`VeritasPlugin`)
- Blueprint-based routing
- Credential verification engine

**StudentVC** is a configured instance:
- Educational credential templates
- University-specific branding
- Student-focused workflows
- Academic use cases

---

## 🏗️ Architecture Overview

### Core Components

```
backend/src/
├── issuer/              # Credential issuance engine
├── verifier/            # Credential verification engine
├── tenants/             # Multi-tenant management
├── settings/            # Configuration management
├── auth/                # Authentication system
├── vc_auth/             # VC-based login
├── validate/            # Credential validation
├── plugin_system/       # Extensible plugin architecture
└── models.py            # Database models
```

### Multi-Tenant System

Each tenant operates in complete isolation:

- **Database**: `tenants/instances/{tenant_id}/database.db`
- **Keys**: `tenants/instances/{tenant_id}/keys/`
- **Config**: `tenants/instances/{tenant_id}/config.json`
- **Branding**: Tenant-specific logos, colors, fonts

### Plugin System

VERITAS includes a powerful plugin system for extensibility:

```python
from backend.src.plugin_system import VeritasPlugin

class MyPlugin(VeritasPlugin):
    def initialize(self) -> bool:
        # Plugin initialization
        return True
    
    def get_metadata(self) -> PluginMetadata:
        # Plugin metadata
        pass
```

**Plugin Types:**
- `STORAGE` - Blockchain, IPFS, distributed storage
- `VERIFICATION` - Custom verification logic
- `CONSENSUS` - Distributed consensus mechanisms
- `ANALYTICS` - Data analytics
- `NOTIFICATION` - Notification systems

---

## 🔐 Cryptographic Foundation

### BBS+ Signatures

VERITAS uses **BBS+ signatures** for privacy-preserving credentials:

1. **Issuer** signs the full credential with BBS+ private key
2. **Holder** creates zero-knowledge proof revealing only selected fields
3. **Verifier** verifies proof with BBS+ public key

**Benefits:**
- ✅ Selective disclosure
- ✅ Unlinkability (each presentation is unique)
- ✅ Zero-knowledge proofs
- ✅ Privacy-preserving verification

### Key Management

Each tenant has isolated cryptographic keys:

- **BBS+ Keys**: For credential signing and selective disclosure
- **JWT Keys**: For transport security and issuer authentication
- **DID**: Decentralized identifier for each tenant

---

## 🚀 Quick Start

### Running StudentVC Instance

```bash
# Start with root tenant
make dev-root

# Start with TU Berlin tenant
make dev-tub

# Start with FU Berlin tenant
make dev-fub

# Start with Veritas tenant
make dev-veritas
```

### Access Points

- **Issuer**: `https://localhost:8080/{tenant}/issuer`
- **Verifier**: `https://localhost:8080/{tenant}/verifier`
- **VC Status**: `https://localhost:8080/{tenant}/vcstatus`
- **Settings**: `https://localhost:8080/{tenant}/settings`
- **VC Login**: `https://localhost:8080/{tenant}/vc-auth/login`

---

## 📁 Key Directories

### `issuer/`
Credential issuance engine:
- OID4VC metadata generation
- Dynamic QR code creation
- Credential signing with BBS+
- Multi-tenant credential templates

### `verifier/`
Credential verification engine:
- OID4VP presentation requests
- Selective disclosure handling
- BBS+ proof verification
- Real-time WebSocket updates

### `tenants/`
Multi-tenant management:
- Tenant detection and routing
- Isolated database per tenant
- Tenant-specific configuration
- Branding and customization

### `plugin_system/`
Extensible plugin architecture:
- `VeritasPlugin` base class
- Plugin loader and registry
- Event bus for plugin communication
- Tenant-aware plugin instances

### `auth/` & `vc_auth/`
Authentication systems:
- Traditional Flask-Login (`auth/`)
- VC-based authentication (`vc_auth/`)
- Session management
- Multi-tenant user isolation

---

## 🔌 Extending VERITAS

### Creating a Plugin

1. **Inherit from VeritasPlugin**:
```python
from backend.src.plugin_system import VeritasPlugin, PluginMetadata, PluginType

class MyStoragePlugin(VeritasPlugin):
    def initialize(self) -> bool:
        # Your initialization logic
        return True
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="My Storage Plugin",
            version="1.0.0",
            author="Your Name",
            description="Custom storage backend",
            plugin_type=PluginType.STORAGE,
            dependencies=[]
        )
```

2. **Register the plugin** in your tenant configuration

3. **Enable per tenant** via settings

### Creating a New Instance

To create a new VERITAS instance (like StudentVC):

1. Configure tenant in `studentVC.jsonl`
2. Create tenant instance directory: `tenants/instances/{tenant_id}/`
3. Generate keys: `make generate-keys TENANT_ID={tenant_id}`
4. Configure branding and settings
5. Start instance: `make dev-{tenant_id}`

---

## 🧪 Testing

```bash
# Run all tests
make test

# Test specific tenant
TENANT_ID=veritas make test

# Test startup
make test-startup
```

---

## 📚 Documentation

- **Architecture**: See `BLUEPRINT_STRUCTURE.md` for routing details
- **Deployment**: See `../../docs/DEPLOYMENT_GUIDE.md`
- **API Reference**: See `../../docs/api/`
- **Student Guide**: See `../../docs/STUDENT_IMPLEMENTATION_GUIDE.md`

---

## 🎯 VERITAS vs StudentVC

| Aspect | VERITAS (Platform) | StudentVC (Instance) |
|--------|-------------------|---------------------|
| **Purpose** | Generic credential platform | Educational credentials |
| **Scope** | Any credential use case | Student credentials only |
| **Tenants** | Configurable | Universities |
| **Templates** | Extensible | Academic-focused |
| **Branding** | Tenant-configurable | University branding |
| **Plugins** | Full plugin system | Educational plugins |

---

## 💡 Use Cases

VERITAS can be configured for various credential use cases:

- 🎓 **Education** (StudentVC) - Student credentials, diplomas
- 🏥 **Healthcare** - Medical licenses, certifications
- 🏢 **Corporate** - Employee badges, training certificates
- 🚗 **Transportation** - Driver licenses, vehicle registrations
- 🏛️ **Government** - Identity documents, permits

Each use case is a **VERITAS instance** with tenant-specific configuration.

---

## 🔒 Security & Privacy

- **BBS+ Signatures**: Zero-knowledge proofs for privacy
- **Selective Disclosure**: Users control data sharing
- **Multi-Tenant Isolation**: Complete data separation
- **Key Management**: Per-tenant cryptographic keys
- **DID-based Identity**: Decentralized identifiers

---

## 📞 Support

For VERITAS platform questions:
- Review architecture docs in `../../docs/`
- Check plugin system examples in `plugin_system/`
- Review tenant configuration in `tenants/`

For StudentVC-specific questions:
- See `../../README.md` for StudentVC documentation
- Review tenant instances in `tenants/instances/`

---

**VERITAS** - Building trust through verifiable credentials 🚀

