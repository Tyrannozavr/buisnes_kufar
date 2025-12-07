#!/bin/bash
# Выполните этот скрипт на ЛОКАЛЬНОЙ машине

echo "🚀 Начинаем развертывание на сервер..."

cd /home/dmiv/PycharmProjects/buisnes_kufar

echo "📦 Создаем дамп локаций..."
docker-compose exec db pg_dump -U postgres -d buisnes_kufar -t countries -t federal_districts -t regions -t cities -F p > dump/locations_structure.sql

echo "📊 Проверяем размер файла..."
ls -lh dump/locations_structure.sql

echo "📤 Копируем файл на сервер..."
scp dump/locations_structure.sql root@77.222.47.33:~/buisnes_kufar/dump/

echo "🔄 Выполняем деплой на сервере..."
ssh root@77.222.47.33 'bash -s' < deploy_serverside.sh

echo ""
echo "✅ Развертывание на сервер завершено!"

