#!/usr/bin/env python3
"""
Скрипт для запуска заполнения базы данных с различными параметрами
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent))

from seed_database import DatabaseSeeder


async def run_seed(clear_existing: bool = True, users_count: int = 50):
    """
    Запуск заполнения базы данных
    
    Args:
        clear_existing: Очищать ли существующие данные
        users_count: Количество пользователей для создания
    """
    print(f"🚀 Запуск заполнения базы данных...")
    print(f"📊 Параметры:")
    print(f"   - Очистка существующих данных: {'Да' if clear_existing else 'Нет'}")
    print(f"   - Количество пользователей: {users_count}")
    print(f"   - Количество компаний: {users_count}")
    print(f"   - Примерное количество товаров: {users_count * 8}")
    print(f"   - Примерное количество услуг: {users_count * 3}")
    print(f"   - Количество объявлений: 200")
    print()
    
    seeder = DatabaseSeeder()
    if clear_existing:
        await seeder._clear_database()
    
    # Создаем пользователей
    print("👥 Создание пользователей...")
    await seeder._create_users()
    
    # Создаем компании
    print("🏢 Создание компаний...")
    await seeder._create_companies()
    
    # Создаем товары
    print("📦 Создание товаров...")
    await seeder._create_products()
    
    # Создаем услуги
    print("🔧 Создание услуг...")
    await seeder._create_services()
    
    # Создаем объявления
    print("📢 Создание объявлений...")
    await seeder._create_announcements()
    
    # Сохраняем изменения
    await seeder.session.commit()
    
    print("✅ Тестовые данные успешно добавлены!")
    seeder._print_statistics()


def main():
    """Главная функция с обработкой аргументов командной строки"""
    parser = argparse.ArgumentParser(description="Заполнение базы данных тестовыми данными")
    parser.add_argument(
        "--no-clear", 
        action="store_true", 
        help="Не очищать существующие данные"
    )
    parser.add_argument(
        "--users", 
        type=int, 
        default=50, 
        help="Количество пользователей для создания (по умолчанию: 50)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Показать что будет создано без выполнения"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 Режим предварительного просмотра:")
        print(f"   - Пользователей: {args.users}")
        print(f"   - Компаний: {args.users}")
        print(f"   - Товаров: ~{args.users * 8}")
        print(f"   - Услуг: ~{args.users * 3}")
        print(f"   - Объявлений: 200")
        print(f"   - Очистка данных: {'Нет' if args.no_clear else 'Да'}")
        return
    
    # Запускаем заполнение
    asyncio.run(run_seed(
        clear_existing=not args.no_clear,
        users_count=args.users
    ))


if __name__ == "__main__":
    main()
