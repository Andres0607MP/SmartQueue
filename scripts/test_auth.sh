#!/usr/bin/env bash
set -euo pipefail

# Usage: BASE_URL=https://your-domain ./scripts/test_auth.sh
BASE_URL=${BASE_URL:-http://localhost:8000}
USERNAME=${USERNAME:-apitest}
EMAIL=${EMAIL:-apitest@example.com}
PASSWORD=${PASSWORD:-TestPass123}

echo "Base URL: $BASE_URL"

# 1) Try to register the user via API (idempotent if already exists)
echo "Registering user $USERNAME..."
REG_RES=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/users/register/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

HTTP_CODE=$(echo "$REG_RES" | tail -n1)
BODY=$(echo "$REG_RES" | sed '$d')

echo "Register response code: $HTTP_CODE"
echo "$BODY"

# proceed even if user exists (400/409)

# 2) Get token
echo
"Obtaining JWT token..."
TOK=$(curl -s -X POST "$BASE_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

echo "$TOK" | jq || true
ACCESS=$(echo "$TOK" | jq -r '.access // empty')
REFRESH=$(echo "$TOK" | jq -r '.refresh // empty')

if [ -z "$ACCESS" ]; then
  echo "Failed to get access token. Full response:"
  echo "$TOK"
  exit 1
fi

# 3) Call protected endpoint: /api/users/me/ (requires auth)
echo
"Calling protected endpoint /api/users/me/ with access token..."
PROT=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/users/me/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Accept: application/json")
HTTP_CODE=$(echo "$PROT" | tail -n1)
BODY=$(echo "$PROT" | sed '$d')

echo "Protected endpoint response code: $HTTP_CODE"
echo "$BODY"

if [ "$HTTP_CODE" -ne 200 ]; then
  echo "Protected endpoint did not return 200. Authentication may be failing."
  exit 2
fi

# 4) Success
echo "Authentication flow OK: token valid and protected endpoint returned 200."
exit 0
