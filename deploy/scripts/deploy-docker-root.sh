#!/bin/bash

# Deploy ROOT tenant only with Docker Compose
# This script starts only the ROOT/Default tenant on port 8082

set -e

echo "======================================"
echo "  Deploying ROOT Tenant Only         "
echo "======================================"
echo ""
echo "Starting ROOT tenant on port 8082"
echo ""

# Check Docker
if ! docker info &> /dev/null; then
    echo "[ERROR] Docker daemon is not running. Please start Docker."
    exit 1
fi

# Create data directories
mkdir -p ../configs/data/root
mkdir -p ../configs/static/root

# Deploy only ROOT service with Redis
cd ../configs
docker compose up -d studentvc-root redis

echo ""
echo "======================================"
echo "        DEPLOYMENT COMPLETE           "
echo "======================================"
echo ""
echo "Access URL:"
echo "  Root/Default: https://localhost:8082"
echo ""
echo "View logs: docker logs studentvc-root -f"
echo "Stop: docker compose -f ../configs/docker-compose.yml stop studentvc-root" 