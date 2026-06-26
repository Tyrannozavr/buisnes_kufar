#!/bin/sh
# renew.sh — обновление сертификатов и симлинка live/tradesynergy.ru на последнюю версию
# Запуск: docker compose run --rm certbot /usr/local/bin/renew.sh
set -e

echo "Запуск certbot renew с deploy-hook..."
certbot renew --webroot --webroot-path=/var/www/html --non-interactive \
  --deploy-hook "/usr/local/bin/update-certificate-links.sh"

echo "Обновление симлинка на последний сертификат (на случай нового lineage)..."
/usr/local/bin/update-certificate-links.sh

echo "Готово. Перезагрузите nginx: docker exec buisnes_kufar-nginx-1 nginx -s reload"
