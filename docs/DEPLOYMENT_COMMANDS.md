# StudentVC Deployment Commands

## Local Development (Make)

### Run Individual Tenants
```bash
make dev-root    # Start ROOT tenant (default branding) on port 8080
make dev-tub     # Start TUB tenant (TU Berlin) on port 8080  
make dev-fub     # Start FUB tenant (FU Berlin) on port 8080
```

### Run Default (ROOT tenant)
```bash
make dev         # Start default ROOT tenant on port 8080
```

## Docker Deployment

### Deploy All Tenants (Multi-tenant)
```bash
./deploy.sh              # Main wrapper script (recommended)
# OR
deploy/scripts/deploy-docker-all.sh   # Direct script execution
```

This starts:
- TUB on port 8080
- FUB on port 8081  
- ROOT on port 8082

### Deploy Individual Tenants
```bash
# Using main script with environment variable
SINGLE_TENANT=tub ./deploy.sh   # Start only TUB tenant on port 8080
SINGLE_TENANT=fub ./deploy.sh   # Start only FUB tenant on port 8081
SINGLE_TENANT=root ./deploy.sh  # Start only ROOT tenant on port 8082

# OR direct script execution
deploy/scripts/deploy-docker-tub.sh   # Start only TUB tenant on port 8080
deploy/scripts/deploy-docker-fub.sh   # Start only FUB tenant on port 8081
deploy/scripts/deploy-docker-root.sh  # Start only ROOT tenant on port 8082
```

### Using Original Deploy Script
```bash
# Multi-tenant (all 3 tenants)
./deploy.sh

# Single tenant
SINGLE_TENANT=tub ./deploy.sh
SINGLE_TENANT=fub ./deploy.sh
SINGLE_TENANT=root ./deploy.sh
```

## Stop Services

### Local Development
```bash
# Press Ctrl+C in terminal
# Or
make kill-port   # Kill process on port 8080
```

### Docker
```bash
# Stop all
docker compose -f deploy/configs/docker-compose.yml down

# Stop individual
docker stop studentvc-tub
docker stop studentvc-fub
docker stop studentvc-root
```

## View Logs

### Docker
```bash
# All services
docker compose -f deploy/configs/docker-compose.yml logs -f

# Individual tenant
docker logs studentvc-tub -f
docker logs studentvc-fub -f
docker logs studentvc-root -f
```

## Quick Reference

| Command | Type | Tenant | Port |
|---------|------|--------|------|
| `make dev-root` | Local | ROOT | 8080 |
| `make dev-tub` | Local | TUB | 8080 |
| `make dev-fub` | Local | FUB | 8080 |
| `./deploy.sh` | Docker | ALL | 8080,8081,8082 |
| `SINGLE_TENANT=tub ./deploy.sh` | Docker | TUB | 8080 |
| `SINGLE_TENANT=fub ./deploy.sh` | Docker | FUB | 8081 |
| `SINGLE_TENANT=root ./deploy.sh` | Docker | ROOT | 8082 | 