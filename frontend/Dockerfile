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

# HEALTHCHECK: node:20-slim не содержит curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s \
  CMD node -e "fetch('http://127.0.0.1:3000').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"