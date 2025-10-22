# Первый этап - сборка
FROM python:3.12-slim AS builder

WORKDIR /app

# Устанавливаем системные зависимости для сборки
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем poetry
RUN pip install --no-cache-dir poetry==1.8.2

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Копируем исходный код
COPY app/ ./app/
COPY app_logging/ ./app_logging/
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY entrypoint.sh ./entrypoint.sh

# Создаем директорию static
RUN mkdir -p ./app/static

# Делаем entrypoint скрипт исполняемым
RUN chmod +x ./entrypoint.sh


# Второй этап - итоговый образ
FROM python:3.12-slim

WORKDIR /app

# Только runtime-зависимости
RUN apt-get update && \
    apt-get install -y libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Копируем только необходимое из builder-этапа
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/app /app/app
COPY --from=builder /app/app_logging /app/app_logging
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/entrypoint.sh /app/entrypoint.sh

# Делаем entrypoint скрипт исполняемым в финальном образе
RUN chmod +x /app/entrypoint.sh

# Устанавливаем entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]