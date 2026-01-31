#!/usr/bin/env bash
# Проверка API документов: GET/PUT по deal_id и document_type.
# Требует: запущенный бэкенд, токен (логин через /api/v1/auth/login) и существующий deal_id.
# Использование: ./scripts/test_documents_api.sh <BASE_URL> <ACCESS_TOKEN> <DEAL_ID>
# Пример: ./scripts/test_documents_api.sh http://localhost:8012 "eyJ..." 1

set -e
BASE_URL="${1:-http://localhost:8012}"
TOKEN="${2:?Need ACCESS_TOKEN}"
DEAL_ID="${3:?Need DEAL_ID}"
DOC_TYPE="order"

echo "GET ${BASE_URL}/api/v1/purchases/${DEAL_ID}/documents/${DOC_TYPE}"
curl -s -X GET "${BASE_URL}/api/v1/purchases/${DEAL_ID}/documents/${DOC_TYPE}" \
  -H "Authorization: Bearer ${TOKEN}" | jq .

echo ""
echo "PUT ${BASE_URL}/api/v1/purchases/${DEAL_ID}/documents/${DOC_TYPE}"
curl -s -X PUT "${BASE_URL}/api/v1/purchases/${DEAL_ID}/documents/${DOC_TYPE}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"payload":{"items":[{"name":"Тест","qty":1}],"comment":"curl test"}}' | jq .

echo ""
echo "GET again (check saved payload)"
curl -s -X GET "${BASE_URL}/api/v1/purchases/${DEAL_ID}/documents/${DOC_TYPE}" \
  -H "Authorization: Bearer ${TOKEN}" | jq .
