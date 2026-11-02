#!/bin/bash
# Автопродление SSL для tradesynergy.ru (cron на сервере: 0 3,15 * * *)
set -euo pipefail
cd /root/buisnes_kufar
rm -f nginx/letsencrypt/.certbot.lock
docker compose --profile certbot run --rm certbot /usr/local/bin/renew.sh >> /var/log/ssl-renew.log 2>&1
