# RabbitMQ и Celery для фоновых задач

## Описание

Реализована система фоновых задач с использованием RabbitMQ и Celery для автоматического обновления кэш-таблиц отношений продуктов-городов и компаний-городов.

## Компоненты

### 1. RabbitMQ
- **Порт**: 5672 (AMQP), 15672 (Management UI)
- **Учетные данные**: admin/admin123
- **Management UI**: http://localhost:15672

### 2. Celery Worker
- Обрабатывает фоновые задачи
- Автоматически перезапускается при сбоях

### 3. Celery Beat
- Планировщик периодических задач
- Выполняет задачи по расписанию

## Периодические задачи

### Обновление кэша продуктов и городов
- **Частота**: каждые 30 минут
- **Задача**: `update_product_city_cache`
- **Описание**: Обновляет таблицу `ProductCityMapping` и `ActiveCitiesCache`

### Обновление кэша компаний и городов
- **Частота**: каждые 30 минут
- **Задача**: `update_company_city_cache`
- **Описание**: Обновляет таблицу `ActiveCitiesCache` для компаний

### Обновление количества товаров по городам
- **Частота**: каждые 15 минут
- **Задача**: `update_cities_product_count`
- **Описание**: Подсчитывает количество товаров, услуг и компаний по городам

### Полное обновление всех кэшей
- **Частота**: каждый час
- **Задача**: `refresh_all_caches`
- **Описание**: Выполняет все обновления кэшей последовательно

## API Endpoints

### Запуск задач вручную

```bash
# Обновление кэша продуктов и городов
POST /api/v1/celery/tasks/update-product-city-cache

# Обновление кэша компаний и городов
POST /api/v1/celery/tasks/update-company-city-cache

# Обновление количества товаров по городам
POST /api/v1/celery/tasks/update-cities-product-count

# Полное обновление всех кэшей
POST /api/v1/celery/tasks/refresh-all-caches

# Очистка всех кэшей
POST /api/v1/celery/tasks/clear-all-caches
```

### Мониторинг задач

```bash
# Получение статуса задачи
GET /api/v1/celery/tasks/{task_id}

# Список активных задач
GET /api/v1/celery/tasks

# Статистика Celery
GET /api/v1/celery/stats
```

## Запуск

### Development
```bash
# Запуск всех сервисов
docker-compose -f docker-compose.dev.yml up -d

# Проверка статуса
docker-compose -f docker-compose.dev.yml ps
```

### Production
```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

## Мониторинг

### RabbitMQ Management UI
- URL: http://localhost:15672
- Логин: admin
- Пароль: admin123

### Логи Celery
```bash
# Логи worker
docker-compose logs -f celery-worker

# Логи beat
docker-compose logs -f celery-beat

# Логи RabbitMQ
docker-compose logs -f rabbitmq
```

## Тестирование

### Запуск тестового скрипта
```bash
cd backend
python test_celery.py
```

### Ручное тестирование через API
```bash
# Запуск задачи
curl -X POST http://localhost:8000/api/v1/celery/tasks/update-cities-product-count

# Проверка статуса
curl http://localhost:8000/api/v1/celery/tasks/{task_id}
```

## Структура кэш-таблиц

### ActiveCitiesCache
- `cache_type`: тип кэша (products, companies)
- `active_city_ids`: список ID активных городов
- `total_cities`: общее количество городов
- `total_companies`: общее количество компаний
- `total_products`: общее количество продуктов
- `last_updated`: время последнего обновления

### ProductCityMapping
- `product_id`: ID продукта
- `city_id`: ID города компании
- `company_id`: ID компании
- `created_at`: время создания записи

## Настройка

### Переменные окружения
```env
CELERY_BROKER_URL=amqp://admin:admin123@rabbitmq:5672//
CELERY_RESULT_BACKEND=rpc://
```

### Изменение расписания
Отредактируйте файл `backend/app/celery_app.py` в секции `beat_schedule`.

## Устранение неполадок

### Celery worker не запускается
1. Проверьте подключение к RabbitMQ
2. Убедитесь, что все зависимости установлены
3. Проверьте логи: `docker-compose logs celery-worker`

### Задачи не выполняются
1. Проверьте статус RabbitMQ: http://localhost:15672
2. Убедитесь, что worker запущен: `docker-compose ps`
3. Проверьте логи: `docker-compose logs celery-worker`

### Периодические задачи не работают
1. Убедитесь, что Celery Beat запущен: `docker-compose ps`
2. Проверьте логи: `docker-compose logs celery-beat`
3. Проверьте настройки в `celery_app.py`
