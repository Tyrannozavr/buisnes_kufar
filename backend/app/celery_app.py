import os
from celery import Celery
from celery.schedules import crontab

# Создаем экземпляр Celery
celery_app = Celery(
    "app",
    broker=os.getenv("CELERY_BROKER_URL", "amqp://admin:admin123@localhost:5672//"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "rpc://"),
    include=[
        # Удалены задачи кэширования - теперь используется прямой JOIN
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
)

# Периодические задачи (Celery Beat)
# Убраны задачи кэширования - теперь используется JOIN напрямую через API
celery_app.conf.beat_schedule = {
    # Задачи кэширования удалены - теперь используется прямая выборка через JOIN
}

# Настройки для разработки
if os.getenv("ENVIRONMENT") == "development":
    celery_app.conf.update(
        task_always_eager=False,
        task_eager_propagates=True,
    )

if __name__ == "__main__":
    celery_app.start()
