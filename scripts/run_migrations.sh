#!/bin/bash

# Скрипт для запуска миграций базы данных
# Использует отдельный контейнер для миграций

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Database Migration Script${NC}"
echo "=================================="

# Проверяем, какой compose файл использовать
if [ "$1" = "dev" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
    echo -e "${YELLOW}📝 Using development environment${NC}"
else
    COMPOSE_FILE="docker-compose.yml"
    echo -e "${YELLOW}📝 Using production environment${NC}"
fi

# Проверяем существование compose файла
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Compose file $COMPOSE_FILE not found!${NC}"
    exit 1
fi

echo -e "${BLUE}🔍 Checking if database is running...${NC}"

# Проверяем, запущена ли база данных
if ! docker compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Database is not running. Starting database...${NC}"
    docker compose -f "$COMPOSE_FILE" up -d db
    
    # Ждем, пока база данных станет доступной
    echo -e "${BLUE}⏳ Waiting for database to be ready...${NC}"
    sleep 10
fi

echo -e "${GREEN}✅ Database is running${NC}"

# Запускаем миграции
echo -e "${BLUE}🚀 Running migrations...${NC}"
echo "=================================="

if docker compose -f "$COMPOSE_FILE" run --rm migrations; then
    echo "=================================="
    echo -e "${GREEN}✅ Migrations completed successfully!${NC}"
    
    # Показываем текущее состояние миграций
    echo -e "${BLUE}📊 Current migration status:${NC}"
    docker compose -f "$COMPOSE_FILE" exec backend alembic current || echo -e "${YELLOW}⚠️  Could not get migration status${NC}"
    
else
    echo "=================================="
    echo -e "${RED}❌ Migrations failed!${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Migration process completed!${NC}"
