#!/usr/bin/env bash
# TZ15 + core API smoke на рабочей dev-БД
set -euo pipefail
BASE="${API_BASE:-http://localhost:8014}"
API="$BASE/api/v1"
PASS="${TEST_PASSWORD:-123456}"
FAIL=0

check() {
  local name="$1" code="$2"
  if [[ "$code" -ge 200 && "$code" -lt 300 ]]; then
    echo "OK  $name ($code)"
  else
    echo "FAIL $name ($code)"
    FAIL=1
  fi
}

login() {
  local email="$1"
  curl -s -X POST "$API/auth/login" -H 'Content-Type: application/json' \
    -d "{\"login\":\"$email\",\"password\":\"$PASS\"}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))"
}

echo "=== TZ15 API smoke ==="
SELLER_TOKEN=$(login seller@gmail.com)
BUYER_TOKEN=$(login buyer@gmail.com)
CARRIER_TOKEN=$(login carrier@gmail.com)

for pair in "seller:$SELLER_TOKEN" "buyer:$BUYER_TOKEN" "carrier:$CARRIER_TOKEN"; do
  label="${pair%%:*}"
  token="${pair#*:}"
  if [[ -z "$token" ]]; then echo "FAIL login $label"; FAIL=1; fi
done

# §7 fill addresses
code=$(curl -s -o /tmp/fa.json -w '%{http_code}' -H "Authorization: Bearer $SELLER_TOKEN" "$API/company/me/fill-addresses")
check "GET fill-addresses" "$code"

# §6 counterparties
code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $SELLER_TOKEN" "$API/company/me/counterparties?per_page=10")
check "GET counterparties" "$code"

code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $SELLER_TOKEN" "$API/company/me/carriers?per_page=10")
check "GET carriers" "$code"

# deals
code=$(curl -s -o /tmp/deals.json -w '%{http_code}' -H "Authorization: Bearer $SELLER_TOKEN" "$API/purchases/seller/deals?limit=10")
check "GET seller deals" "$code"
DEAL_ID=$(python3 -c "import json; d=json.load(open('/tmp/deals.json')); print(d[0]['id'] if isinstance(d,list) and d else (d.get('data',[{}])[0].get('id','') if isinstance(d,dict) else ''))" 2>/dev/null || true)

if [[ -n "$DEAL_ID" ]]; then
  code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $SELLER_TOKEN" "$API/purchases/deals/$DEAL_ID")
  check "GET deal by id" "$code"

  # §8 bill replace path (no-op if no bill — still 200 on create)
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H "Authorization: Bearer $SELLER_TOKEN" \
    -H 'Content-Type: application/json' -d '{"replace":false}' "$API/purchases/deals/$DEAL_ID/bill")
  check "POST bill" "$code"

  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H "Authorization: Bearer $SELLER_TOKEN" \
    -H 'Content-Type: application/json' -d '{}' "$API/purchases/deals/$DEAL_ID/transport-contract")
  check "POST transport-contract" "$code"

  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H "Authorization: Bearer $SELLER_TOKEN" \
    -H 'Content-Type: application/json' -d '{"doc_type":"UPD"}' "$API/purchases/deals/$DEAL_ID/closing-document")
  check "POST closing-document" "$code"
fi

code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $BUYER_TOKEN" "$API/purchases/buyer/deals?limit=10")
check "GET buyer deals" "$code"

code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $SELLER_TOKEN" "$API/purchases/company-contracts")
check "GET company contracts" "$code"

code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $SELLER_TOKEN" "$API/purchases/units")
check "GET units (OKEI)" "$code"

echo "=== done ==="
exit $FAIL
