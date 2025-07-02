#!/bin/bash

# Deploy TUB tenant only with Docker Compose
# This script starts only the TU Berlin tenant on port 8080

set -e

echo "======================================"
echo "  Deploying TUB Tenant Only          "
echo "======================================"
echo ""
echo "Starting TU Berlin tenant on port 8080"
echo ""

# Check Docker
if ! docker info &> /dev/null; then
    echo "[ERROR] Docker daemon is not running. Please start Docker."
    exit 1
fi

# Create data directories
mkdir -p ../configs/data/tub
mkdir -p ../configs/static/tub

# Deploy only TUB service with Redis
cd ../configs
docker compose up -d studentvc-tub redis

echo ""
echo "======================================"
echo "        DEPLOYMENT COMPLETE           "
echo "======================================"
echo ""
echo "Access URL:"
echo "  TU Berlin: https://localhost:8080"
echo ""
echo "View logs: docker logs studentvc-tub -f"
echo "Stop: docker compose -f ../configs/docker-compose.yml stop studentvc-tub" 