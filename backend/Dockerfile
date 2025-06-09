# Первый этап - сборка
FROM python:3.12-slim AS builder

WORKDIR /app

# Устанавливаем системные зависимости для сборки
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv poetry==2.1.3

COPY pyproject.toml poetry.lock ./
RUN uv venv && \
    . /app/.venv/bin/activate && \
    uv pip install --no-cache-dir -e ".[dev]"

COPY app/ ./app/
COPY app_logging/ ./app_logging/

# Второй этап - итоговый образ
FROM python:3.12-slim

WORKDIR /app

# Только runtime-зависимости
RUN apt-get update && \
    apt-get install -y libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Копируем только необходимое из builder-этапа
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app
COPY --from=builder /app/app_logging /app/app_logging

# Добавляем .venv/bin в PATH
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]