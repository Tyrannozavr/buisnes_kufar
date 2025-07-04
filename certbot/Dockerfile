FROM ubuntu:22.04

# Устанавливаем необходимые пакеты
RUN apt-get update && \
    apt-get install -y \
    certbot \
    python3-certbot-nginx \
    && rm -rf /var/lib/apt/lists/*

# Копируем скрипты и даем права на выполнение
COPY generate-certificate.sh /usr/local/bin/
COPY update-certificate-links.sh /usr/local/bin/
COPY fix-certificate-links.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/generate-certificate.sh
RUN chmod +x /usr/local/bin/update-certificate-links.sh
RUN chmod +x /usr/local/bin/fix-certificate-links.sh

# Рабочая директория
WORKDIR /certbot

# Переменные среды
ENV DOMAIN_EMAIL=${DOMAIN_EMAIL:-"default@example.com"}
ENV DOMAIN_URL=${DOMAIN_URL:-"example.com"}

# Точка входа
CMD ["/usr/local/bin/generate-certificate.sh"]