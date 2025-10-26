#!/usr/bin/env python3
"""
Скрипт для добавления дополнительных продуктов в разных городах
"""

import asyncio
import random
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.api.company.models.company import Company
from app.api.common.models.city import City
from app.api.products.models.product import Product, ProductType


PRODUCT_NAMES = [
    "Цемент", "Кирпич", "Бетон", "Арматура", "Плитка", "Сайдинг", "Профнастил",
    "Гипсокартон", "Вагонка", "ОСП", "Фанера", "ДСП", "Доска", "Брус",
    "Рубероид", "Металлочерепица", "Шифер", "Керамзит", "Песок", "Щебень",
    "Радиатор", "Труба", "Фитинг", "Кран", "Смеситель", "Ванна", "Унитаз",
    "Кран", "Лейка", "Шланг", "Шланг", "Полив", "Кран", "Ковш", "Ведро"
]


SERVICE_NAMES = [
    "Укладка плитки", "Монтаж потолка", "Монтаж стен", "Утепление",
    "Покраска", "Оклейка обоями", "Штукатурка", "Сантехника",
    "Электромонтаж", "Ремонт", "Отделка", "Дизайн", "Консультация",
    "Доставка", "Погрузка", "Разгрузка", "Демонтаж", "Монтаж",
    "Установка", "Подключение"
]


UNITS_OF_MEASUREMENT = ["шт", "кг", "т", "м²", "м³", "м", "п.м", "л", "час", "день"]


async def add_products_by_cities():
    """Добавляет продукты для каждой компании из разных городов"""
    print("🚀 Добавление продуктов в разные города...")
    
    async with AsyncSessionLocal() as session:
        # Получаем все города
        result = await session.execute(select(City))
        cities = result.scalars().all()
        
        # Получаем все компании
        result = await session.execute(select(Company))
        companies = result.scalars().all()
        
        print(f"Найдено городов: {len(cities)}")
        print(f"Найдено компаний: {len(companies)}")
        
        if len(companies) == 0:
            print("❌ Нет компаний в базе данных")
            return
        
        # Создаем 20 продуктов для случайных компаний из разных городов
        products_to_add = 20
        products_created = 0
        existing_slugs = set()
        
        # Получаем существующие slug продуктов
        result = await session.execute(select(Product.slug))
        existing_slugs.update([slug for slug in result.scalars().all()])
        
        for i in range(products_to_add):
            # Выбираем случайную компанию
            company = random.choice(companies)
            
            # Выбираем случайное имя продукта или услуги
            is_service = random.random() < 0.4  # 40% услуг
            
            if is_service:
                name = random.choice(SERVICE_NAMES)
                product_type = ProductType.SERVICE
                unit = "час"
            else:
                name = random.choice(PRODUCT_NAMES)
                product_type = ProductType.GOOD
                unit = random.choice(UNITS_OF_MEASUREMENT)
            
            # Создаем уникальное имя с городом
            unique_name = f"{name} - {company.city}"
            
            # Генерируем уникальный slug
            base_slug = f"{name.lower().replace(' ', '-')}-{company.slug}"
            slug = base_slug
            counter = 1
            while slug in existing_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
            existing_slugs.add(slug)
            
            # Создаем продукт
            product = Product(
                name=unique_name,
                slug=slug,
                description=f"Качественный {name.lower()} от компании {company.name}. Доставка в {company.city}.",
                article=f"ART-{random.randint(100000, 999999)}",
                type=product_type,
                price=random.uniform(500, 50000),
                images=[],
                characteristics=[
                    {"name": "Материал", "value": random.choice(["Сталь", "Пластик", "Дерево", "Бетон"])},
                    {"name": "Размер", "value": f"{random.randint(10, 1000)}x{random.randint(10, 1000)}"},
                    {"name": "Вес", "value": f"{random.randint(1, 100)} кг"}
                ],
                is_hidden=False,
                is_deleted=False,
                unit_of_measurement=unit,
                company_id=company.id
            )
            
            session.add(product)
            products_created += 1
            
            print(f"✅ Создан продукт {products_created}/{products_to_add}: {unique_name} в городе {company.city}")
            
            # Делаем commit каждые 5 продуктов
            if products_created % 5 == 0:
                await session.commit()
                print(f"   Сохранено {products_created} продуктов...")
        
        await session.commit()
        
        print(f"\n🎉 Создано {products_created} продуктов в разных городах!")
        
        # Проверяем результаты
        result = await session.execute(select(Product))
        all_products = result.scalars().all()
        print(f"\n📊 Всего продуктов в базе: {len(all_products)}")


if __name__ == "__main__":
    asyncio.run(add_products_by_cities())

