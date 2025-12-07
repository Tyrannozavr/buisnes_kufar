#!/bin/bash
# Выполните этот скрипт на сервере

cd ~/buisnes_kufar

echo "📥 Получаем изменения из Git..."
git pull origin master

echo "🛑 Останавливаем контейнеры..."
docker-compose down

echo "🔨 Пересобираем контейнеры..."
docker-compose up -d --build

echo "⏳ Ждем запуска базы данных (15 сек)..."
sleep 15

echo "💾 Создаем резервную копию..."
docker-compose exec db pg_dump -U postgres -d buisnes_kufar -F c > ~/backup_$(date +%Y%m%d_%H%M%S).backup

echo "🗑️ Удаляем старые данные локаций..."
docker-compose exec db psql -U postgres -d buisnes_kufar -c "TRUNCATE TABLE cities, regions, federal_districts, countries CASCADE;"

echo "📦 Загружаем новые данные локаций..."
if [ -f "dump/locations_structure.sql" ]; then
    docker-compose exec -T db psql -U postgres -d buisnes_kufar < dump/locations_structure.sql
    echo "✅ Данные загружены!"
else
    echo "❌ Файл dump/locations_structure.sql не найден!"
    echo "Сначала скопируйте файл на сервер командой на ЛОКАЛЬНОЙ машине:"
    echo "scp dump/locations_structure.sql root@77.222.47.33:~/buisnes_kufar/dump/"
    exit 1
fi

echo "📊 Проверяем результат..."
docker-compose exec db psql -U postgres -d buisnes_kufar -c "SELECT COUNT(*) as total_cities FROM cities WHERE is_active = TRUE"

echo ""
echo "✅ Развертывание завершено! Городов должно быть: 11,526"

