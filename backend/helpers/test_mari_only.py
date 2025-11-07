#!/usr/bin/env python3
"""
Тестовый скрипт для проверки парсинга только Марий Эл
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Подключение к БД
os.environ.setdefault('POSTGRES_SERVER', 'localhost')
os.environ.setdefault('POSTGRES_USER', 'postgres')  
os.environ.setdefault('POSTGRES_PASSWORD', 'postgres')
os.environ.setdefault('POSTGRES_DB', 'buisnes_kufar')  # Название БД

sys.path.append(str(Path(__file__).parent))

from app.db.base import AsyncSessionLocal
from app.api.common.models.region import Region
from app.api.common.models.city import City
from sqlalchemy import select
import httpx
from bs4 import BeautifulSoup
import re


async def parse_cities_from_page(region_name: str, page_id: int) -> list:
    """Парсит города с одной страницы"""
    url = f"https://superresearch.ru/?id={page_id}"
    
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
        
        return unique_cities


async def test_mari():
    print("🧪 Тестирование парсинга Марий Эл\n")
    
    # Парсим
    cities = await parse_cities_from_page("Республика Марий Эл", 858)
    print(f"📍 Найдено городов на сайте: {len(cities)}")
    print(f"Список первых 10:")
    for i, city in enumerate(cities[:10]):
        print(f"  {i+1}. {city}")
    
    print(f"\n📍 Всего уникальных городов: {len(cities)}")
    
    # Проверяем в БД
    async with AsyncSessionLocal() as db:
        region_result = await db.execute(
            select(Region).where(Region.name == "Республика Марий Эл")
        )
        region = region_result.scalar_one_or_none()
        
        if not region:
            print("❌ Регион не найден")
            return
        
        print(f"\n✅ Найден регион: {region.name}")
        
        # Проверяем существующие города
        existing_result = await db.execute(
            select(City.name).where(City.region_id == region.id)
        )
        existing_names = {city[0].lower().strip() for city in existing_result.all()}
        
        print(f"📋 Уже есть в БД: {len(existing_names)}")
        
        # Новые города
        new_cities = [c for c in cities if c.lower().strip() not in existing_names]
        print(f"➕ Новых для добавления: {len(new_cities)}")
        
        if new_cities:
            print("\nПервые 20 новых городов:")
            for i, city in enumerate(new_cities[:20]):
                print(f"  {i+1}. {city}")


if __name__ == "__main__":
    asyncio.run(test_mari())

