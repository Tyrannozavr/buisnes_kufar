#!/usr/bin/env python3
"""
Скрипт для создания компаний в разных городах и продуктов для них
"""

import asyncio
import random
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.api.company.models.company import Company, BusinessType, TradeActivity
from app.api.common.models.city import City
from app.api.products.models.product import Product, ProductType


COMPANY_NAMES = [
    "СтройМаркет", "СтройСервис", "СтройГарант", "СтройЭксперт",
    "СтройПлюс", "СтройПро", "СтройЛогистик", "СтройЦентр",
    "СтройКонсалт", "СтройИмпорт", "СтройТех", "СтройСнаб",
    "СтройТорг", "СтройОпт", "СтройХоз", "СтройТрейд",
    "СтройКомплект", "СтройАльянс", "СтройФорум", "СтройДом"
]

PRODUCT_NAMES = [
    "Цемент", "Кирпич", "Бетон", "Арматура", "Плитка", "Сайдинг",
    "Профнастил", "Гипсокартон", "Вагонка", "ОСП", "Фанера",
    "ДСП", "Доска", "Брус", "Рубероид", "Металлочерепица"
]

SERVICE_NAMES = [
    "Укладка плитки", "Монтаж потолка", "Монтаж стен", "Утепление",
    "Покраска", "Оклейка обоями", "Штукатурка", "Сантехника"
]

UNITS = ["шт", "кг", "т", "м²", "м³", "м", "п.м"]

def generate_slug(name: str) -> str:
    """Генерирует slug из названия"""
    import re
    return re.sub(r'[^\w\s-]', '', name.lower()).strip().replace(' ', '-')


async def create_companies_in_cities():
    """Создает компании в разных городах и продукты для них"""
    print("🚀 Создание компаний в разных городах...")
    
    async with AsyncSessionLocal() as session:
        # Получаем случайные города
        result = await session.execute(select(City).limit(10).offset(random.randint(0, 2600)))
        cities = result.scalars().all()
        
        if len(cities) == 0:
            print("❌ Не найдено городов в базе данных")
            return
        
        print(f"Найдено {len(cities)} городов")
        
        companies_created = 0
        products_created = 0
        existing_slugs = set()
        
        for i, city in enumerate(cities):
            # Генерируем уникальное название компании
            base_name = random.choice(COMPANY_NAMES)
            name = f"{base_name} {i+1}"
            
            # Генерируем уникальный slug
            base_slug = generate_slug(name)
            slug = base_slug
            counter = 1
            while slug in existing_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
            existing_slugs.add(slug)
            
            # Создаем компанию
            company = Company(
                name=name,
                slug=slug,
                type="ООО",
                trade_activity=random.choice(list(TradeActivity)),
                business_type=random.choice(list(BusinessType)),
                activity_type="Строительство",
                description=f"Компания {name} в городе {city.name}",
                country="Россия",
                federal_district="",
                region="",
                city=city.name,
                country_id=1,
                federal_district_id=city.federal_district_id,
                region_id=city.region_id,
                city_id=city.id,
                full_name=f"{name} - полное наименование",
                inn=f"{random.randint(1000000000, 9999999999)}",
                ogrn=f"{random.randint(1000000000000, 9999999999999)}",
                kpp=f"{random.randint(100000000, 999999999)}",
                registration_date=datetime.now(),
                legal_address=f"г. {city.name}, ул. Строительная, д. {random.randint(1, 100)}",
                production_address=f"г. {city.name}, ул. Промышленная, д. {random.randint(1, 100)}",
                phone=f"+7{random.randint(9100000000, 9999999999)}",
                email=f"{generate_slug(name)}@mail.ru",
                website=f"https://{generate_slug(name)}.ru",
                total_views=0,
                monthly_views=0,
                total_purchases=0,
                is_active=True
            )
            
            session.add(company)
            await session.flush()
            companies_created += 1
            
            print(f"✅ Создана компания {companies_created}: {name} в {city.name}")
            
            # Создаем 2-3 продукта для каждой компании
            num_products = random.randint(2, 3)
            for j in range(num_products):
                is_service = random.random() < 0.4
                
                if is_service:
                    product_name = random.choice(SERVICE_NAMES)
                    product_type = ProductType.SERVICE
                    unit = "час"
                else:
                    product_name = random.choice(PRODUCT_NAMES)
                    product_type = ProductType.GOOD
                    unit = random.choice(UNITS)
                
                unique_name = f"{product_name} {city.name}"
                
                # Генерируем уникальный slug для продукта
                base_slug = generate_slug(unique_name)
                slug_prod = base_slug
                counter = 1
                while slug_prod in existing_slugs:
                    slug_prod = f"{base_slug}-{counter}"
                    counter += 1
                existing_slugs.add(slug_prod)
                
                product = Product(
                    name=unique_name,
                    slug=slug_prod,
                    description=f"Качественный {product_name.lower()} в городе {city.name}",
                    article=f"ART-{random.randint(100000, 999999)}",
                    type=product_type,
                    price=random.uniform(1000, 50000),
                    images=[],
                    characteristics=[
                        {"name": "Материал", "value": "Качественный"},
                        {"name": "Размер", "value": "Стандартный"}
                    ],
                    is_hidden=False,
                    is_deleted=False,
                    unit_of_measurement=unit,
                    company_id=company.id
                )
                
                session.add(product)
                products_created += 1
            
            # Делаем commit каждые 5 компаний
            if companies_created % 5 == 0:
                await session.commit()
                print(f"   Сохранено {companies_created} компаний с {products_created} продуктами...")
        
        await session.commit()
        
        print(f"\n🎉 Создано {companies_created} компаний с {products_created} продуктами в разных городах!")


if __name__ == "__main__":
    asyncio.run(create_companies_in_cities())

