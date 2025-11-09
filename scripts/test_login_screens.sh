#!/bin/bash

# Test Login Screens for All Tenants
# This script verifies that login screens are accessible for all tenants

echo "🎨 Testing Login Screens for All Tenants"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test a tenant login page
test_tenant_login() {
    local tenant_name=$1
    local port=$2
    local url="https://localhost:${port}/login"
    
    echo -e "${YELLOW}Testing ${tenant_name} (Port ${port})...${NC}"
    
    # Test if server is running
    if curl -k -s --max-time 5 "${url}" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ${tenant_name} login page is accessible at ${url}${NC}"
        return 0
    else
        echo -e "${RED}❌ ${tenant_name} login page is NOT accessible${NC}"
        echo "   Make sure the server is running: make dev-${tenant_name,,}"
        return 1
    fi
}

echo "Prerequisites:"
echo "- Servers must be running on their respective ports"
echo "- Use 'make dev-root', 'make dev-tub', etc. to start servers"
echo ""

# Test each tenant
test_tenant_login "Root" "8080"
echo ""

test_tenant_login "TUB" "8081"
echo ""

test_tenant_login "FUB" "8082"
echo ""

test_tenant_login "Veritas" "8083"
echo ""

echo "=========================================="
echo "Test Complete!"
echo ""
echo "To start each tenant:"
echo "  make dev-root    # Port 8080"
echo "  make dev-tub     # Port 8081"
echo "  make dev-fub     # Port 8082"
echo "  make dev-veritas # Port 8083"
echo ""
echo "Access login pages in browser:"
echo "  https://localhost:8080/login (Root)"
echo "  https://localhost:8081/login (TU Berlin)"
echo "  https://localhost:8082/login (FU Berlin)"
echo "  https://localhost:8083/login (Veritas)"

