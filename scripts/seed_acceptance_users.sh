#!/usr/bin/env bash
# Seed тестовых пользователей для приёмки (ТЗ_15 + счёт).
# Запуск на новом ПК после поднятия docker-compose.dev.yml и миграций.
#
# Что создаёт / обновляет (idempotent):
#   seller@gmail.com      — ООО Поставщик Тест
#   buyer@gmail.com       — ООО Покупатель Тест
#   carrier@gmail.com     — ООО Перевозчик Тест
#   forwarder@gmail.com   — ООО Экспедитор Тест
#   + алиасы разработчика, сделки, договоры, fill-адреса, ОКЕИ
#
# Пароль всех: 123456
#
# Использование:
#   bash scripts/seed_acceptance_users.sh
#   COMPOSE_FILE=docker-compose.yml bash scripts/seed_acceptance_users.sh   # другой compose

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.dev.yml}"
SERVICE="${BACKEND_SERVICE:-backend}"

echo "=== Seed приёмки (seller / buyer / carrier / forwarder) ==="
echo "compose: $COMPOSE_FILE  service: $SERVICE"
echo

if ! docker compose -f "$COMPOSE_FILE" ps --status running "$SERVICE" 2>/dev/null | grep -q "$SERVICE"; then
  echo "Backend не запущен. Поднимите стек:"
  echo "  docker compose -f $COMPOSE_FILE up -d"
  echo "  docker compose -f $COMPOSE_FILE exec $SERVICE poetry run alembic upgrade head"
  exit 1
fi

echo "→ миграции (alembic upgrade head)..."
docker compose -f "$COMPOSE_FILE" exec -T "$SERVICE" poetry run alembic upgrade head

echo "→ ensure_schet_test_users.py ..."
docker compose -f "$COMPOSE_FILE" exec -T "$SERVICE" poetry run python scripts/ensure_schet_test_users.py

echo
echo "=== Готово. Логин для приёмки (пароль 123456) ==="
echo "  seller@gmail.com      поставщик"
echo "  buyer@gmail.com       покупатель"
echo "  carrier@gmail.com     перевозчик"
echo "  forwarder@gmail.com   экспедитор"
echo
echo "Чеклист: docs/tz15/manual-full-acceptance-checklist.md"
echo "Аккаунты: docs/tz15/test-users.md"
