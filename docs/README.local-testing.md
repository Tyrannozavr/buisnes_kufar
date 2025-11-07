# Локальное тестирование с nginx

## Описание

Этот набор файлов предназначен для локального тестирования приложения с nginx в качестве прокси-сервера. nginx будет проксировать запросы на локально запущенные сервисы frontend (localhost:3000) и backend (localhost:8000).

## Файлы

- `nginx/nginx.local.conf` - конфигурация nginx для локального тестирования (HTTP)
- `nginx/Dockerfile.local` - Dockerfile для сборки nginx контейнера
- `docker-compose.local.yml` - docker-compose файл для запуска только nginx

## Использование

### 1. Запуск frontend и backend локально

```bash
# В терминале 1 - Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# В терминале 2 - Frontend (Production режим для корректной работы с nginx)
cd frontend
npm run build
node .output/server/index.mjs
```

### 2. Запуск nginx в контейнере

```bash
# В корне проекта
docker-compose -f docker-compose.local.yml up --build
```

### 3. Доступ к приложению

- Приложение будет доступно по адресу: http://localhost
- nginx будет проксировать:
  - `/api/*` и `/admin/*` → localhost:8000 (backend)
  - `/_nuxt/*` и `/_ipx/*` → localhost:3000 (frontend)
  - `/uploads/*` → статические файлы из backend/uploads
  - `/` → localhost:3000 (frontend)

## Особенности конфигурации

- Используется `network_mode: "host"` для доступа к хосту из контейнера на Linux
- nginx подключается к 127.0.0.1:8000 (backend) и 127.0.0.1:3000 (frontend)
- Убраны все HTTPS настройки и SSL сертификаты
- Упрощена конфигурация для локального тестирования
- Сохранены все основные прокси настройки и WebSocket поддержка

## Важно!

1. **Frontend должен быть запущен в production режиме** - это решает проблему с неправильными путями к статическим ресурсам в dev режиме
2. **Backend должен быть запущен на всех интерфейсах (0.0.0.0)**, а не только на localhost (127.0.0.1)

```bash
# Backend должен быть запущен так:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend должен быть запущен в production режиме:
cd frontend
npm run build
node .output/server/index.mjs
```

## Решенные проблемы

- ✅ Исправлена проблема с неправильными путями к статическим ресурсам Nuxt в dev режиме
- ✅ Настроен nginx для корректной работы с production сборкой frontend
- ✅ Все статические ресурсы (_nuxt/*) теперь загружаются правильно
- ✅ Исправлена проблема с CORS - добавлен `http://localhost` в разрешенные origins
- ✅ Настроена правильная маршрутизация `/_nuxt_icon/` запросов на frontend
- ✅ API запросы теперь работают корректно через nginx прокси

## Остановка

```bash
docker-compose -f docker-compose.local.yml down
```
