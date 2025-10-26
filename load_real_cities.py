#!/usr/bin/env python3
"""
Скрипт для загрузки реальных городов из таблицы Company в таблицы City, Region, FederalDistrict
"""

import asyncio
import asyncpg
from typing import List, Dict, Set

async def load_real_cities():
    # Подключение к базе данных
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    
    try:
        # Получаем уникальные города и регионы из таблицы Company
        query = """
        SELECT DISTINCT city, region 
        FROM companies 
        WHERE city IS NOT NULL AND city != '' AND region IS NOT NULL AND region != ''
        ORDER BY city, region
        """
        
        rows = await conn.fetch(query)
        print(f"Найдено {len(rows)} уникальных комбинаций город-регион")
        
        # Создаем маппинг регионов к федеральным округам
        region_to_district = {
            # Центральный федеральный округ
            "Москва": 1,
            "Московская область": 1,
            "Тульская область": 1,
            "Тамбовская область": 1,
            "Орловская область": 1,
            "Калужская область": 1,
            "Костромская область": 1,
            "Владимирская область": 1,
            "Воронежская область": 1,
            "Ивановская область": 1,
            "Курская область": 1,
            "Липецкая область": 1,
            "Рязанская область": 1,
            "Смоленская область": 1,
            "Тверская область": 1,
            "Ярославская область": 1,
            "Белгородская область": 1,
            "Брянская область": 1,
            
            # Северо-Западный федеральный округ
            "Санкт-Петербург": 2,
            "Архангельская область": 2,
            "Вологодская область": 2,
            "Калининградская область": 2,
            "Карелия": 2,
            "Коми": 2,
            "Ленинградская область": 2,
            "Мурманская область": 2,
            "Ненецкий автономный округ": 2,
            "Новгородская область": 2,
            "Псковская область": 2,
            
            # Южный федеральный округ
            "Астраханская область": 3,
            "Волгоградская область": 3,
            "Краснодарский край": 3,
            "Ростовская область": 3,
            "Республика Адыгея": 3,
            "Республика Калмыкия": 3,
            "Крым": 3,
            "Севастополь": 3,
            
            # Дальневосточный федеральный округ
            "Амурская область": 4,
            "Еврейская автономная область": 4,
            "Забайкальский край": 4,
            "Камчатский край": 4,
            "Магаданская область": 4,
            "Приморский край": 4,
            "Республика Саха (Якутия)": 4,
            "Сахалинская область": 4,
            "Хабаровский край": 4,
            "Чукотский автономный округ": 4,
            
            # Сибирский федеральный округ
            "Алтайский край": 5,
            "Иркутская область": 5,
            "Кемеровская область": 5,
            "Красноярский край": 5,
            "Новосибирская область": 5,
            "Омская область": 5,
            "Республика Алтай": 5,
            "Республика Бурятия": 5,
            "Республика Тыва": 5,
            "Республика Хакасия": 5,
            "Томская область": 5,
            
            # Уральский федеральный округ
            "Курганская область": 6,
            "Свердловская область": 6,
            "Тюменская область": 6,
            "Ханты-Мансийский автономный округ": 6,
            "Ямало-Ненецкий автономный округ": 6,
            "Челябинская область": 6,
            
            # Приволжский федеральный округ
            "Кировская область": 7,
            "Нижегородская область": 7,
            "Оренбургская область": 7,
            "Пензенская область": 7,
            "Пермский край": 7,
            "Республика Башкортостан": 7,
            "Республика Марий Эл": 7,
            "Республика Мордовия": 7,
            "Республика Татарстан": 7,
            "Самарская область": 7,
            "Саратовская область": 7,
            "Удмуртская Республика": 7,
            "Чувашская Республика": 7,
            
            # Северо-Кавказский федеральный округ
            "Ставропольский край": 8,
            "Республика Дагестан": 8,
            "Республика Ингушетия": 8,
            "Кабардино-Балкарская Республика": 8,
            "Карачаево-Черкесская Республика": 8,
            "Республика Северная Осетия": 8,
            "Чеченская Республика": 8,
        }
        
        # Собираем уникальные регионы
        unique_regions = set()
        for row in rows:
            unique_regions.add(row['region'])
        
        print(f"Найдено {len(unique_regions)} уникальных регионов")
        
        # Вставляем регионы
        for region_name in sorted(unique_regions):
            district_id = region_to_district.get(region_name, 1)  # По умолчанию Центральный округ
            
            # Определяем тип региона
            region_type = "область"
            if "край" in region_name.lower():
                region_type = "край"
            elif "республика" in region_name.lower():
                region_type = "республика"
            elif "округ" in region_name.lower():
                region_type = "округ"
            elif region_name in ["Москва", "Санкт-Петербург"]:
                region_type = "город"
            
            await conn.execute("""
                INSERT INTO regions (district_id, country_id, name, type)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT DO NOTHING
            """, district_id, 1, region_name, region_type)
        
        # Получаем ID регионов
        region_ids = {}
        region_rows = await conn.fetch("SELECT id, name FROM regions")
        for row in region_rows:
            region_ids[row['name']] = row['id']
        
        # Вставляем города
        city_count = 0
        for row in rows:
            region_id = region_ids.get(row['region'])
            if region_id:
                district_id = region_to_district.get(row['region'], 1)
                
                await conn.execute("""
                    INSERT INTO cities (region_id, district_id, country_id, name, population, is_capital)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT DO NOTHING
                """, region_id, district_id, 1, row['city'], 0, False)
                city_count += 1
        
        print(f"Загружено {city_count} городов")
        
        # Проверяем результат
        cities_count = await conn.fetchval("SELECT COUNT(*) FROM cities")
        regions_count = await conn.fetchval("SELECT COUNT(*) FROM regions")
        
        print(f"Итого в базе: {cities_count} городов, {regions_count} регионов")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(load_real_cities())

