#!/usr/bin/env python3
"""
Универсальный скрипт для добавления городов для любого региона России
Не указываем ID явно - БД автоинкрементирует
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
import re

sys.path.insert(0, str(Path(__file__).parent))

from app.db.base import AsyncSessionLocal
from app.api.common.models.region import Region
from app.api.common.models.city import City
from sqlalchemy import select


async def parse_cities_from_superresearch(page_id: int):
    """Парсит города с superresearch.ru по page_id"""
    url = f"https://superresearch.ru/?id={page_id}"
    
    print(f"📡 Парсим города с {url}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        full_text = soup.get_text()
        
        pattern = r'Города\s+.*?\s+в\s+алфавитном\s+порядке:'
        match = re.search(pattern, full_text)
        
        cities = []
        
        if match:
            start_pos = match.end()
            text_after_marker = full_text[start_pos:]
            lines = text_after_marker.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if len(line) > 2 and len(line) < 60 and line[0].isupper():
                    if not any(skip in line for skip in ['©', 'Тел.', 'Россия', 'ул.', 'д.', 'п.', '+7']):
                        cities.append(line)
                        if '©' in line or 'Тел.' in line:
                            break
        
        # Удаляем дубликаты
        unique_cities = []
        seen = set()
        for city in cities:
            city_normalized = ' '.join(city.split()).strip()
            if 2 < len(city_normalized) < 50 and any(c.isalpha() for c in city_normalized):
                city_key = city_normalized.lower()
                if city_key not in seen:
                    seen.add(city_key)
                    unique_cities.append(city_normalized)
        
        print(f"✅ Найдено уникальных городов: {len(unique_cities)}")
        if unique_cities:
            print("Первые 10 городов:")
            for i, city in enumerate(unique_cities[:10], 1):
                print(f"  {i}. {city}")
        
        return unique_cities


async def add_cities_for_region(region_name: str, page_id: int):
    """Добавляет города для конкретного региона"""
    
    print(f"\n{'='*60}")
    print(f"🌍 Добавление городов для: {region_name}")
    print(f"{'='*60}\n")
    
    # Парсим города
    cities_list = await parse_cities_from_superresearch(page_id)
    
    if not cities_list:
        print("❌ Не удалось получить города")
        return
    
    async with AsyncSessionLocal() as db:
        # Находим регион
        region_result = await db.execute(
            select(Region).where(Region.name == region_name)
        )
        region = region_result.scalar_one_or_none()
        
        if not region:
            print(f"❌ Регион '{region_name}' не найден в БД")
            return
        
        print(f"✅ Найден регион: {region.name} (ID: {region.id})")
        
        # Получаем существующие города
        existing_result = await db.execute(
            select(City.name).where(City.region_id == region.id)
        )
        existing_names = {city[0].lower().strip() for city in existing_result.all()}
        
        print(f"📊 Уже есть в БД: {len(existing_names)} городов")
        
        # Добавляем новые (БЕЗ указания ID - автоинкремент)
        added_count = 0
        skipped_count = 0
        
        for city_name in cities_list:
            city_key = city_name.lower().strip()
            
            if city_key in existing_names:
                skipped_count += 1
                continue
            
            new_city = City(
                # НЕ указываем id - автоинкремент!
                region_id=region.id,
                federal_district_id=region.federal_district_id,
                country_id=region.country_id,
                name=city_name,
                population=0,
                is_million_city=False,
                is_regional_center=False,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(new_city)
            added_count += 1
            existing_names.add(city_key)
        
        await db.commit()
        
        print(f"\n✅ Добавлено новых городов: {added_count}")
        print(f"⏭️  Пропущено (уже существуют): {skipped_count}")
        
        # Финальная проверка
        result = await db.execute(
            select(City).where(City.region_id == region.id)
        )
        total_cities = result.scalars().all()
        print(f"🎉 Всего городов: {len(total_cities)}")


async def main():
    # Ярославская обл. - меньше всего городов (23)
    # ID на superresearch.ru для Ярославской области: 810
    await add_cities_for_region("Ярославская обл.", 810)


if __name__ == "__main__":
    asyncio.run(main())

