#!/usr/bin/env python3
"""
Скрипт для тестирования Celery задач
"""

import os
import sys
import asyncio
from pathlib import Path

# Добавляем путь к приложению
sys.path.insert(0, str(Path(__file__).parent))

from app.celery_app import celery_app
from app.tasks.cache_tasks import (
    update_product_city_cache,
    update_company_city_cache,
    update_cities_product_count,
    refresh_all_caches,
    clear_all_caches
)


def test_celery_connection():
    """Тестирует подключение к Celery"""
    try:
        # Проверяем статус Celery
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print("✅ Celery подключен успешно")
            print(f"📊 Активных воркеров: {len(stats)}")
            for worker, worker_stats in stats.items():
                print(f"   - {worker}: {worker_stats.get('total', 0)} задач выполнено")
        else:
            print("❌ Celery воркеры не найдены")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к Celery: {e}")
        return False


def test_task_execution():
    """Тестирует выполнение задач"""
    try:
        print("\n🔄 Тестируем выполнение задач...")
        
        # Тестируем простую задачу
        print("1. Тестируем обновление количества товаров по городам...")
        task = update_cities_product_count.delay()
        print(f"   Задача запущена с ID: {task.id}")
        
        # Ждем результат
        result = task.get(timeout=60)
        print(f"   ✅ Результат: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка выполнения задачи: {e}")
        return False


def test_periodic_tasks():
    """Тестирует периодические задачи"""
    try:
        print("\n⏰ Проверяем периодические задачи...")
        
        # Получаем расписание
        schedule = celery_app.conf.beat_schedule
        
        if schedule:
            print("✅ Периодические задачи настроены:")
            for task_name, task_config in schedule.items():
                print(f"   - {task_name}: {task_config['schedule']}")
        else:
            print("❌ Периодические задачи не настроены")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки периодических задач: {e}")
        return False


def main():
    """Основная функция"""
    print("🚀 Тестирование Celery задач")
    print("=" * 50)
    
    # Проверяем переменные окружения
    broker_url = os.getenv("CELERY_BROKER_URL", "amqp://admin:admin123@localhost:5672//")
    print(f"📡 Broker URL: {broker_url}")
    
    # Тестируем подключение
    if not test_celery_connection():
        print("\n❌ Не удалось подключиться к Celery")
        print("💡 Убедитесь, что RabbitMQ запущен и Celery worker работает")
        return
    
    # Тестируем периодические задачи
    test_periodic_tasks()
    
    # Тестируем выполнение задач
    test_task_execution()
    
    print("\n✅ Тестирование завершено")


if __name__ == "__main__":
    main()
