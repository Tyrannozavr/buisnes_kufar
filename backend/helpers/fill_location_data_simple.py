#!/usr/bin/env python3
"""
Упрощенный скрипт для заполнения таблиц локаций тестовыми данными
"""
import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append('/app')

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.base import AsyncSessionLocal


async def fill_test_data():
    """Заполняем таблицы тестовыми данными"""
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. Создаем страны
            countries_data = [
                {"code": "RU", "name": "Россия"},
                {"code": "BY", "name": "Беларусь"},
                {"code": "KZ", "name": "Казахстан"},
                {"code": "UA", "name": "Украина"},
            ]
            
            countries = {}
            for country_data in countries_data:
                result = await session.execute(
                    text("INSERT INTO countries (code, name, is_active) VALUES (:code, :name, :is_active) RETURNING id"),
                    {"code": country_data["code"], "name": country_data["name"], "is_active": True}
                )
                country_id = result.scalar()
                countries[country_data["code"]] = country_id
            
            # 2. Создаем федеральные округа для России
            federal_districts_data = [
                {"country_code": "RU", "name": "Центральный федеральный округ", "code": "ЦФО"},
                {"country_code": "RU", "name": "Северо-Западный федеральный округ", "code": "СЗФО"},
                {"country_code": "RU", "name": "Южный федеральный округ", "code": "ЮФО"},
                {"country_code": "RU", "name": "Приволжский федеральный округ", "code": "ПФО"},
                {"country_code": "RU", "name": "Уральский федеральный округ", "code": "УФО"},
                {"country_code": "RU", "name": "Сибирский федеральный округ", "code": "СФО"},
                {"country_code": "RU", "name": "Дальневосточный федеральный округ", "code": "ДФО"},
            ]
            
            federal_districts = {}
            for fd_data in federal_districts_data:
                result = await session.execute(
                    text("INSERT INTO federal_districts (country_id, name, code, is_active) VALUES (:country_id, :name, :code, :is_active) RETURNING id"),
                    {"country_id": countries[fd_data["country_code"]], "name": fd_data["name"], "code": fd_data["code"], "is_active": True}
                )
                fd_id = result.scalar()
                federal_districts[fd_data["code"]] = fd_id
            
            # 3. Создаем регионы
            regions_data = [
                # Центральный федеральный округ
                {"country_code": "RU", "fd_code": "ЦФО", "name": "Брянская область", "code": "BRY"},
                {"country_code": "RU", "fd_code": "ЦФО", "name": "Московская область", "code": "MOS"},
                {"country_code": "RU", "fd_code": "ЦФО", "name": "Воронежская область", "code": "VOR"},
                
                # Северо-Западный федеральный округ
                {"country_code": "RU", "fd_code": "СЗФО", "name": "Ленинградская область", "code": "LEN"},
                {"country_code": "RU", "fd_code": "СЗФО", "name": "Архангельская область", "code": "ARK"},
                
                # Приволжский федеральный округ
                {"country_code": "RU", "fd_code": "ПФО", "name": "Нижегородская область", "code": "NIZ"},
                {"country_code": "RU", "fd_code": "ПФО", "name": "Самарская область", "code": "SAM"},
                
                # Беларусь (без федеральных округов)
                {"country_code": "BY", "fd_code": None, "name": "Витебская область", "code": "VIT"},
                {"country_code": "BY", "fd_code": None, "name": "Минская область", "code": "MIN"},
                
                # Казахстан (без федеральных округов)
                {"country_code": "KZ", "fd_code": None, "name": "Алматинская область", "code": "ALM"},
                {"country_code": "KZ", "fd_code": None, "name": "Акмолинская область", "code": "AKM"},
                
                # Украина (без федеральных округов)
                {"country_code": "UA", "fd_code": None, "name": "Луганская область", "code": "LUG"},
                {"country_code": "UA", "fd_code": None, "name": "Винницкая область", "code": "VIN"},
            ]
            
            regions = {}
            for region_data in regions_data:
                result = await session.execute(
                    text("INSERT INTO regions (country_id, federal_district_id, name, code, is_active) VALUES (:country_id, :federal_district_id, :name, :code, :is_active) RETURNING id"),
                    {
                        "country_id": countries[region_data["country_code"]], 
                        "federal_district_id": federal_districts[region_data["fd_code"]] if region_data["fd_code"] else None,
                        "name": region_data["name"], 
                        "code": region_data["code"], 
                        "is_active": True
                    }
                )
                region_id = result.scalar()
                regions[region_data["code"]] = region_id
            
            # 4. Создаем города
            cities_data = [
                # Брянская область
                {"region_code": "BRY", "fd_code": "ЦФО", "name": "Брянск", "population": 400000, "is_regional_center": True},
                {"region_code": "BRY", "fd_code": "ЦФО", "name": "Клинцы", "population": 60000, "is_regional_center": False},
                {"region_code": "BRY", "fd_code": "ЦФО", "name": "Новозыбков", "population": 40000, "is_regional_center": False},
                
                # Московская область
                {"region_code": "MOS", "fd_code": "ЦФО", "name": "Москва", "population": 12000000, "is_million_city": True, "is_regional_center": True},
                {"region_code": "MOS", "fd_code": "ЦФО", "name": "Подольск", "population": 200000, "is_regional_center": False},
                
                # Воронежская область
                {"region_code": "VOR", "fd_code": "ЦФО", "name": "Воронеж", "population": 1000000, "is_million_city": True, "is_regional_center": True},
                {"region_code": "VOR", "fd_code": "ЦФО", "name": "Борисоглебск", "population": 60000, "is_regional_center": False},
                
                # Ленинградская область
                {"region_code": "LEN", "fd_code": "СЗФО", "name": "Санкт-Петербург", "population": 5000000, "is_million_city": True, "is_regional_center": True},
                {"region_code": "LEN", "fd_code": "СЗФО", "name": "Выборг", "population": 80000, "is_regional_center": False},
                
                # Нижегородская область
                {"region_code": "NIZ", "fd_code": "ПФО", "name": "Нижний Новгород", "population": 1200000, "is_million_city": True, "is_regional_center": True},
                {"region_code": "NIZ", "fd_code": "ПФО", "name": "Дзержинск", "population": 240000, "is_regional_center": False},
                
                # Самарская область
                {"region_code": "SAM", "fd_code": "ПФО", "name": "Самара", "population": 1100000, "is_million_city": True, "is_regional_center": True},
                {"region_code": "SAM", "fd_code": "ПФО", "name": "Тольятти", "population": 700000, "is_regional_center": False},
                
                # Витебская область (Беларусь)
                {"region_code": "VIT", "fd_code": None, "name": "Витебск", "population": 360000, "is_regional_center": True},
                {"region_code": "VIT", "fd_code": None, "name": "Орша", "population": 110000, "is_regional_center": False},
                
                # Минская область (Беларусь)
                {"region_code": "MIN", "fd_code": None, "name": "Минск", "population": 2000000, "is_million_city": True, "is_regional_center": True},
                {"region_code": "MIN", "fd_code": None, "name": "Борисов", "population": 140000, "is_regional_center": False},
                
                # Алматинская область (Казахстан)
                {"region_code": "ALM", "fd_code": None, "name": "Алматы", "population": 2000000, "is_million_city": True, "is_regional_center": True},
                {"region_code": "ALM", "fd_code": None, "name": "Талдыкорган", "population": 120000, "is_regional_center": False},
                
                # Акмолинская область (Казахстан)
                {"region_code": "AKM", "fd_code": None, "name": "Нур-Султан", "population": 1000000, "is_million_city": True, "is_regional_center": True},
                {"region_code": "AKM", "fd_code": None, "name": "Кокшетау", "population": 150000, "is_regional_center": False},
                
                # Луганская область (Украина)
                {"region_code": "LUG", "fd_code": None, "name": "Запорожье", "population": 750000, "is_regional_center": True},
                {"region_code": "LUG", "fd_code": None, "name": "Луганск", "population": 400000, "is_regional_center": False},
                
                # Винницкая область (Украина)
                {"region_code": "VIN", "fd_code": None, "name": "Львов", "population": 720000, "is_regional_center": True},
                {"region_code": "VIN", "fd_code": None, "name": "Винница", "population": 370000, "is_regional_center": False},
            ]
            
            for city_data in cities_data:
                country_id = countries["RU"] if city_data["region_code"] in ["BRY", "MOS", "VOR", "LEN", "NIZ", "SAM"] else \
                             countries["BY"] if city_data["region_code"] in ["VIT", "MIN"] else \
                             countries["KZ"] if city_data["region_code"] in ["ALM", "AKM"] else \
                             countries["UA"]
                
                await session.execute(
                    text("INSERT INTO cities (country_id, region_id, federal_district_id, name, population, is_million_city, is_regional_center, is_active) VALUES (:country_id, :region_id, :federal_district_id, :name, :population, :is_million_city, :is_regional_center, :is_active)"),
                    {
                        "country_id": country_id,
                        "region_id": regions[city_data["region_code"]],
                        "federal_district_id": federal_districts[city_data["fd_code"]] if city_data["fd_code"] else None,
                        "name": city_data["name"],
                        "population": city_data["population"],
                        "is_million_city": city_data.get("is_million_city", False),
                        "is_regional_center": city_data.get("is_regional_center", False),
                        "is_active": True
                    }
                )
            
            await session.commit()
            print("✅ Тестовые данные успешно добавлены!")
            
            # Выводим статистику
            countries_count = await session.execute(text("SELECT COUNT(*) FROM countries"))
            fd_count = await session.execute(text("SELECT COUNT(*) FROM federal_districts"))
            regions_count = await session.execute(text("SELECT COUNT(*) FROM regions"))
            cities_count = await session.execute(text("SELECT COUNT(*) FROM cities"))
            
            print(f"📊 Статистика:")
            print(f"   Страны: {countries_count.scalar()}")
            print(f"   Федеральные округа: {fd_count.scalar()}")
            print(f"   Регионы: {regions_count.scalar()}")
            print(f"   Города: {cities_count.scalar()}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при заполнении данных: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(fill_test_data())
