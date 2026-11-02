#!/usr/bin/env bash
# Освободить 8080/8012/3012 от зомби docker-proxy и поднять docker-compose.dev.yml.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Убиваем docker-proxy на 8080/8012/3012/8081/8013/3013"
for port in 8080 8012 3012 8081 8013 3013; do
  while read -r pid; do
    [ -n "${pid:-}" ] || continue
    cmd=$(ps -p "$pid" -o comm= 2>/dev/null || true)
    if [ "$cmd" = "docker-proxy" ]; then
      echo "  kill $pid (port $port)"
      sudo kill "$pid" || true
    fi
  done < <(sudo ss -tlnp "( sport = :$port )" 2>/dev/null | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | sort -u)
done

echo "==> Логи backend (права)"
sudo mkdir -p backend/logging
sudo chown -R "$(id -u):$(id -g)" backend/logging || true
sudo rm -f backend/logging/app.log
touch backend/logging/app.log
chmod 666 backend/logging/app.log || true

echo "==> Пересоздаём стек"
docker compose -f docker-compose.dev.yml down --remove-orphans || true
docker compose -f docker-compose.dev.yml up -d --build

echo "==> Ждём nginx..."
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 http://localhost:8080/ || true)
  if [ "$code" != "000" ] && [ -n "$code" ]; then
    echo "OK http://localhost:8080/ → HTTP $code"
    exit 0
  fi
  sleep 2
done

echo "WARN: 8080 ещё не отвечает — смотри: docker compose -f docker-compose.dev.yml ps / logs"
exit 1
