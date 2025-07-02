# Mobile Wallet Server Configuration Guide

## Overview

Mobile wallets require HTTPS connections and publicly accessible URLs. While ngrok is great for development, production servers need proper configuration.

## Production Configuration Options

### Option 1: Direct Domain with SSL (Recommended)

#### Requirements
- A domain name (e.g., studentvc.university.edu)
- SSL certificate (Let's Encrypt or commercial)
- Public IP address or cloud hosting

#### Configuration Steps

1. **Domain Setup**
   ```bash
   # Point your domain to your server IP
   # DNS A Records:
   studentvc.example.com     → Your-Server-IP
   tub.studentvc.example.com → Your-Server-IP
   fub.studentvc.example.com → Your-Server-IP
   ```

2. **SSL Certificate with Let's Encrypt**
   ```bash
   # Install certbot
   sudo apt-get update
   sudo apt-get install certbot python3-certbot-nginx

   # Generate certificates
   sudo certbot certonly --standalone -d studentvc.example.com
   sudo certbot certonly --standalone -d tub.studentvc.example.com
   sudo certbot certonly --standalone -d fub.studentvc.example.com
   ```

3. **Update NGINX Configuration**
   ```nginx
   # /etc/nginx/sites-available/studentvc
   server {
       listen 443 ssl;
       server_name studentvc.example.com;
       
       ssl_certificate /etc/letsencrypt/live/studentvc.example.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/studentvc.example.com/privkey.pem;
       
       location / {
           proxy_pass https://localhost:8082;  # ROOT tenant
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-Proto https;
       }
   }

   # TUB tenant
   server {
       listen 443 ssl;
       server_name tub.studentvc.example.com;
       
       ssl_certificate /etc/letsencrypt/live/tub.studentvc.example.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/tub.studentvc.example.com/privkey.pem;
       
       location / {
           proxy_pass https://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-Proto https;
       }
   }
   ```

4. **Update Environment Configuration**
   ```bash
   # .env file
   TUB_PUBLIC_URL=https://tub.studentvc.example.com
   FUB_PUBLIC_URL=https://fub.studentvc.example.com
   ROOT_PUBLIC_URL=https://studentvc.example.com
   ```

### Option 2: Reverse Proxy with Cloudflare

#### Benefits
- Free SSL certificates
- DDoS protection
- Global CDN
- Hide server IP

#### Setup
1. Add domain to Cloudflare
2. Enable "Full (strict)" SSL mode
3. Create DNS records pointing to your server
4. Use Cloudflare Origin certificates

### Option 3: Cloud Provider Load Balancer

#### AWS Application Load Balancer
```bash
# Configure ALB with SSL termination
# Target groups for each tenant:
# - TUB → Port 8080
# - FUB → Port 8081
# - ROOT → Port 8082
```

#### Google Cloud Load Balancer
```bash
# Similar setup with SSL certificates
# Backend services for each tenant
```

## Server-Side Configuration

### 1. Update Flask Application

```python
# backend/src/utils.py
def get_server_url():
    """Get the public server URL for mobile wallet access"""
    # Check environment variable first
    public_url = os.environ.get('PUBLIC_URL')
    if public_url:
        return public_url
    
    # For production domains
    if request:
        return f"https://{request.host}"
    
    # Fallback
    return "https://localhost:8080"
```

### 2. Configure Tenant URLs

```python
# backend/src/settings/tenant_config.py
TENANT_URLS = {
    'tub': os.environ.get('TUB_PUBLIC_URL', 'https://tub.studentvc.example.com'),
    'fub': os.environ.get('FUB_PUBLIC_URL', 'https://fub.studentvc.example.com'),
    'root': os.environ.get('ROOT_PUBLIC_URL', 'https://studentvc.example.com')
}
```

### 3. Update Docker Compose

```yaml
# deployment/docker-compose.yml
services:
  studentvc-tub:
    environment:
      - PUBLIC_URL=${TUB_PUBLIC_URL}
      - TENANT_ID=tub
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.tub.rule=Host(`tub.studentvc.example.com`)"
      - "traefik.http.routers.tub.tls=true"
```

## Network Configuration

### Firewall Rules
```bash
# Allow HTTPS
sudo ufw allow 443/tcp

# Allow HTTP (for Let's Encrypt validation)
sudo ufw allow 80/tcp

# If using Docker
sudo ufw allow 8080:8082/tcp
```

### Security Headers
```nginx
# Add to nginx configuration
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Access-Control-Allow-Origin "capacitor://localhost" always;
```

## Mobile Wallet Configuration

### Update Wallet URLs
```swift
// iOS Wallet Configuration
struct ServerConfig {
    static let baseURL = "https://studentvc.example.com"
    static let tubURL = "https://tub.studentvc.example.com"
    static let fubURL = "https://fub.studentvc.example.com"
}
```

### Certificate Pinning (Optional)
```swift
// For additional security
let pinnedCertificates = [
    "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
]
```

## Testing Production Configuration

### 1. SSL Certificate Validation
```bash
# Test SSL configuration
openssl s_client -connect studentvc.example.com:443 -servername studentvc.example.com
```

### 2. Mobile Wallet Connection Test
```bash
# Test credential offer endpoint
curl -k https://studentvc.example.com/issuer/.well-known/openid-credential-issuer
```

### 3. QR Code Generation
- Ensure QR codes contain public HTTPS URLs
- Test scanning with actual mobile device

## Monitoring

### Health Checks
```bash
# Add monitoring endpoints
curl https://studentvc.example.com/health
curl https://tub.studentvc.example.com/health
curl https://fub.studentvc.example.com/health
```

### SSL Certificate Monitoring
- Set up renewal reminders
- Monitor certificate expiration
- Automate renewal with cron

## Troubleshooting

### Common Issues

1. **Certificate Errors**
   - Verify certificate chain is complete
   - Check certificate matches domain
   - Ensure intermediate certificates included

2. **Connection Refused**
   - Check firewall rules
   - Verify Docker containers running
   - Check NGINX proxy configuration

3. **CORS Issues**
   - Add proper CORS headers
   - Allow capacitor:// origins for mobile

4. **QR Code Not Working**
   - Verify public URL in QR code
   - Check SSL certificate validity
   - Test with curl from mobile network

## Migration from Ngrok

1. **Update Environment Variables**
   ```bash
   # Old (ngrok)
   TUB_NGROK_URL=https://abc123.ngrok.io
   
   # New (production)
   TUB_PUBLIC_URL=https://tub.studentvc.example.com
   ```

2. **Update Application Code**
   - Replace ngrok URL references
   - Use PUBLIC_URL environment variable
   - Update QR code generation

3. **Test Thoroughly**
   - Test all credential issuance flows
   - Verify mobile wallet connections
   - Check all tenant endpoints

## Best Practices

1. **Use Subdomains** for tenant separation
2. **Implement Rate Limiting** to prevent abuse
3. **Enable Access Logs** for debugging
4. **Regular Security Updates**
5. **Backup SSL Certificates**
6. **Monitor Server Resources**
7. **Use CDN** for static assets
8. **Implement Health Checks**

## Example Production Setup Script

```bash
#!/bin/bash
# setup-production.sh

# Install dependencies
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Setup domains
DOMAIN="studentvc.example.com"
TUB_DOMAIN="tub.studentvc.example.com"
FUB_DOMAIN="fub.studentvc.example.com"

# Generate certificates
sudo certbot certonly --standalone -d $DOMAIN
sudo certbot certonly --standalone -d $TUB_DOMAIN
sudo certbot certonly --standalone -d $FUB_DOMAIN

# Configure nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/studentvc
sudo ln -s /etc/nginx/sites-available/studentvc /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Start services
./deploy-docker-all.sh

echo "Production setup complete!"
echo "Access at: https://$DOMAIN"
``` 