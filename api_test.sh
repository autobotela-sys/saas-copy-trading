#!/bin/bash
API="http://localhost:3445"

echo "=================================="
echo "  SaaS API Test Suite"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
PASS=0
FAIL=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local token="$5"
    
    echo -n "Testing: $name ... "
    
    if [ -z "$token" ]; then
        response=$(curl -s -X "$method" "$API$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    else
        response=$(curl -s -X "$method" "$API$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data" 2>&1)
    fi
    
    if echo "$response" | grep -q "error\|Error\|Internal Server Error\|detail"; then
        echo -e "${RED}FAILED${NC}"
        echo "  Response: $response"
        FAIL=$((FAIL + 1))
    else
        echo -e "${GREEN}OK${NC}"
        PASS=$((PASS + 1))
    fi
}

echo "=== 1. AUTHENTICATION TESTS ==="
echo ""

# Register Admin
test_endpoint "Register Admin" "POST" "/api/auth/register" '{"email":"admin@saas.com","password":"Admin123!","role":"ADMIN"}'

# Register User
test_endpoint "Register User" "POST" "/api/auth/register" '{"email":"user@saas.com","password":"User123!","role":"USER"}'

# Login Admin
ADMIN_TOKEN=$(curl -s -X POST "$API/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@saas.com","password":"Admin123!"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$ADMIN_TOKEN" ]; then
    echo -e "${GREEN}Admin Login: OK${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}Admin Login: FAILED${NC}"
    FAIL=$((FAIL + 1))
fi

# Login User
USER_TOKEN=$(curl -s -X POST "$API/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"user@saas.com","password":"User123!"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$USER_TOKEN" ]; then
    echo -e "${GREEN}User Login: OK${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}User Login: FAILED${NC}"
    FAIL=$((FAIL + 1))
fi

# Get Current User (Admin)
test_endpoint "Get Admin Profile" "GET" "/api/auth/me" "" "$ADMIN_TOKEN"

# Get Current User (User)
test_endpoint "Get User Profile" "GET" "/api/auth/me" "" "$USER_TOKEN"

echo ""
echo "=== 2. TRADING PROFILE TESTS ==="
echo ""

# Create Trading Profile
test_endpoint "Create Trading Profile" "POST" "/api/users/me/trading-profile" '{"lot_size_multiplier":"2X","risk_profile":"MODERATE","max_loss_per_day":5000}' "$USER_TOKEN"

# Get Trading Profile
test_endpoint "Get Trading Profile" "GET" "/api/users/me/trading-profile" "" "$USER_TOKEN"

echo ""
echo "=== 3. ADMIN TESTS ==="
echo ""

# List All Users
test_endpoint "List All Users" "GET" "/api/admin/users" "" "$ADMIN_TOKEN"

echo ""
echo "=== 4. BROKER TESTS ==="
echo ""

# Get Zerodha Login URL
test_endpoint "Get Zerodha Login URL" "GET" "/api/users/zerodha/login" "" "$USER_TOKEN"

# Get Broker Accounts
test_endpoint "Get Broker Accounts" "GET" "/api/users/broker-accounts" "" "$USER_TOKEN"

echo ""
echo "=== 5. USER DASHBOARD TESTS ==="
echo ""

# Get Dashboard
test_endpoint "Get User Dashboard" "GET" "/api/users/me/dashboard" "" "$USER_TOKEN"

# Get Positions
test_endpoint "Get User Positions" "GET" "/api/users/me/positions" "" "$USER_TOKEN"

echo ""
echo "=== 6. MONITORING TESTS ==="
echo ""

# Get Monitoring Metrics
test_endpoint "Get Monitoring Metrics" "GET" "/api/monitoring/metrics" "" "$ADMIN_TOKEN"

# Get Monitoring Health
test_endpoint "Get Monitoring Health" "GET" "/api/monitoring/health" "" "$ADMIN_TOKEN"

echo ""
echo "=================================="
echo "  TEST SUMMARY"
echo "=================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo "Total: $((PASS + FAIL))"
echo "=================================="
echo ""
echo "Tokens saved for manual testing:"
echo "ADMIN_TOKEN=$ADMIN_TOKEN"
echo "USER_TOKEN=$USER_TOKEN"
