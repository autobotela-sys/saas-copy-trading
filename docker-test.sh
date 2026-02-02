#!/bin/bash
# Quick test script for Docker setup

echo "=========================================="
echo "  SaaS App - Docker Test Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:3445"

echo "1. Checking if API is running..."
if curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is running${NC}"
else
    echo -e "${RED}✗ API is not responding${NC}"
    echo "Please run: docker-compose up -d"
    exit 1
fi

echo ""
echo "2. Testing endpoints..."

# Test root endpoint
echo -n "  - Root endpoint: "
if curl -s -f "$BASE_URL/" | grep -q "Copy Trading"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Test health endpoint
echo -n "  - Health endpoint: "
if curl -s -f "$BASE_URL/health" | grep -q "healthy"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Test API docs
echo -n "  - Swagger docs: "
if curl -s -f "$BASE_URL/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Test OpenAPI JSON
echo -n "  - OpenAPI spec: "
if curl -s -f "$BASE_URL/openapi.json" | grep -q "openapi"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo ""
echo "3. Testing database connection (through API)..."
echo -n "  - Auth endpoint: "
response=$(curl -s -X POST "$BASE_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"Test123!","role":"USER"}')
if echo "$response" | grep -q "email\|exists\|created"; then
    echo -e "${GREEN}✓ Database is connected${NC}"
else
    echo -e "${YELLOW}⚠ Could not verify (may need migration)${NC}"
fi

echo ""
echo "=========================================="
echo "  Quick Test Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Open Swagger UI: $BASE_URL/docs"
echo "  2. Test registration and login"
echo "  3. Follow TESTING_GUIDE.md for full tests"
echo ""
