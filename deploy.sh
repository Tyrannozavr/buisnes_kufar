#!/bin/bash

echo "🚀 Начинаем развертывание..."

# 1. Создаем дамп локально (только данные, без CREATE TABLE)
echo "📦 Создаем дамп базы данных..."
docker-compose exec -T db pg_dump -U postgres -d buisnes_kufar -t countries -t federal_districts -t regions -t cities --data-only -F p > dump/locations_data_only.sql

# 2. Подключаемся к серверу и создаем директорию dump/ если её нет
echo "📤 Создаем директорию dump/ на сервере..."
ssh root@77.222.47.33 "mkdir -p ~/buisnes_kufar/dump/"

# 3. Копируем на сервер
echo "📤 Копируем дамп на сервер..."
if scp dump/locations_data_only.sql root@77.222.47.33:~/buisnes_kufar/dump/ 2>&1; then
    echo "✅ Файл успешно скопирован!"
else
    echo "❌ Ошибка при копировании файла на сервер!"
    exit 1
fi

# 4. Выполняем команды на сервере
echo "🔄 Выполняем деплой на сервере..."
ssh root@77.222.47.33 << 'EOF'
cd ~/buisnes_kufar

echo "📥 Получаем изменения из Git..."
git pull origin master || echo "Git pull завершен"

echo "🛑 Останавливаем контейнеры..."
docker-compose down

echo "🔨 Пересобираем контейнеры..."
docker-compose up -d --build

echo "⏳ Ждем запуска базы данных..."
sleep 20

echo "🗑️ Очищаем таблицы локаций..."
docker-compose exec db psql -U postgres -d buisnes_kufar -c "TRUNCATE TABLE cities, regions, federal_districts, countries CASCADE;"

echo "📦 Загружаем новые данные..."
if [ -f "dump/locations_data_only.sql" ]; then
    docker-compose exec -T db psql -U postgres -d buisnes_kufar < dump/locations_data_only.sql
    echo "✅ Данные загружены!"
else
    echo "❌ Файл дампа не найден!"
    exit 1
fi

echo "📊 Проверяем результат..."
docker-compose exec db psql -U postgres -d buisnes_kufar -c "SELECT COUNT(*) as total_cities FROM cities WHERE is_active = TRUE"

echo ""
echo "✅ Развертывание завершено!"

EOF

echo ""
echo "🎉 Деплой завершен!"

