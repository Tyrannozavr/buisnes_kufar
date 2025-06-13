# Убедитесь что базовый образ есть локально
FROM nginx:1.25 AS builder

# Ваши команды
RUN rm /etc/nginx/conf.d/default.conf

# Финальный образ
FROM nginx:1.25
COPY --from=builder /etc/nginx /etc/nginx
COPY nginx.conf /etc/nginx/conf.d/
COPY letsencrypt /etc/nginx/letsencrypt/