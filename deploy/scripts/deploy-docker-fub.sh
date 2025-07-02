#!/bin/bash

# Deploy FUB tenant only with Docker Compose
# This script starts only the FU Berlin tenant on port 8081

set -e

echo "======================================"
echo "  Deploying FUB Tenant Only          "
echo "======================================"
echo ""
echo "Starting FU Berlin tenant on port 8081"
echo ""

# Check Docker
if ! docker info &> /dev/null; then
    echo "[ERROR] Docker daemon is not running. Please start Docker."
    exit 1
fi

# Create data directories
mkdir -p ../configs/data/fub
mkdir -p ../configs/static/fub

# Deploy only FUB service with Redis
cd ../configs
docker compose up -d studentvc-fub redis

echo ""
echo "======================================"
echo "        DEPLOYMENT COMPLETE           "
echo "======================================"
echo ""
echo "Access URL:"
echo "  FU Berlin: https://localhost:8081"
echo ""
echo "View logs: docker logs studentvc-fub -f"
echo "Stop: docker compose -f ../configs/docker-compose.yml stop studentvc-fub" 