#!/bin/sh
# generate-certificate.sh
set -e

# Проверка переменных среды (используем совместимый с sh синтаксис)
if [ -z "$DOMAIN_EMAIL" ] || [ -z "$DOMAIN_URL" ]; then
  echo "Ошибка: Необходимо установить переменные среды DOMAIN_EMAIL и DOMAIN_URL."
  echo "Пример запуска: DOMAIN_EMAIL=mail@site.ru DOMAIN_URL=site.ru ./generate-certificate.sh"
  exit 1
fi

# Удаляем старые сертификаты (более безопасный вариант)
if [ -d "/etc/letsencrypt/live/tradesynergy.ru" ]; then
  echo "Удаление старых сертификатов..."
  rm -rf /etc/letsencrypt/live/tradesynergy.ru
  echo "Старые сертификаты удалены."
else
  echo "Старые сертификаты не найдены, пропускаем удаление."
fi

# Получаем новый сертификат (добавляем --force-renewal для гарантии)
echo "Запрос нового сертификата для $DOMAIN_URL..."
certbot certonly --webroot \
  --webroot-path=/var/www/html \
  --email "$DOMAIN_EMAIL" \
  -d "$DOMAIN_URL" \
  --cert-name=tradesynergy.ru \
  --key-type rsa \
  --agree-tos \
  --non-interactive \
  --force-renewal

echo "Сертификат успешно получен."

# Обновляем символические ссылки
echo "Обновление символических ссылок..."
/usr/local/bin/update-certificate-links.sh

echo "Готово! Сертификаты обновлены."