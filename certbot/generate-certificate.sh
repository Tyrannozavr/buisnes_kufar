#!/bin/bash
# generate-certificate.sh
set -e

# Проверка переменных среды
if [[ -z "$DOMAIN_EMAIL" || -z "$DOMAIN_URL" ]]; then
  echo "Ошибка: Необходимо установить переменные среды DOMAIN_EMAIL и DOMAIN_URL."
  echo "Пример запуска: DOMAIN_EMAIL=mail@site.ru DOMAIN_URL=site.ru ./generate-certificate.sh"
  exit 1
fi

# чистим папку, где могут находиться старые сертификаты
rm -rf /etc/letsencrypt/live/tradesynergy.ru
echo "Старые сертификаты удалены."

# выдаем себе сертификат
certbot certonly --webroot --webroot-path=/var/www/html --email "$DOMAIN_EMAIL" -d "$DOMAIN_URL" --cert-name=tradesynergy.ru --key-type rsa --agree-tos --non-interactive

echo "Сертификат успешно получен."

# Сертификаты уже находятся в правильном месте для nginx
echo "Сертификаты готовы для использования nginx."

echo "Готово! Сертификаты обновлены." 