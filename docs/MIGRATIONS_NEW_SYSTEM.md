# Система миграций базы данных

## Обзор

Теперь миграции базы данных выполняются через отдельный контейнер, что позволяет серверу работать даже если миграции не применены.

## Структура

- **`backend/Dockerfile.migrations`** - Dockerfile для контейнера миграций
- **`scripts/run_migrations.sh`** - Скрипт для ручного запуска миграций
- **Сервис `migrations`** в docker-compose файлах

## Использование

### Автоматический запуск миграций

Для запуска миграций используйте профиль `migrations`:

```bash
# Production
docker compose --profile migrations up migrations

# Development
docker compose -f docker-compose.dev.yml --profile migrations up migrations
```

### Ручной запуск миграций

Используйте скрипт `scripts/run_migrations.sh`:

```bash
# Production
./scripts/run_migrations.sh

# Development
./scripts/run_migrations.sh dev
```

### Проверка статуса миграций

```bash
# Production
docker compose exec backend alembic current

# Development
docker compose -f docker-compose.dev.yml exec backend alembic current
```

## Процесс деплоя

1. **Локально**: Создайте миграции
   ```bash
   cd backend
   alembic revision --autogenerate -m "описание изменений"
   ```

2. **Коммит**: Заливайте изменения в Git
   ```bash
   git add .
   git commit -m "Add migration: описание"
   git push
   ```

3. **На сервере**: 
   ```bash
   git pull
   docker compose up -d --build
   ./scripts/run_migrations.sh
   ```

## Преимущества новой системы

- ✅ **Сервер работает независимо** от состояния миграций
- ✅ **Контролируемый процесс** применения миграций
- ✅ **Безопасность** - миграции не блокируют запуск приложения
- ✅ **Гибкость** - можно применять миграции в любое время
- ✅ **Откат** - легко откатить миграции при необходимости

## Troubleshooting

### Если миграции не применяются

1. Проверьте статус базы данных:
   ```bash
   docker compose ps db
   ```

2. Проверьте логи миграций:
   ```bash
   docker compose logs migrations
   ```

3. Запустите миграции вручную:
   ```bash
   ./scripts/run_migrations.sh
   ```

### Если таблицы уже существуют

Миграция `b81e833cc420_create_location_tables_manually.py` была исправлена для проверки существования таблиц перед их созданием.

## Команды Alembic

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "описание"

# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Показать текущую версию
alembic current

# Показать историю миграций
alembic history
```
