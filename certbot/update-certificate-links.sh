#!/bin/sh
# update-certificate-links.sh — live/tradesynergy.ru → lineage с самым поздним notAfter
set -e

echo "Обновление символических ссылок на сертификаты..."

BEST_DIR=""
BEST_EPOCH=0

for dir in /etc/letsencrypt/live/tradesynergy.ru /etc/letsencrypt/live/tradesynergy.ru-*; do
  [ -e "$dir/fullchain.pem" ] || [ -e "$dir/cert.pem" ] || continue
  # skip the symlink itself while scanning numbered lineages
  case "$dir" in
    */tradesynergy.ru) continue ;;
  esac
  pem="$dir/fullchain.pem"
  [ -f "$pem" ] || pem="$dir/cert.pem"
  [ -f "$pem" ] || continue
  end=$(openssl x509 -in "$pem" -noout -enddate 2>/dev/null | cut -d= -f2) || continue
  epoch=$(date -d "$end" +%s 2>/dev/null) || continue
  if [ "$epoch" -ge "$BEST_EPOCH" ]; then
    BEST_EPOCH=$epoch
    BEST_DIR=$dir
  fi
done

# Also consider a real directory named tradesynergy.ru (not a symlink)
if [ -d /etc/letsencrypt/live/tradesynergy.ru ] && [ ! -L /etc/letsencrypt/live/tradesynergy.ru ]; then
  pem=/etc/letsencrypt/live/tradesynergy.ru/fullchain.pem
  if [ -f "$pem" ]; then
    end=$(openssl x509 -in "$pem" -noout -enddate 2>/dev/null | cut -d= -f2) || true
    epoch=$(date -d "$end" +%s 2>/dev/null) || epoch=0
    if [ "$epoch" -ge "$BEST_EPOCH" ]; then
      BEST_EPOCH=$epoch
      BEST_DIR=/etc/letsencrypt/live/tradesynergy.ru
    fi
  fi
fi

if [ -z "$BEST_DIR" ]; then
  echo "Ошибка: Не найдены сертификаты tradesynergy.ru*"
  exit 1
fi

echo "Найден актуальный сертификат: $BEST_DIR (до $(date -d @$BEST_EPOCH -u '+%Y-%m-%d' 2>/dev/null || echo "$BEST_EPOCH"))"

TARGET_NAME=$(basename "$BEST_DIR")

if [ -L /etc/letsencrypt/live/tradesynergy.ru ] || [ -e /etc/letsencrypt/live/tradesynergy.ru ]; then
  if [ "$(readlink -f /etc/letsencrypt/live/tradesynergy.ru 2>/dev/null)" = "$(readlink -f "$BEST_DIR")" ]; then
    echo "Симлинк уже указывает на актуальный сертификат"
  else
    echo "Обновление симлинка live/tradesynergy.ru → $TARGET_NAME"
    rm -rf /etc/letsencrypt/live/tradesynergy.ru
    ln -sfn "$TARGET_NAME" /etc/letsencrypt/live/tradesynergy.ru
  fi
else
  ln -sfn "$TARGET_NAME" /etc/letsencrypt/live/tradesynergy.ru
fi

echo "Проверка созданной ссылки..."
ls -la /etc/letsencrypt/live/tradesynergy.ru

if [ -f /etc/letsencrypt/live/tradesynergy.ru/fullchain.pem ] && [ -f /etc/letsencrypt/live/tradesynergy.ru/privkey.pem ]; then
  echo "Сертификаты найдены и доступны"
  openssl x509 -in /etc/letsencrypt/live/tradesynergy.ru/fullchain.pem -noout -enddate
else
  echo "Ошибка: Файлы сертификатов не найдены"
  exit 1
fi

echo "Готово! Символические ссылки обновлены."
