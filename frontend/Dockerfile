# Этап сборки
FROM node:20-slim AS builder

WORKDIR /app

# Копируем только файлы, необходимые для установки зависимостей
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm ci --omit=dev && npm cache clean --force

# Копируем остальные файлы
COPY . .

# Сборка проекта
ENV NUXT_UI_FONTS=false
RUN npm run build

# Удаляем ненужные файлы после сборки, но оставляем node_modules
RUN rm -rf ./src ./test ./*.md ./.github

# Финальный этап
FROM node:20-slim

WORKDIR /app

# Копируем только необходимое из builder-этапа
COPY --from=builder /app /app

# Создаем непривилегированного пользователя
RUN groupadd -r appuser && \
    useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

# Используем exec-form для корректной обработки сигналов
CMD ["npm", "run", "start"]

# HEALTHCHECK для мониторинга
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:3000/ || exit 1