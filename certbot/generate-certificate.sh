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
certbot certonly --webroot --webroot-path=/var/www/html --email "$DOMAIN_EMAIL" -d "$DOMAIN_URL" --cert-name=certfolder --key-type rsa --agree-tos

echo "Сертификат успешно получен."

# удаляем старые сертификаты из папки Nginx
rm -f /etc/nginx/cert.pem
rm -f /etc/nginx/key.pem
echo "Старые сертификаты Nginx удалены."

# копируем сертификаты из certbot в папку Nginx
cp /etc/letsencrypt/live/tradesynergy.ru/fullchain.pem /etc/nginx/cert.pem
cp /etc/letsencrypt/live/tradesynergy.ru/privkey.pem /etc/nginx/key.pem
echo "Сертификаты скопированы в /etc/nginx."

echo "Готово! Сертификаты обновлены." 