FROM ubuntu:22.04

# Устанавливаем необходимые пакеты
RUN apt-get update && \
    apt-get install -y \
    certbot \
    python3-certbot-nginx \  # Для интеграции с Nginx (опционально)
    && rm -rf /var/lib/apt/lists/*

# Копируем скрипт и даем права на выполнение
COPY generate-certificate.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/generate-certificate.sh

# Рабочая директория
WORKDIR /certbot

# Переменные среды
ENV DOMAIN_EMAIL=${DOMAIN_EMAIL:-"default@example.com"}
ENV DOMAIN_URL=${DOMAIN_URL:-"example.com"}

# Точка входа
CMD ["/usr/local/bin/generate-certificate.sh"]