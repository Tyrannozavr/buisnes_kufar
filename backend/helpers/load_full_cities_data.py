#!/usr/bin/env python3
"""
Скрипт для загрузки полных данных о городах России в базу данных
"""

import asyncio
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.db.base import AsyncSessionLocal


def escape_sql_string(value):
    """Экранирует специальные символы в SQL строках"""
    return value.replace("'", "''")


async def load_full_cities_data():
    """Загружает полные данные о городах из SQL файла"""
    print("🚀 Загрузка полных данных о городах России...")
    
    sql_file = Path(__file__).parent.parent / "data_cities" / "complete_cities_db_final.sql"
    
    if not sql_file.exists():
        print(f"❌ Файл не найден: {sql_file}")
        return
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Извлекаем INSERT INTO statements
    countries_pattern = r"INSERT INTO `countries`[^;]+VALUES\s+([^;]+);"
    federal_districts_pattern = r"INSERT INTO `federal_districts`[^;]+VALUES\s+([^;]+);"
    regions_pattern = r"INSERT INTO `regions`[^;]+VALUES\s+([^;]+);"
    cities_pattern = r"INSERT INTO `cities`[^;]+VALUES\s+([^;]+);"
    
    countries_match = re.search(countries_pattern, content, re.DOTALL)
    federal_districts_match = re.search(federal_districts_pattern, content, re.DOTALL)
    regions_match = re.search(regions_pattern, content, re.DOTALL)
    cities_match = re.search(cities_pattern, content, re.DOTALL)
    
    if not countries_match or not federal_districts_match or not regions_match or not cities_match:
        print("❌ Не удалось найти данные в SQL файле")
        return
    
    # Парсим найденные данные
    def parse_insert_data(data_str):
        """Парсит строку INSERT VALUES в список кортежей"""
        records = []
        # Находим все записи между скобками
        for match in re.finditer(r'\(([^)]+)\)', data_str):
            values = match.group(1)
            # Разделяем на части, учитывая кавычки
            parts = []
            current = ""
            in_quotes = False
            quote_char = None
            
            for char in values:
                if char in ("'", '"') and not (current and current[-1] == '\\'):
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                elif char == ',' and not in_quotes:
                    parts.append(current.strip())
                    current = ""
                    continue
                
                current += char
            
            if current:
                parts.append(current.strip())
            
            # Очищаем значения от кавычек
            cleaned_parts = []
            for part in parts:
                part = part.strip().strip("'\"")
                cleaned_parts.append(part)
            
            if cleaned_parts:
                records.append(cleaned_parts)
        
        return records
    
    countries_data = parse_insert_data(countries_match.group(1))
    federal_districts_data = parse_insert_data(federal_districts_match.group(1))
    regions_data = parse_insert_data(regions_match.group(1))
    cities_data = parse_insert_data(cities_match.group(1))
    
    print(f"📊 Найдено данных:")
    print(f"   • Страны: {len(countries_data)}")
    print(f"   • Федеральные округа: {len(federal_districts_data)}")
    print(f"   • Регионы: {len(regions_data)}")
    print(f"   • Города: {len(cities_data)}")
    
    async with AsyncSessionLocal() as session:
        try:
            # Очищаем старые данные
            print("\n🧹 Очистка старых данных...")
            await session.execute(text("DELETE FROM cities"))
            await session.execute(text("DELETE FROM regions"))
            await session.execute(text("DELETE FROM federal_districts"))
            await session.execute(text("DELETE FROM countries"))
            await session.commit()
            print("✅ Старые данные удалены")
            
            # Загружаем страны
            print("\n📥 Загрузка стран...")
            for data in countries_data:
                if len(data) >= 3:
                    country_id = data[0]
                    name = escape_sql_string(data[1])
                    code = data[2]
                    
                    await session.execute(text(
                        f"INSERT INTO countries (id, name, code, is_active) VALUES ({country_id}, '{name}', '{code}', true)"
                    ))
            await session.commit()
            print(f"✅ Загружено {len(countries_data)} стран")
            
            # Загружаем федеральные округа
            print("\n📥 Загрузка федеральных округов...")
            # Маппинг округов к кодам
            district_codes = {
                'Центральный федеральный округ': 'FD1',
                'Северо-Западный федеральный округ': 'FD2',
                'Южный федеральный округ': 'FD3',
                'Дальневосточный федеральный округ': 'FD4',
                'Сибирский федеральный округ': 'FD5',
                'Уральский федеральный округ': 'FD6',
                'Приволжский федеральный округ': 'FD7',
                'Северо-Кавказский федеральный округ': 'FD8'
            }
            
            for data in federal_districts_data:
                if len(data) >= 3:
                    fd_id = data[0]
                    country_id = data[1]
                    name = escape_sql_string(data[2])
                    code = district_codes.get(name, f'FD{fd_id}')
                    
                    await session.execute(text(
                        f"INSERT INTO federal_districts (id, country_id, name, code, is_active) VALUES ({fd_id}, {country_id}, '{name}', '{code}', true)"
                    ))
            await session.commit()
            print(f"✅ Загружено {len(federal_districts_data)} федеральных округов")
            
            # Загружаем регионы
            print("\n📥 Загрузка регионов...")
            for data in regions_data:
                if len(data) >= 5:
                    region_id = data[0]
                    district_id = data[1]
                    country_id = data[2]
                    name = escape_sql_string(data[3])
                    region_type = data[4] if len(data) > 4 else ''
                    # Генерируем код региона на основе названия
                    code = name[:20].upper().replace(' ', '').replace('.', '')
                    
                    await session.execute(text(
                        f"INSERT INTO regions (id, federal_district_id, country_id, name, code, is_active) VALUES ({region_id}, {district_id}, {country_id}, '{name}', '{code}', true)"
                    ))
            await session.commit()
            print(f"✅ Загружено {len(regions_data)} регионов")
            
            # Загружаем города
            print("\n📥 Загрузка городов...")
            batch_size = 100
            for i in range(0, len(cities_data), batch_size):
                batch = cities_data[i:i+batch_size]
                
                for data in batch:
                    if len(data) >= 7:
                        city_id = data[0]
                        region_id = data[1]
                        district_id = data[2]
                        country_id = data[3]
                        name = escape_sql_string(data[4])
                        population = int(data[5]) if data[5] else 0
                        is_regional_center = data[6] == '1' or data[6] == 1
                        is_million_city = population >= 1000000
                        
                        await session.execute(text(
                            f"INSERT INTO cities (id, region_id, federal_district_id, country_id, name, population, is_million_city, is_regional_center, is_active) VALUES ({city_id}, {region_id}, {district_id}, {country_id}, '{name}', {population}, {is_million_city}, {is_regional_center}, true)"
                        ))
                
                if (i // batch_size + 1) % 10 == 0:
                    print(f"   Загружено {i + len(batch)} городов...")
                
                await session.commit()
            
            print(f"✅ Загружено {len(cities_data)} городов")
            print("\n🎉 Данные успешно загружены!")
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке данных: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(load_full_cities_data())
