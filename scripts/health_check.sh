#!/bin/bash
# Usage: ./scripts/health_check.sh https://your-app-url.com

BASE_URL="${1:-http://localhost:8000}"
PASS=0
FAIL=0

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check() {
    local name="$1"
    local expected_status="$2"
    local actual_status="$3"
    local expected_field="$4"
    local actual_field="$5"

    if [ "$actual_status" == "$expected_status" ] && \
       ([ -z "$expected_field" ] || [ "$actual_field" == "$expected_field" ]); then
        echo -e "${GREEN}PASS${NC} — $name (HTTP $actual_status)"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}FAIL${NC} — $name (got HTTP $actual_status, expected $expected_status)"
        FAIL=$((FAIL + 1))
    fi
}

echo "Running health checks against: $BASE_URL"
echo "─────────────────────────────────────────────"

# Check 1: Swagger UI available
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$BASE_URL/docs")
check "GET /docs — Swagger UI reachable" "200" "$STATUS"

# Check 2: Validation error on missing body
RESPONSE=$(curl -s -o /tmp/hc_resp.json -w "%{http_code}" --max-time 10 \
    -X POST "$BASE_URL/carts" \
    -H "Content-Type: application/json" \
    -d '{}')
ERROR=$(cat /tmp/hc_resp.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('error',''))" 2>/dev/null)
check "POST /carts {} — returns VALIDATION_ERROR" "422" "$RESPONSE" "VALIDATION_ERROR" "$ERROR"

# Check 3: User not found
RESPONSE=$(curl -s -o /tmp/hc_resp.json -w "%{http_code}" --max-time 10 \
    -X POST "$BASE_URL/carts" \
    -H "Content-Type: application/json" \
    -d '{"user_id": 999}')
ERROR=$(cat /tmp/hc_resp.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('error',''))" 2>/dev/null)
check "POST /carts user_id=999 — returns USER_NOT_FOUND" "404" "$RESPONSE" "USER_NOT_FOUND" "$ERROR"

# Check 4: Invalid path param
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    -X DELETE "$BASE_URL/carts/0")
check "DELETE /carts/0 — returns 422 validation" "422" "$RESPONSE"

echo "─────────────────────────────────────────────"
echo "Results: ${PASS} passed, ${FAIL} failed"

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}Health check FAILED${NC}"
    exit 1
fi
echo -e "${GREEN}Health check PASSED${NC}"
exit 0
