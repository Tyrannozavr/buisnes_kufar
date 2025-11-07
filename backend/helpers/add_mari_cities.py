#!/usr/bin/env python3
"""
Скрипт для добавления городов Республики Марий Эл в базу данных
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Устанавливаем переменные окружения перед импортом
os.environ.setdefault('POSTGRES_SERVER', 'localhost')
os.environ.setdefault('POSTGRES_USER', 'postgres')
os.environ.setdefault('POSTGRES_PASSWORD', 'postgres')
os.environ.setdefault('POSTGRES_DB', 'business_trade')

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent))

from app.db.base import AsyncSessionLocal
from app.api.common.models.region import Region
from app.api.common.models.city import City
from sqlalchemy import select


async def add_mari_cities():
    """Добавляем города Марий Эл"""
    print("🗺️ Добавляем города Республики Марий Эл...")
    
    # Данные о городах Марий Эл
    mari_cities = [
        {
            "name": "Йошкар-Ола",
            "population": 280000,
            "is_million_city": False,
            "is_regional_center": True
        },
        {
            "name": "Волжск",
            "population": 54000,
            "is_million_city": False,
            "is_regional_center": False
        },
        {
            "name": "Козьмодемьянск",
            "population": 20000,
            "is_million_city": False,
            "is_regional_center": False
        },
        {
            "name": "Звенигово",
            "population": 12000,
            "is_million_city": False,
            "is_regional_center": False
        },
        {
            "name": "Советский",
            "population": 11000,
            "is_million_city": False,
            "is_regional_center": False
        },
        {
            "name": "Морки",
            "population": 10000,
            "is_million_city": False,
            "is_regional_center": False
        },
        {
            "name": "Юрино",
            "population": 4000,
            "is_million_city": False,
            "is_regional_center": False
        }
    ]
    
    async with AsyncSessionLocal() as db:
        # Находим регион "Республика Марий Эл"
        region_result = await db.execute(
            select(Region)
            .where(Region.name == "Республика Марий Эл")
        )
        region = region_result.scalar_one_or_none()
        
        if not region:
            print("❌ Регион 'Республика Марий Эл' не найден в базе данных")
            return
        
        print(f"✅ Найден регион: {region.name} (ID: {region.id}, Федеральный округ ID: {region.federal_district_id})")
        
        added_count = 0
        for city_data in mari_cities:
            # Проверяем, существует ли город
            city_result = await db.execute(
                select(City)
                .where(City.name == city_data["name"])
                .where(City.region_id == region.id)
            )
            existing_city = city_result.scalar_one_or_none()
            
            if existing_city:
                print(f"⚠️  Город {city_data['name']} уже существует (ID: {existing_city.id})")
                continue
            
            # Создаем новый город
            new_city = City(
                region_id=region.id,
                federal_district_id=region.federal_district_id,
                country_id=region.country_id,
                name=city_data["name"],
                population=city_data["population"],
                is_million_city=city_data["is_million_city"],
                is_regional_center=city_data["is_regional_center"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_city)
            added_count += 1
            print(f"✅ Добавлен город: {city_data['name']} (население: {city_data['population']})")
        
        await db.commit()
        print(f"\n🎉 Всего добавлено/проверено: {added_count} новых городов")
    
    # Проверяем результат
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(City)
            .join(Region)
            .where(Region.name == "Республика Марий Эл")
        )
        cities = result.scalars().all()
        print(f"\n📊 Всего городов в Республике Марий Эл: {len(cities)}")
        print("\nСписок городов:")
        for city in sorted(cities, key=lambda x: x.population or 0, reverse=True):
            print(f"  - {city.name} (население: {city.population or 'не указано'})")


if __name__ == "__main__":
    asyncio.run(add_mari_cities())

