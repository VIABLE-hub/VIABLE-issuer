# Quick Start: Production Server for Mobile Wallets

## Simple Production Setup (10 minutes)

### Prerequisites
- Ubuntu/Debian server with public IP
- Domain name pointing to your server
- Root/sudo access

### Step 1: Point Domain to Server
```bash
# Add DNS A records at your domain provider:
studentvc.yourdomain.com → Your-Server-IP
```

### Step 2: Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose nginx certbot python3-certbot-nginx
```

### Step 3: Get SSL Certificate
```bash
# Get free Let's Encrypt certificate
sudo certbot --nginx -d studentvc.yourdomain.com
```

### Step 4: Configure NGINX
```bash
sudo nano /etc/nginx/sites-available/studentvc
```

Add this configuration:
```nginx
server {
    listen 443 ssl;
    server_name studentvc.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/studentvc.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/studentvc.yourdomain.com/privkey.pem;
    
    # Route to different tenants based on path
    location /tub {
        proxy_pass https://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }
    
    location /fub {
        proxy_pass https://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }
    
    location / {
        proxy_pass https://localhost:8082;  # Default ROOT
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }
}

# HTTP redirect to HTTPS
server {
    listen 80;
    server_name studentvc.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Step 5: Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/studentvc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Update Environment
```bash
# Create .env file
cat > .env << EOF
# Public URLs for mobile wallet access
TUB_PUBLIC_URL=https://studentvc.yourdomain.com/tub
FUB_PUBLIC_URL=https://studentvc.yourdomain.com/fub
ROOT_PUBLIC_URL=https://studentvc.yourdomain.com

# Other settings
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF
```

### Step 7: Deploy StudentVC
```bash
# Clone repository
git clone https://github.com/yourusername/stvc.git
cd stvc

# Deploy all tenants
./deploy-docker-all.sh
```

### Step 8: Test Mobile Wallet Access
```bash
# Test endpoints
curl https://studentvc.yourdomain.com/health
curl https://studentvc.yourdomain.com/issuer/.well-known/openid-credential-issuer
```

## Mobile Wallet URLs

Your mobile wallets can now connect to:
- **Root**: `https://studentvc.yourdomain.com`
- **TUB**: `https://studentvc.yourdomain.com/tub`
- **FUB**: `https://studentvc.yourdomain.com/fub`

## Comparison: Ngrok vs Production

| Feature | Ngrok (Development) | Production Server |
|---------|-------------------|-------------------|
| URL | `https://random.ngrok.io` | `https://studentvc.yourdomain.com` |
| SSL | Ngrok managed | Let's Encrypt (free) |
| Stability | Changes on restart | Permanent |
| Performance | Limited bandwidth | Full server capacity |
| Cost | Free tier limited | Server costs only |
| Security | Ngrok proxy | Direct control |

## Alternative: Keep Using Ngrok Features

If you like ngrok's features, you can use **Cloudflare Tunnel** (free):

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create studentvc

# Run tunnel
cloudflared tunnel run --url https://localhost:8080 studentvc
```

Benefits:
- No port forwarding needed
- Free subdomain from Cloudflare
- Built-in DDoS protection
- Works behind firewall/NAT

## Security Checklist

- [ ] SSL certificate installed and auto-renewing
- [ ] Firewall configured (only allow 80/443)
- [ ] Strong passwords in .env file
- [ ] Regular security updates
- [ ] Backup configuration
- [ ] Monitor server logs
- [ ] Rate limiting configured

## Common Issues

**Mobile wallet can't connect:**
- Check SSL certificate is valid
- Verify domain resolves correctly
- Test with curl from another network
- Check firewall allows HTTPS

**QR code shows localhost:**
- Update PUBLIC_URL environment variables
- Restart Docker containers
- Check nginx proxy headers

**Certificate errors:**
- Ensure full certificate chain
- Check certificate matches domain
- Verify port 443 is open 