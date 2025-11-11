# Veritas University Tenant

This directory contains the configuration and resources for the Veritas University tenant.

## Directory Structure

```
veritas/
├── config.py           # Python configuration class
├── config.json         # JSON configuration file
├── __init__.py         # Module initialization
├── static/             # Tenant-specific static assets
│   └── veritas-logo.png  # University logo (placeholder - replace with actual logo)
├── keys/               # Cryptographic keys (auto-generated)
├── backups/            # Database backups
└── database.db         # Tenant-specific database (auto-created)
```

## Starting Veritas Tenant

To start the StudentVC application with the Veritas tenant:

```bash
# Using Makefile (recommended)
make dev-veritas

# Or using environment variable directly
cd backend
TENANT_ID=veritas ../test_env/bin/python main.py --host 0.0.0.0 --port 8080
```

## Configuration

The Veritas tenant uses the following configuration:

- **Primary Color**: `#003f7f` (Berlin Blue)
- **Accent Color**: `#4A90E2` (Light Blue)
- **Domain Patterns**: `veritas`, `veritas-university`

## Customization

### Logo
Replace `static/veritas-logo.png` with your actual Veritas University logo. The logo should be:
- Format: PNG with transparency
- Recommended size: 200x200 pixels or larger
- Used in: Header, credential branding, QR codes

### Colors
Edit `config.py` to customize the theme colors:
- `primary_color`: Main university color
- `accent_color`: Secondary color for accents
- `text_color`: Text color on colored backgrounds

### Settings & ngrok URL
1. Start the tenant: `make dev-veritas`
2. Navigate to: `https://localhost:8080/settings`
3. Configure your ngrok URL and other settings
4. Settings are stored in the tenant-specific database

## Database

Each tenant has its own isolated database:
- Location: `backend/src/tenants/instances/veritas/database.db`
- Backups: Stored in `backups/` directory
- Schema: Automatically created on first startup

## Keys

Cryptographic keys are stored in the `keys/` directory:
- `issuer_private_key.pem` - Issuer signing key
- `issuer_public_key.pem` - Issuer verification key
- `bbs_private_key.pem` - BBS+ credential key

Keys are auto-generated on first use and should be kept secure.

## Troubleshooting

### Tenant not loading
- Verify `TENANT_ID=veritas` environment variable is set
- Check logs for tenant registration errors
- Ensure all files in this directory are present

### Logo not showing
- Verify `static/veritas-logo.png` exists and is a valid PNG
- Check file permissions (should be readable)
- Clear browser cache and reload

### Settings not persisting
- Check database file exists and is writable
- Verify tenant detection is working (check logs)
- Ensure you're accessing the correct tenant URL

## Support

For issues specific to the Veritas tenant configuration, check:
1. Application logs: `instance/service.log`
2. Tenant registry: Verify tenant is registered in `setup.py`
3. Database: Ensure `database.db` was created successfully

