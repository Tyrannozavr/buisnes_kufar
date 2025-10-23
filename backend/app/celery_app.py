import os
from celery import Celery
from celery.schedules import crontab

# Создаем экземпляр Celery
celery_app = Celery(
    "app",
    broker=os.getenv("CELERY_BROKER_URL", "amqp://admin:admin123@localhost:5672//"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "rpc://"),
    include=[
        "app.tasks.cache_tasks",
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
celery_app.conf.beat_schedule = {
    # Обновление кэша продуктов и городов каждые 30 минут
    "update-product-city-cache": {
        "task": "app.tasks.cache_tasks.update_product_city_cache",
        "schedule": crontab(minute="*/30"),  # Каждые 30 минут
    },
    # Обновление кэша компаний и городов каждые 30 минут
    "update-company-city-cache": {
        "task": "app.tasks.cache_tasks.update_company_city_cache", 
        "schedule": crontab(minute="*/30"),  # Каждые 30 минут
    },
    # Обновление количества товаров по городам каждые 15 минут
    "update-cities-product-count": {
        "task": "app.tasks.cache_tasks.update_cities_product_count",
        "schedule": crontab(minute="*/15"),  # Каждые 15 минут
    },
    # Полное обновление всех кэшей каждый час
    "refresh-all-caches": {
        "task": "app.tasks.cache_tasks.refresh_all_caches",
        "schedule": crontab(minute=0),  # Каждый час в 0 минут
    },
}

# Настройки для разработки
if os.getenv("ENVIRONMENT") == "development":
    celery_app.conf.update(
        task_always_eager=False,
        task_eager_propagates=True,
    )

if __name__ == "__main__":
    celery_app.start()
