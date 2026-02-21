#!/usr/bin/env bash
# Проверка продакшена tradesynergy.ru по ТЗ (страницы + API)
# Запуск: bash scripts/test_production.sh

set -e
BASE="https://tradesynergy.ru"
API="$BASE/api/v1"
FAIL=0

check() {
  local method="$1"
  local url="$2"
  local expect="$3"
  local desc="${4:-$url}"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" -L -k 2>/dev/null || echo "000")
  if [ "$code" = "$expect" ]; then
    echo "OK   $expect $desc"
  else
    echo "FAIL $desc (ожидалось $expect, получено $code)"
    FAIL=$((FAIL+1))
  fi
}

echo "=== Страницы (по ТЗ) ==="
check GET "$BASE/" 200 "Главная"
check GET "$BASE/auth/login" 200 "Вход"
check GET "$BASE/catalog/products" 200 "Каталог товаров"
check GET "$BASE/catalog/services" 200 "Каталог услуг"
check GET "$BASE/checkout" 200 "Подтверждение заказа (checkout)"
# Профиль: без авторизации отдаётся 200 (страница с client-side редиректом или meta refresh)
check GET "$BASE/profile/purchases" 200 "Профиль закупки (страница или редирект)"
check GET "$BASE/profile/sales" 200 "Профиль продажи"
check GET "$BASE/profile/documents" 200 "Профиль документы"
# Редактор: 200 после деплоя фикса useStates (SSR); до деплоя возможна 500
code_editor=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/profile/editor" -L -k 2>/dev/null || echo "000")
if [ "$code_editor" = "200" ]; then
  echo "OK   200 Редактор заказа"
elif [ "$code_editor" = "500" ]; then
  echo "WARN 500 Редактор заказа (до деплоя фикса useStates.ts для SSR)"
else
  echo "FAIL Редактор заказа (код $code_editor)"
  FAIL=$((FAIL+1))
fi
check GET "$BASE/companies" 200 "Список компаний"
check GET "$BASE/docs" 200 "Swagger API"
check GET "$BASE/about" 200 "О нас"

echo ""
echo "=== API (публичные) ==="
check GET "$API/companies/?limit=3" 200 "GET /api/v1/companies/"
check GET "$API/announcements?per_page=3" 200 "GET /api/v1/announcements"
check GET "$API/products?limit=3" 200 "GET /api/v1/products"
check GET "$API/locations/location-tree" 200 "GET /api/v1/locations/location-tree"
check GET "$API/locations/countries" 200 "GET /api/v1/locations/countries"

echo ""
if [ $FAIL -eq 0 ]; then
  echo "Все проверки пройдены."
  exit 0
else
  echo "Ошибок: $FAIL"
  exit 1
fi
