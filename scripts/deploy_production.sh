#!/usr/bin/env bash
# Деплой на продакшн (запускать на сервере в /root/buisnes_kufar)
set -euo pipefail

cd "$(dirname "$0")/.."
BRANCH="${DEPLOY_BRANCH:-preprod}"

echo "📥 git pull origin ${BRANCH}"
git fetch origin
git checkout "${BRANCH}"
git reset --hard "origin/${BRANCH}"

echo "🔄 Миграции (alembic из каталога на хосте)"
docker compose run --rm --no-deps --entrypoint "" \
  -v "$(pwd)/backend/alembic:/app/alembic:ro" \
  backend alembic -c /app/alembic.ini upgrade head

echo "🔨 Сборка frontend, backend, nginx, celery"
if ! docker compose build frontend backend nginx celery-worker celery-beat; then
  echo "⚠️  Сборка не удалась (часто сеть Docker Hub). Обновляем код в работающих контейнерах..."
  for svc in backend celery-worker celery-beat; do
    cid="$(docker compose ps -q "${svc}" 2>/dev/null || true)"
    [ -n "${cid}" ] || continue
    docker cp backend/app/. "${cid}:/app/app/"
    docker cp backend/alembic/. "${cid}:/app/alembic/"
    docker cp backend/alembic.ini "${cid}:/app/alembic.ini"
  done
fi

echo "🚀 docker compose up -d"
docker compose up -d frontend backend nginx celery-worker celery-beat

echo "✅ Готово. Проверка:"
docker compose ps --format 'table {{.Name}}\t{{.Status}}' | head -12
