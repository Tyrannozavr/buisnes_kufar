# Первый этап - сборка
FROM python:3.12-slim as builder

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

COPY src/ ./src/

# Второй этап - итоговый образ
FROM python:3.12-slim

WORKDIR /app

# Только runtime-зависимости (без gcc и dev-пакетов)
RUN apt-get update && \
    apt-get install -y libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Копируем виртуальное окружение из builder-этапа
COPY --from=builder /app /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]