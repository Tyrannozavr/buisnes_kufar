#!/bin/sh
# renew.sh — обновление сертификатов и симлинка live/tradesynergy.ru
# Запуск: docker compose --profile certbot run --rm certbot /usr/local/bin/renew.sh
set -e

echo "Запуск certbot renew с deploy-hook..."
# --force-renewal если уже просрочен (иначе renew может skip'нуть битый lineage)
FORCE=""
if [ -f /etc/letsencrypt/live/tradesynergy.ru/fullchain.pem ]; then
  if ! openssl x509 -in /etc/letsencrypt/live/tradesynergy.ru/fullchain.pem -noout -checkend 0 >/dev/null 2>&1; then
    echo "Текущий сертификат просрочен — принудительное обновление"
    FORCE="--force-renewal"
  fi
fi

certbot renew --webroot --webroot-path=/var/www/html --non-interactive \
  $FORCE \
  --deploy-hook "/usr/local/bin/update-certificate-links.sh"

echo "Обновление симлинка на актуальный сертификат..."
/usr/local/bin/update-certificate-links.sh

echo "Готово. Перезагрузите nginx: docker exec buisnes_kufar-nginx-1 nginx -s reload"
