# NGROK Setup for Veritas Tenant

## Quick Start Guide

### 1. Start Veritas Tenant
```bash
make dev-veritas
```

The server will start on:
- **Local network**: `https://192.168.178.156:8080`
- **Localhost**: `https://localhost:8080`

### 2. Configure NGROK for External Wallet Access

#### Option A: Via Web UI (Recommended)
1. Navigate to **Settings** → **Network** tab
2. In the **Connection Mode** section, select **NGROK**
3. Enter your NGROK domain (e.g., `abc123.ngrok-free.app`)
4. Click **Save Settings**
5. Test the connection using the **Test Connection** button

#### Option B: Via API
```bash
curl -X POST https://localhost:8080/api/network \
  -H "Content-Type: application/json" \
  -d '{
    "use_ngrok": true,
    "ngrok_url": "https://your-domain.ngrok-free.app",
    "connection_mode": "ngrok"
  }'
```

### 3. Start NGROK Tunnel

```bash
# Using ngrok command
ngrok http 8080

# Or with a specific domain (if you have a paid plan)
ngrok http 8080 --domain=your-domain.ngrok-free.app
```

### 4. Verify Configuration

Check that your NGROK URL is working:
- **Issuer endpoint**: `https://your-domain.ngrok-free.app/issuer`
- **Verifier endpoint**: `https://your-domain.ngrok-free.app/verifier`
- **Well-known config**: `https://your-domain.ngrok-free.app/.well-known/openid-credential-issuer`

### 5. Connect External Wallet

1. Open your wallet app (e.g., StudentWallet iOS app)
2. Scan the QR code from the Issuer page
3. The wallet will connect via the NGROK URL
4. Accept and store the credential

## Configuration Persistence

All NGROK settings are automatically saved to the Veritas tenant database:
- **Database location**: `backend/src/tenants/instances/veritas/database.db`
- **Settings table**: `tenant_settings`

Your NGROK configuration will persist across server restarts.

## Troubleshooting

### NGROK URL not working
1. Verify NGROK tunnel is running: `ngrok status`
2. Check the Settings page shows correct NGROK domain
3. Test connection using the **Test Connection** button in Settings

### Wallet can't connect
1. Ensure NGROK URL is publicly accessible
2. Check that NGROK free plan allows the required traffic
3. Verify the QR code contains the NGROK URL (not localhost)

### Settings not saving
1. Check browser console for errors
2. Verify tenant ID is correct: should be `veritas`
3. Check database write permissions

## Features

✅ **Real-time Updates**: NGROK URL updates without server restart  
✅ **Tenant Isolation**: Each tenant has separate NGROK configuration  
✅ **Automatic QR Codes**: QR codes automatically use NGROK URL when configured  
✅ **Connection Testing**: Built-in connection test in Settings  
✅ **Persistent Storage**: Configuration saved to tenant database  

## Development Tips

### Local Development with WiFi
If you're on the same network as your mobile device, you can use the local IP without NGROK:
- Use: `https://192.168.178.156:8080`
- This is faster and doesn't require NGROK

### NGROK Free vs Paid
- **Free**: Temporary URLs, session limits
- **Paid**: Custom domains, higher limits, better for production

## Related Documentation

- Main README: `/README.md`
- Tenant System: `/docs/PERFECT_TENANT_IMPLEMENTATION_GUIDE.md`
- Network Configuration: `/backend/src/settings/network_api.py`

