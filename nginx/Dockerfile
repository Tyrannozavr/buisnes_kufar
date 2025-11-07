# Убедитесь что базовый образ есть локально
FROM nginx:latest AS builder

# Ваши команды
RUN rm /etc/nginx/conf.d/default.conf

# Финальный образ
FROM nginx:latest
COPY --from=builder /etc/nginx /etc/nginx
COPY nginx.conf /etc/nginx/conf.d/