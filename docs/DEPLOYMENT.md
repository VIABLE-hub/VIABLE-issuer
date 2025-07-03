# StudentVC Deployment Guide

## Overview

StudentVC is a multi-tenant verifiable credential platform that can be deployed in various configurations. This guide covers all deployment options.

## Deployment Modes

### Multi-Tenant Deployment (Default)

Runs three separate containers, each serving a different tenant:

- **TUB (TU Berlin)**: Port 8080
- **FUB (FU Berlin)**: Port 8081  
- **ROOT (Default)**: Port 8082

Each tenant has:
- Isolated database
- Custom branding and themes
- Separate cryptographic keys
- Independent configuration

### Single-Tenant Deployment

Runs only one specific tenant for simpler deployments or development:

```bash
# Deploy only TU Berlin tenant
SINGLE_TENANT=tub ./deploy.sh

# Deploy only FU Berlin tenant  
SINGLE_TENANT=fub ./deploy.sh

# Deploy only Root tenant
SINGLE_TENANT=root ./deploy.sh
```

## Prerequisites

1. **Docker** (v20.10+)
   - Installation: https://docs.docker.com/get-docker/
   
2. **Docker Compose** (v2.0+)
   - Installation: https://docs.docker.com/compose/install/
   
3. **kubectl** (for Kubernetes deployment)
   - Installation: https://kubernetes.io/docs/tasks/tools/

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd stvc
```

### 2. Configure Environment

```bash
# Copy environment template
cp deployment.env .env

# Edit with your settings
nano .env
```

Key settings to configure:
- `TUB_NGROK_URL`: NGROK URL for TU Berlin tenant
- `FUB_NGROK_URL`: NGROK URL for FU Berlin tenant  
- `ROOT_NGROK_URL`: NGROK URL for Root tenant
- `SECRET_KEY`: Change to a secure random value
- `JWT_SECRET_KEY`: Change to a secure random value

### 3. Deploy

#### Multi-Tenant Docker Compose (Recommended)

```bash
./deploy.sh
```

**Note**: The deployment scripts are now organized in the `deploy/` directory. The root `deploy.sh` is a wrapper that calls `deploy/scripts/deploy.sh`.

#### Single-Tenant Docker Compose

```bash
# Choose one:
SINGLE_TENANT=tub ./deploy.sh    # TU Berlin only
SINGLE_TENANT=fub ./deploy.sh    # FU Berlin only
SINGLE_TENANT=root ./deploy.sh   # Root only
```

#### Kubernetes Deployment

```bash
./deploy.sh kubernetes
```

## Architecture

### Container Structure

```
studentvc-tub     (Port 8080) - TU Berlin tenant
studentvc-fub     (Port 8081) - FU Berlin tenant  
studentvc-root    (Port 8082) - Root/Default tenant
studentvc-nginx   (Port 80)   - Reverse proxy
studentvc-redis   (Port 6379) - Session cache
```

### Data Persistence

Each tenant has isolated data directories:

```
deploy/configs/
├── data/
│   ├── tub/      # TUB database files
│   ├── fub/      # FUB database files
│   └── root/     # ROOT database files
└── static/
    ├── tub/      # TUB static assets
    ├── fub/      # FUB static assets
    └── root/     # ROOT static assets
```

## Deployment Script Details

The `deploy.sh` script performs these steps:

1. **Prerequisites Check**
   - Verifies Docker installation
   - Checks Docker daemon status
   - Validates Docker Compose availability

2. **Directory Setup**
   - Creates data directories for each tenant
   - Creates static asset directories
   - Prepares SSL certificate directory

3. **Environment Configuration**
   - Checks for .env file
   - Copies from template if missing
   - Prompts for configuration review

4. **Container Deployment**
   - Builds Docker images with dependencies
   - Starts containers with proper networking
   - Configures tenant isolation via environment variables

5. **Health Verification**
   - Waits for services to start
   - Checks HTTP endpoints
   - Reports deployment status

6. **Access Information**
   - Displays service URLs
   - Shows monitoring commands
   - Provides shutdown instructions

## Accessing Services

### Web Interface

After deployment, access services at:

- **TU Berlin**: https://localhost:8080
- **FU Berlin**: https://localhost:8081  
- **Root/Default**: https://localhost:8082

### API Endpoints

Each tenant provides:
- `/issuer` - Issue credentials
- `/verifier` - Verify credentials
- `/settings` - Tenant configuration
- `/vcstatus` - Credential status

## Monitoring

### View Logs

```bash
# All services
docker compose -f deploy/configs/docker-compose.yml logs -f

# Specific tenant
docker logs studentvc-tub -f
docker logs studentvc-fub -f
docker logs studentvc-root -f
```

### Check Status

```bash
# Container status
docker ps

# Service health
curl -k https://localhost:8080/health
curl -k https://localhost:8081/health
curl -k https://localhost:8082/health
```

## Management

### Stop Services

```bash
# Stop all services
docker compose -f deploy/configs/docker-compose.yml down

# Stop with volume cleanup
docker compose -f deploy/configs/docker-compose.yml down -v
```

### Restart Services

```bash
# Restart all
docker compose -f deploy/configs/docker-compose.yml restart

# Restart specific tenant
docker restart studentvc-tub
```

### Update Deployment

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose -f deploy/configs/docker-compose.yml up -d --build
```

## Troubleshooting

### Container Won't Start

1. Check logs: `docker logs studentvc-<tenant>`
2. Verify port availability: `lsof -i :8080`
3. Check Docker resources: `docker system df`

### Tenant Shows Wrong Configuration

1. Verify TENANT_ID environment variable is set
2. Check container environment: `docker exec studentvc-tub env | grep TENANT`
3. Restart container after configuration changes

### SSL Certificate Errors

- Use `--insecure` flag with curl for testing
- Add proper certificates in `deployment/ssl/` for production

## Production Considerations

### Security

1. Change all default passwords in .env
2. Use proper SSL certificates
3. Configure firewall rules
4. Enable authentication for admin endpoints

### Performance

1. Adjust container resource limits in docker-compose.yml
2. Configure Redis for session persistence
3. Use external database for large deployments

### Backup

1. Backup data directories regularly
2. Export database dumps: `docker exec studentvc-tub sqlite3 /app/data/database.db .dump > backup.sql`
3. Version control configuration files

## Support

For issues or questions:
1. Check container logs
2. Review this documentation
3. Submit issues to repository 