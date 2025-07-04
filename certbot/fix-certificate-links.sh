#!/bin/sh
# fix-certificate-links.sh
set -e

echo "Исправление символических ссылок на сертификаты..."

# Находим последний сертификат
LATEST_CERT_DIR=$(ls -d /etc/letsencrypt/live/tradesynergy.ru-* 2>/dev/null | sort -V | tail -n 1)

if [ -z "$LATEST_CERT_DIR" ]; then
    echo "Ошибка: Не найдены сертификаты tradesynergy.ru-*"
    echo "Доступные директории:"
    ls -la /etc/letsencrypt/live/
    exit 1
fi

echo "Найден последний сертификат: $LATEST_CERT_DIR"

# Удаляем старую символическую ссылку, если она существует
if [ -L "/etc/letsencrypt/live/tradesynergy.ru" ]; then
    echo "Удаление старой символической ссылки..."
    rm -f /etc/letsencrypt/live/tradesynergy.ru
fi

# Создаем новую символическую ссылку
echo "Создание символической ссылки на $LATEST_CERT_DIR..."
ln -sf "$LATEST_CERT_DIR" /etc/letsencrypt/live/tradesynergy.ru

echo "Проверка созданной ссылки..."
ls -la /etc/letsencrypt/live/tradesynergy.ru

echo "Проверка наличия файлов сертификатов..."
if [ -f "/etc/letsencrypt/live/tradesynergy.ru/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/tradesynergy.ru/privkey.pem" ]; then
    echo "✅ Сертификаты найдены и доступны"
    echo "Сертификат действителен до: $(openssl x509 -in /etc/letsencrypt/live/tradesynergy.ru/fullchain.pem -noout -enddate)"
else
    echo "❌ Ошибка: Файлы сертификатов не найдены"
    exit 1
fi

echo "Готово! Символические ссылки исправлены."
echo "Теперь можно перезапустить nginx: docker-compose restart nginx" 