#!/bin/bash

# Deploy all StudentVC tenants with Docker Compose
# This script starts all three tenants: TUB, FUB, and ROOT

set -e

echo "======================================"
echo "  Deploying All StudentVC Tenants    "
echo "======================================"
echo ""
echo "Starting multi-tenant deployment:"
echo "  - TUB (TU Berlin) on port 8080"
echo "  - FUB (FU Berlin) on port 8081"
echo "  - ROOT (Default) on port 8082"
echo ""

# Check Docker
if ! docker info &> /dev/null; then
    echo "[ERROR] Docker daemon is not running. Please start Docker."
    exit 1
fi

# Create data directories
mkdir -p ../configs/data/{tub,fub,root}
mkdir -p ../configs/static/{tub,fub,root}

# Deploy all services
cd ../configs
docker compose up -d --build

echo ""
echo "======================================"
echo "        DEPLOYMENT COMPLETE           "
echo "======================================"
echo ""
echo "Access URLs:"
echo "  TU Berlin: https://localhost:8080"
echo "  FU Berlin: https://localhost:8081"
echo "  Root/Default: https://localhost:8082"
echo ""
echo "View logs: docker compose -f ../configs/docker-compose.yml logs -f"
echo "Stop all: docker compose -f ../configs/docker-compose.yml down" 