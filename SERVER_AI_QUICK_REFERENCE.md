# 🚨 SERVER AI - Quick Reference Card

## ⚡ **IMMEDIATE HEALTH CHECK**
```bash
# 1. Container Status
docker compose ps
# Expected: All 5 containers "Up" and "healthy"

# 2. Service Endpoints  
curl -k https://tub.85-215-156-198.sslip.io/health
curl -k https://fub.85-215-156-198.sslip.io/health
curl -k https://root.85-215-156-198.sslip.io/health
# Expected: HTTP 200 for all

# 3. Tenant Routing
curl -s https://tub.85-215-156-198.sslip.io/ | grep -i "tu berlin"
curl -s https://fub.85-215-156-198.sslip.io/ | grep -i "fu berlin"  
curl -s https://root.85-215-156-198.sslip.io/ | grep -i "root"
# Expected: Each returns tenant-specific content
```

## 🔥 **EMERGENCY FIXES**

### **Problem: All subdomains show same content**
```bash
# Check nginx config
grep "server_name" /etc/nginx/nginx.conf
# Should show: tub.85-215-156-198.sslip.io, fub.85-215-156-198.sslip.io, root.85-215-156-198.sslip.io

# Fix: Update nginx config
sudo cp /path/to/studentvc/deploy/configs/nginx-production.conf /etc/nginx/nginx.conf
sudo nginx -t && sudo systemctl reload nginx
```

### **Problem: Containers unhealthy/down**
```bash
# Emergency restart
docker compose down
docker compose up -d --build

# If still failing
docker system prune -f
docker compose up -d --build --force-recreate
```

### **Problem: Wrong URLs in credential offers**
```bash
# Check environment variables
docker exec studentvc-tub printenv | grep EXTERNAL_SERVER_URL
# Should be: https://tub.85-215-156-198.sslip.io

# Fix: Update environment
cp deploy/configs/docker.env.production deploy/configs/docker.env
docker compose down && docker compose up -d
```

### **Problem: SSL certificate errors**
```bash
# Check certificates
sudo certbot certificates
# Should show valid certs for all 3 subdomains

# Renew if expired
sudo certbot renew
sudo systemctl reload nginx
```

## 🎯 **SUCCESS INDICATORS**
- ✅ 5/5 containers running and healthy
- ✅ Each subdomain serves correct tenant content
- ✅ SSL certificates valid for all domains
- ✅ Health endpoints return HTTP 200
- ✅ Credential offers use correct subdomain URLs

## 📊 **KEY METRICS**
- **Response Time**: < 500ms
- **Memory Usage**: < 2GB total
- **CPU Usage**: < 10%
- **SSL**: Valid Let's Encrypt certificates
- **Uptime**: 99.9% target

## 📞 **ESCALATION**
1. **Level 1**: Container restart (`docker compose restart`)
2. **Level 2**: Configuration fix (nginx, env vars)
3. **Level 3**: Code debugging (logs analysis)
4. **Level 4**: Infrastructure (server resources) 