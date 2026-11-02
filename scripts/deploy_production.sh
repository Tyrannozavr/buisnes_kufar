#!/usr/bin/env bash
# Деплой на продакшн (запускать на сервере в /root/buisnes_kufar)
set -euo pipefail

cd "$(dirname "$0")/.."
BRANCH="${DEPLOY_BRANCH:-preprod}"

echo "📥 git pull origin ${BRANCH}"
git fetch origin
git checkout "${BRANCH}"
git reset --hard "origin/${BRANCH}"

echo "🔨 Сборка frontend, backend, nginx, celery (до миграций — нужен актуальный код app.*)"
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

echo "🔄 Миграции"
docker compose run --rm --no-deps --entrypoint "" \
  backend alembic -c /app/alembic.ini upgrade head

echo "🚀 docker compose up -d"
docker compose up -d frontend backend nginx celery-worker celery-beat

# Nginx резолвит upstream при старте/reload. После recreate backend/frontend без reload
# остаются старые IP → 502 на /api (логин) и «пустые» страницы у клиента.
echo "🔁 nginx reload (обновить DNS upstream)"
docker compose exec -T nginx nginx -s reload || true

echo "✅ Готово. Проверка:"
docker compose ps --format 'table {{.Name}}\t{{.Status}}' | head -12
curl -sS -o /dev/null -w "login_api:%{http_code}\n" -X POST http://127.0.0.1/api/v1/auth/login \
  -H 'Host: devxyz.ridewise.ru' -H 'Content-Type: application/json' \
  -d '{"login":"seller@gmail.com","password":"123456"}' || true
