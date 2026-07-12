#!/usr/bin/env bash
# Ручная проверка API этапов 1–3 (счёт, договоры, заказ) через curl.
# Использование: bash scripts/test_schet_stages_api.sh [BASE_URL]
# Пример: bash scripts/test_schet_stages_api.sh https://tradesynergy.ru

set -euo pipefail
BASE="${1:-https://tradesynergy.ru}"
API="$BASE/api/v1"
SELLER_EMAIL="${SChet_SELLER_EMAIL:-seller@gmail.com}"
BUYER_EMAIL="${SChet_BUYER_EMAIL:-buyer@gmail.com}"
PASS="${SChet_PASS:-123456}"
FAIL=0
TMP="${TMPDIR:-/tmp}/schet_api_$$"
mkdir -p "$TMP"

login() {
  local email="$1"
  local out="$2"
  curl -s -X POST "$API/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"login\":\"$email\",\"password\":\"$PASS\"}" -L -k >"$out" 2>/dev/null || true
  if ! grep -q '"access_token"' "$out"; then
    echo "FAIL логин $email"
    cat "$out" | head -c 300
    echo ""
    exit 1
  fi
  sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p' "$out" | head -1
}

check() {
  local method="$1" url="$2" token="$3" expect="$4" desc="$5"
  local body="${6:-}"
  local code auth=()
  [ -n "$token" ] && auth=(-H "Authorization: Bearer $token")
  if [ -n "$body" ]; then
    code=$(curl -s -o "$TMP/resp.json" -w "%{http_code}" -X "$method" "$url" \
      "${auth[@]}" -H "Content-Type: application/json" \
      -d "$body" -L -k 2>/dev/null || echo "000")
  else
    code=$(curl -s -o "$TMP/resp.json" -w "%{http_code}" -X "$method" "$url" \
      "${auth[@]}" -L -k 2>/dev/null || echo "000")
  fi
  if [ "$code" = "$expect" ]; then
    echo "OK   $expect $desc"
  else
    echo "FAIL $desc (ожидалось $expect, получено $code)"
    head -c 400 "$TMP/resp.json" 2>/dev/null || true
    echo ""
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Логин тестовых пользователей ==="
SELLER_TOKEN=$(login "$SELLER_EMAIL" "$TMP/seller.json")
echo "OK   seller token"
BUYER_TOKEN=$(login "$BUYER_EMAIL" "$TMP/buyer.json")
echo "OK   buyer token"

echo ""
echo "=== Этап 2: сделки, единицы измерения ==="
check GET "$API/purchases/seller/deals?skip=0&limit=20" "$SELLER_TOKEN" 200 "GET seller/deals"
curl -s -o "$TMP/deals.json" -H "Authorization: Bearer $SELLER_TOKEN" "$API/purchases/seller/deals?limit=5" -k
DEAL_ID=$(grep -o '"id":[0-9]*' "$TMP/deals.json" | head -1 | cut -d: -f2 || true)
check GET "$API/purchases/buyer/deals?skip=0&limit=20" "$BUYER_TOKEN" 200 "GET buyer/deals"
check GET "$API/purchases/units-of-measurement" "$SELLER_TOKEN" 200 "GET units-of-measurement"

if [ -n "$DEAL_ID" ]; then
  echo "     deal_id=$DEAL_ID"
  check GET "$API/purchases/deals/$DEAL_ID" "$SELLER_TOKEN" 200 "GET deal by id"
  check GET "$API/purchases/deals/$DEAL_ID/changes/review" "$BUYER_TOKEN" 200 "GET change review"
else
  echo "WARN нет сделок у продавца — пропуск deal-specific"
fi

echo ""
echo "=== Этап 3.2: company-contracts ==="
check GET "$API/purchases/company-contracts" "$SELLER_TOKEN" 200 "GET company-contracts list"
check GET "$API/purchases/company-contracts/next-number?relation=as_seller" "$SELLER_TOKEN" 200 "GET next-number"

echo ""
echo "=== Этап 3.3: версия заказа (order-only body) ==="
if [ -n "$DEAL_ID" ]; then
  check POST "$API/purchases/deals/$DEAL_ID/versions" "$BUYER_TOKEN" 200 \
    "POST versions (buyer comments)" '{"comments":"curl-test-buyer"}'
  check POST "$API/purchases/deals/$DEAL_ID/versions" "$BUYER_TOKEN" 403 \
    "POST versions buyer+bill forbidden" '{"comments":"x","bill":{"number":"HACK"}}'
  check POST "$API/purchases/deals/$DEAL_ID/versions" "$SELLER_TOKEN" 200 \
    "POST versions (seller order)" '{"comments":"curl-test-seller"}'
fi

echo ""
echo "=== Этап 3.4: supply-contract entity ==="
if [ -n "$DEAL_ID" ]; then
  check GET "$API/purchases/deals/$DEAL_ID" "$SELLER_TOKEN" 200 "GET deal for supply contract"
fi

echo ""
echo "=== Публичные ручки ==="
check GET "$API/companies/?limit=3" "" 200 "GET companies (no auth)"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "Все проверки этапов 1–3 API пройдены."
  rm -rf "$TMP"
  exit 0
else
  echo "Ошибок: $FAIL"
  rm -rf "$TMP"
  exit 1
fi
