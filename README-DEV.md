# Docker Compose для разработки

Этот файл `docker-compose-dev.yml` предназначен для разработки и отличается от продакшн версии следующими особенностями:

## Основные отличия от продакшн версии:

### 1. **Volumes вместо COPY**
- Исходный код пробрасывается через volumes для hot reload
- Изменения в коде сразу отражаются в контейнерах без пересборки
- Отдельные именованные тома для кэша и данных

### 2. **Открытые порты**
- **Backend**: `8000` - прямой доступ к FastAPI
- **Frontend**: `3000` - прямой доступ к Nuxt.js dev server
- **Database**: `5432` - прямой доступ к PostgreSQL
- **PgAdmin**: `5050` - веб-интерфейс для управления БД
- **Nginx**: `80` - основной веб-сервер

### 3. **Инструменты разработки**
- **PgAdmin** включен для удобного управления базой данных
- **Hot reload** для backend и frontend
- **Health checks** для всех сервисов
- **Resource limits** для оптимизации производительности

### 4. **Переменные окружения для разработки**
- `DEBUG=true`
- `RELOAD=true`
- `PYTHONUNBUFFERED=1`
- `PYTHONDONTWRITEBYTECODE=1`
- `NODE_ENV=development`

### 5. **Именованные тома**
- `postgres_data_dev` - данные PostgreSQL
- `pgadmin_data` - данные PgAdmin
- `backend_logs` - логи backend
- `backend_cache` - кэш backend
- `backend_uploads` - загруженные файлы
- `backend_static` - статические файлы
- `frontend_nuxt_cache` - кэш Nuxt
- `frontend_output_cache` - кэш сборки
- `frontend_node_modules` - зависимости Node.js
- `pip_cache` - кэш pip
- `npm_cache` - кэш npm

## Запуск:

```bash
# Запуск всех сервисов
docker-compose -f docker-compose-dev.yml up -d

# Просмотр логов
docker-compose -f docker-compose-dev.yml logs -f

# Просмотр логов конкретного сервиса
docker-compose -f docker-compose-dev.yml logs -f backend

# Остановка
docker-compose -f docker-compose-dev.yml down

# Остановка с удалением volumes (ОСТОРОЖНО: удалит данные БД)
docker-compose -f docker-compose-dev.yml down -v
```

## Доступ к сервисам:

- **Основной сайт**: http://localhost
- **API документация**: http://localhost:8000/docs
- **Админка**: http://localhost:8000/admin
- **PgAdmin**: http://localhost:5050
  - Email: admin@tradesynergy.dev
  - Password: admin123
- **Прямой доступ к фронтенду**: http://localhost:3000
- **Прямой доступ к API**: http://localhost:8000

## Подключение к базе данных:

```bash
# Через psql
psql -h localhost -p 5432 -U postgres -d postgres

# Или через любой PostgreSQL клиент
Host: localhost
Port: 5432
Database: postgres
Username: postgres
Password: postgres
```

## Hot Reload:

- **Backend**: Изменения в Python коде автоматически перезагружают сервер
- **Frontend**: Изменения в Vue/Nuxt коде автоматически обновляют страницу
- **База данных**: Данные сохраняются в именованном томе `postgres_data_dev`

## Полезные команды:

```bash
# Пересборка конкретного сервиса
docker-compose -f docker-compose-dev.yml build backend

# Перезапуск конкретного сервиса
docker-compose -f docker-compose-dev.yml restart backend

# Просмотр статуса сервисов
docker-compose -f docker-compose-dev.yml ps

# Просмотр использования ресурсов
docker-compose -f docker-compose-dev.yml top

# Выполнение команд в контейнере
docker-compose -f docker-compose-dev.yml exec backend bash
docker-compose -f docker-compose-dev.yml exec frontend sh

# Просмотр логов с фильтрацией
docker-compose -f docker-compose-dev.yml logs --tail=100 -f backend

# Очистка неиспользуемых ресурсов
docker system prune -f
docker volume prune -f
```

## Мониторинг и отладка:

- **Health checks** настроены для всех сервисов
- **Resource limits** предотвращают чрезмерное использование ресурсов
- **Structured logging** для лучшей отладки
- **PgAdmin** для визуального управления БД

## Производительность:

- **Кэширование** pip и npm для ускорения установки пакетов
- **Именованные тома** для быстрого доступа к данным
- **Resource limits** для оптимального использования ресурсов
- **Cached volumes** для ускорения работы с файлами
