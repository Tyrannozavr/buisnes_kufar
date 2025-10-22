# Настройка автоматического применения миграций Alembic

## Что было настроено

### 1. Entrypoint скрипт для backend контейнера
- **Файл**: `backend/entrypoint.sh`
- **Функция**: Автоматически применяет миграции Alembic при запуске контейнера
- **Логика**:
  - Ждет готовности базы данных
  - Применяет все миграции командой `alembic upgrade head`
  - Показывает статус миграций
  - Запускает основное приложение

### 2. Обновленный Dockerfile
- **Файл**: `backend/Dockerfile`
- **Изменения**:
  - Копирует `entrypoint.sh` в контейнер
  - Делает скрипт исполняемым
  - Устанавливает `ENTRYPOINT` для автоматического запуска скрипта

### 3. Скрипт для ручного применения миграций
- **Файл**: `scripts/apply_migrations.sh`
- **Функция**: Позволяет применить миграции вручную при необходимости
- **Использование**: `./scripts/apply_migrations.sh`

## Как это работает

### При развертывании на сервере:
1. **Git push** → изменения попадают в репозиторий
2. **GitHub Actions** → автоматически развертывает изменения
3. **Docker build** → собирает новый образ с миграциями
4. **Container start** → автоматически применяет миграции перед запуском приложения

### При локальной разработке:
1. **Создание миграции**: `docker compose exec backend alembic revision --autogenerate -m "описание"`
2. **Git commit** → миграция попадает в репозиторий
3. **Docker rebuild** → миграция автоматически применяется

## Проверка работы

### Логи показывают:
```
🚀 Starting backend container...
⏳ Waiting for database to be ready...
✅ Database is ready!
🔄 Applying database migrations...
INFO  [alembic.runtime.migration] Running upgrade 2ad4670bb348 -> test123456789, test local migration
✅ Migrations applied successfully!
📊 Current migration status:
test123456789 (head)
🎉 Starting FastAPI application...
```

## Преимущества

✅ **Автоматизация**: Миграции применяются автоматически при каждом развертывании  
✅ **Безопасность**: Миграции не игнорируются Git'ом  
✅ **Надежность**: Проверка готовности БД перед применением миграций  
✅ **Прозрачность**: Подробные логи процесса применения миграций  
✅ **Простота**: Одна команда `docker compose up -d --build` обновляет всё  

## Команды для работы с миграциями

```bash
# Создать новую миграцию
docker compose exec backend alembic revision --autogenerate -m "описание изменений"

# Применить миграции вручную
docker compose exec backend alembic upgrade head

# Откатить миграции
docker compose exec backend alembic downgrade -1

# Посмотреть историю миграций
docker compose exec backend alembic history

# Посмотреть текущее состояние
docker compose exec backend alembic current
```
