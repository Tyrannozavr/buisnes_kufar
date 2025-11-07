# Backend API

Backend API для системы управления бизнесом.

## Технологии

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Argon2 для хеширования паролей
- JWT токены

## Установка

```bash
# Установка зависимостей через Poetry
poetry install

# Или через pip
pip install -r requirements.txt
```

## Запуск

```bash
# Активация виртуального окружения
source new_venv/bin/activate

# Запуск сервера
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Хеширование паролей

Проект использует Argon2 для безопасного хеширования паролей вместо bcrypt для лучшей производительности и безопасности.
