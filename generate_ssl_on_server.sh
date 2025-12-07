#!/bin/bash

echo "=== Генерация SSL сертификата на сервере ==="

# Укажите ваш email
DOMAIN_EMAIL="your-email@example.com"
DOMAIN_URL="tradesynergy.ru"

echo "Используем email: $DOMAIN_EMAIL"
echo "Домен: $DOMAIN_URL"
echo ""

# Сначала перезапустим nginx в dev режиме (без SSL)
echo "1. Временно отключаем SSL в nginx..."
# Нужно временно изменить конфигурацию nginx чтобы убрать SSL

# 2. Запустим certbot для получения сертификата
echo "2. Запускаем certbot..."
docker-compose run --rm certbot certbot certonly --webroot \
  --webroot-path=/var/www/html \
  --email "$DOMAIN_EMAIL" \
  -d "$DOMAIN_URL" \
  --cert-name=tradesynergy.ru \
  --key-type rsa \
  --agree-tos \
  --non-interactive

echo "3. Сертификат получен, перезапускаем nginx..."
docker-compose restart nginx

echo "Готово!"
