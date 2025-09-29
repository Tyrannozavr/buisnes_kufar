#!/usr/bin/env python3
"""
Быстрый скрипт для заполнения базы данных минимальным набором тестовых данных
Создает 10 пользователей, 10 компаний, товары, услуги и объявления
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent))

from seed_database import DatabaseSeeder
from app.db.base import AsyncSessionLocal


async def quick_seed():
    """Быстрое заполнение базы данных минимальными данными"""
    print("🚀 Быстрое заполнение базы данных...")
    print("📊 Создастся:")
    print("   - 10 пользователей")
    print("   - 10 компаний") 
    print("   - ~80 товаров")
    print("   - ~30 услуг")
    print("   - 200 объявлений")
    print()
    
    async with AsyncSessionLocal() as session:
        seeder = DatabaseSeeder()
        seeder.session = session
        
        # Очищаем базу
        print("🧹 Очистка данных...")
        await seeder._clear_database()
        
        # Создаем только 10 пользователей
        print("👥 Создание 10 пользователей...")
        for i in range(10):
            from app.api.authentication.models.user import User
            import bcrypt
            import random
            from seed_database import FIRST_NAMES, LAST_NAMES, POSITIONS
            
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@example.com"
            
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                patronymic=random.choice(FIRST_NAMES) + "ович" if random.choice([True, False]) else None,
                phone=f"+7 9{random.randint(10, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
                inn=f"{random.randint(1000000000, 9999999999)}",
                position=random.choice(POSITIONS),
                hashed_password=bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=True
            )
            seeder.session.add(user)
            seeder.users.append(user)
        
        await seeder.session.flush()
        
        # Создаем компании
        print("🏢 Создание 10 компаний...")
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
        
        # Сохраняем
        await seeder.session.commit()
        
        print("✅ Быстрое заполнение завершено!")
        seeder._print_statistics()


if __name__ == "__main__":
    asyncio.run(quick_seed())
