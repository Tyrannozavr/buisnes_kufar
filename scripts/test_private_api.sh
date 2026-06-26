#!/usr/bin/env bash
# Проверка приватных API под пользователем dmitriy40647274@gmail.com
# Использование: bash scripts/test_private_api.sh [BASE_URL]
# BASE_URL по умолчанию https://tradesynergy.ru

set -e
BASE="${1:-https://tradesynergy.ru}"
API="$BASE/api/v1"
LOGIN="dmitriy40647274@gmail.com"
PASS="12345678"
FAIL=0

echo "=== Логин ==="
RESP=$(curl -s -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"login\":\"$LOGIN\",\"password\":\"$PASS\"}" -L -k 2>/dev/null || echo "{}")

if echo "$RESP" | grep -q '"access_token"'; then
  TOKEN=$(echo "$RESP" | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')
  echo "OK   Получен access_token"
else
  echo "FAIL Логин не удался. Ответ: $RESP"
  exit 1
fi

check_private() {
  local method="$1"
  local url="$2"
  local expect="$3"
  local desc="${4:-$url}"
  local code
  if [ "$method" = "GET" ]; then
    code=$(curl -s -o /tmp/private_response.json -w "%{http_code}" -X GET "$url" \
      -H "Authorization: Bearer $TOKEN" -L -k 2>/dev/null || echo "000")
  else
    code=$(curl -s -o /tmp/private_response.json -w "%{http_code}" -X "$method" "$url" \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -L -k 2>/dev/null || echo "000")
  fi
  if [ "$code" = "$expect" ]; then
    echo "OK   $expect $desc"
  else
    echo "FAIL $desc (ожидалось $expect, получено $code)"
    [ -f /tmp/private_response.json ] && cat /tmp/private_response.json | head -c 500
    echo ""
    FAIL=$((FAIL+1))
  fi
}

echo ""
echo "=== Приватные ручки (Bearer) ==="
check_private POST "$API/auth/verify-token" 200 "POST /auth/verify-token"
check_private GET  "$API/company/me" 200 "GET /company/me"
check_private GET  "$API/purchases/buyer/deals?skip=0&limit=10" 200 "GET /purchases/buyer/deals"
check_private GET  "$API/purchases/seller/deals?skip=0&limit=10" 200 "GET /purchases/seller/deals"
check_private GET  "$API/chats/" 200 "GET /chats/"
check_private GET  "$API/me/products?skip=0&limit=5" 200 "GET /me/products"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "Все приватные проверки пройдены."
  exit 0
else
  echo "Ошибок: $FAIL"
  exit 1
fi
