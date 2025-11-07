#!/bin/bash

# Скрипт для применения миграций Alembic
# Используется при развертывании для обновления базы данных

set -e

echo "🔄 Starting database migration process..."

# Проверяем, что контейнер backend запущен
if ! docker compose ps backend | grep -q "Up"; then
    echo "❌ Backend container is not running. Please start it first."
    exit 1
fi

# Проверяем, что база данных доступна
echo "🔍 Checking database connection..."
if ! docker compose exec backend python -c "from app.core.config import settings; from sqlalchemy import create_engine; engine = create_engine(settings.SQLALCHEMY_DATABASE_URL); engine.connect().close(); print('Database connection OK')" 2>/dev/null; then
    echo "❌ Cannot connect to database. Please check database configuration."
    exit 1
fi

echo "✅ Database connection established"

# Проверяем текущее состояние миграций
echo "📊 Current migration status:"
docker compose exec backend alembic current

# Применяем миграции
echo "🚀 Applying migrations..."
if docker compose exec backend alembic upgrade head; then
    echo "✅ Migrations applied successfully!"
    
    # Показываем финальное состояние
    echo "📊 Final migration status:"
    docker compose exec backend alembic current
    
    echo "🎉 Database migration completed successfully!"
else
    echo "❌ Migration failed!"
    exit 1
fi
