#!/bin/bash
# Команды для восстановления базы данных на сервере

echo "Создаем базу данных (если не существует)..."
docker exec -i buisnes_kufar-db-1 psql -U postgres -c "CREATE DATABASE buisnes_kufar;" 2>/dev/null || echo "База данных уже существует или создана"

echo "Восстанавливаем дамп..."
cat backup_20251026_143805.sql | docker exec -i buisnes_kufar-db-1 psql -U postgres -d buisnes_kufar

echo "Готово!"
