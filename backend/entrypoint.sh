#!/bin/bash

# Entrypoint скрипт для backend контейнера
# Запускает FastAPI приложение без применения миграций

set -e

echo "🚀 Starting backend container..."

# Ждем, пока база данных станет доступной
echo "⏳ Waiting for database to be ready..."
until python -c "
import time
from sqlalchemy import create_engine
from app.core.config import settings

while True:
    try:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
        engine.connect().close()
        print('✅ Database is ready!')
        break
    except Exception as e:
        print(f'⏳ Database not ready yet: {e}')
        time.sleep(2)
" 2>/dev/null; do
    sleep 2
done

# Показываем текущее состояние миграций (только для информации)
echo "📊 Current migration status:"
alembic current || echo "⚠️  No migrations applied yet"

# Запускаем основное приложение
echo "🎉 Starting FastAPI application..."
exec "$@"
