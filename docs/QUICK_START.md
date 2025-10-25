## Инструкция по запуску RabbitMQ и Celery

### 1. Запуск всех сервисов (development)
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 2. Проверка статуса сервисов
```bash
docker-compose -f docker-compose.dev.yml ps
```

### 3. Мониторинг
- **RabbitMQ Management UI**: http://localhost:15672 (admin/admin123)
- **API документация**: http://localhost:8000/docs
- **Celery API**: http://localhost:8000/api/v1/celery/

### 4. Тестирование
```bash
cd backend
python test_celery.py
```

### 5. Логи
```bash
# Логи всех сервисов
docker-compose -f docker-compose.dev.yml logs -f

# Логи конкретного сервиса
docker-compose -f docker-compose.dev.yml logs -f celery-worker
docker-compose -f docker-compose.dev.yml logs -f celery-beat
docker-compose -f docker-compose.dev.yml logs -f rabbitmq
```

### 6. Остановка
```bash
docker-compose -f docker-compose.dev.yml down
```

## Периодические задачи

- **Обновление кэша продуктов и городов**: каждые 30 минут
- **Обновление кэша компаний и городов**: каждые 30 минут  
- **Обновление количества товаров по городам**: каждые 15 минут
- **Полное обновление всех кэшей**: каждый час

## API для ручного запуска задач

- POST /api/v1/celery/tasks/update-product-city-cache
- POST /api/v1/celery/tasks/update-company-city-cache
- POST /api/v1/celery/tasks/update-cities-product-count
- POST /api/v1/celery/tasks/refresh-all-caches
- POST /api/v1/celery/tasks/clear-all-caches

## Мониторинг задач

- GET /api/v1/celery/tasks/{task_id} - статус задачи
- GET /api/v1/celery/tasks - активные задачи
- GET /api/v1/celery/stats - статистика Celery

