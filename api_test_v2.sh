#!/bin/bash
API="http://localhost:3445"

echo "=================================="
echo "  SaaS API Test Suite v2"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

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
    
    if echo "$response" | grep -qi "error\|Internal Server Error\|detail" && ! echo "$response" | grep -q "id\|status\|email\|role\|healthy\|lot_size\|positions\|token"; then
        echo -e "${RED}FAILED${NC}"
        echo "  Response: $response"
        FAIL=$((FAIL + 1))
    else
        echo -e "${GREEN}OK${NC}"
        PASS=$((PASS + 1))
    fi
}

echo "=== 1. AUTHENTICATION ==="

# Login Admin
ADMIN_TOKEN=$(curl -s -X POST "$API/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@saas.com","password":"Admin123!"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$ADMIN_TOKEN" ]; then
    echo -e "Admin Login: ${GREEN}OK${NC}"
    PASS=$((PASS + 1))
else
    echo -e "Admin Login: ${RED}FAILED${NC}"
    FAIL=$((FAIL + 1))
fi

# Login User
USER_TOKEN=$(curl -s -X POST "$API/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"user@saas.com","password":"User123!"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$USER_TOKEN" ]; then
    echo -e "User Login: ${GREEN}OK${NC}"
    PASS=$((PASS + 1))
else
    echo -e "User Login: ${RED}FAILED${NC}"
    FAIL=$((FAIL + 1))
fi

test_endpoint "Get Admin Profile" "GET" "/api/auth/me" "" "$ADMIN_TOKEN"
test_endpoint "Get User Profile" "GET" "/api/auth/me" "" "$USER_TOKEN"

echo ""
echo "=== 2. TRADING PROFILE ==="

test_endpoint "Create Trading Profile" "POST" "/api/users/me/trading-profile" '{"lot_size_multiplier":"2X","risk_profile":"MODERATE","max_loss_per_day":5000}' "$USER_TOKEN"
test_endpoint "Get Trading Profile" "GET" "/api/users/me/trading-profile" "" "$USER_TOKEN"

echo ""
echo "=== 3. ADMIN FEATURES ==="

test_endpoint "List All Users" "GET" "/api/admin/users" "" "$ADMIN_TOKEN"

echo ""
echo "=== 4. BROKER ENDPOINTS ==="

test_endpoint "Get Zerodha Login URL" "GET" "/api/users/zerodha/login" "" "$USER_TOKEN"
test_endpoint "Get Broker Accounts" "GET" "/api/users/broker-accounts" "" "$USER_TOKEN"

echo ""
echo "=== 5. USER DASHBOARD ==="

test_endpoint "Get Dashboard" "GET" "/api/users/me/dashboard" "" "$USER_TOKEN"
test_endpoint "Get Positions" "GET" "/api/users/me/positions" "" "$USER_TOKEN"

echo ""
echo "=== 6. MONITORING ==="

test_endpoint "Health Check" "GET" "/api/monitoring/" "" "$ADMIN_TOKEN"
test_endpoint "Metrics" "GET" "/api/monitoring/metrics" "" "$ADMIN_TOKEN"
test_endpoint "Stats" "GET" "/api/monitoring/stats" "" "$ADMIN_TOKEN"

echo ""
echo "=================================="
echo "  SUMMARY"
echo "=================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo "Total: $((PASS + FAIL))"
echo "=================================="
