#!/usr/bin/env python3
"""
Скрипт для создания таблиц и наполнения базы данных городами
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import AsyncSessionLocal, create_db_and_tables
from app.api.common.models import Country, FederalDistrict, Region, City


async def setup_database():
    """Создаем таблицы и наполняем данными"""
    
    print("🔧 Создаем таблицы базы данных...")
    await create_db_and_tables()
    print("✅ Таблицы созданы!")
    
    print("📊 Наполняем базу тестовыми данными...")
    await create_sample_data()
    print("✅ Данные добавлены!")


async def create_sample_data():
    """Создаем тестовые данные для демонстрации фильтра"""
    
    async with AsyncSessionLocal() as session:
        # Создаем страну Россия
        russia = Country(
            code="RU",
            name="Россия",
            is_active=True
        )
        session.add(russia)
        await session.flush()  # Получаем ID
        
        # Создаем федеральные округа
        federal_districts = [
            {"name": "Центральный федеральный округ", "code": "CFO"},
            {"name": "Северо-Западный федеральный округ", "code": "NWFO"},
            {"name": "Южный федеральный округ", "code": "SFO"},
            {"name": "Дальневосточный федеральный округ", "code": "DFO"},
            {"name": "Сибирский федеральный округ", "code": "SIBFO"},
            {"name": "Уральский федеральный округ", "code": "UFO"},
            {"name": "Приволжский федеральный округ", "code": "PFO"},
            {"name": "Северо-Кавказский федеральный округ", "code": "NCFO"}
        ]
        
        fd_objects = []
        for fd_data in federal_districts:
            fd = FederalDistrict(
                country_id=russia.id,
                name=fd_data["name"],
                code=fd_data["code"],
                is_active=True
            )
            session.add(fd)
            fd_objects.append(fd)
        
        await session.flush()
        
        # Создаем регионы для каждого федерального округа
        regions_data = {
            "CFO": [
                {"name": "Москва", "code": "MOS"},
                {"name": "Московская область", "code": "MOS_OBL"},
                {"name": "Белгородская область", "code": "BEL"},
                {"name": "Брянская область", "code": "BRY"},
                {"name": "Владимирская область", "code": "VLA"},
                {"name": "Воронежская область", "code": "VOR"},
                {"name": "Ивановская область", "code": "IVA"},
                {"name": "Калужская область", "code": "KAL"},
                {"name": "Костромская область", "code": "KOS"},
                {"name": "Курская область", "code": "KUR"},
                {"name": "Липецкая область", "code": "LIP"},
                {"name": "Орловская область", "code": "ORL"},
                {"name": "Рязанская область", "code": "RYA"},
                {"name": "Смоленская область", "code": "SMO"},
                {"name": "Тамбовская область", "code": "TAM"},
                {"name": "Тверская область", "code": "TVE"},
                {"name": "Тульская область", "code": "TUL"},
                {"name": "Ярославская область", "code": "YAR"}
            ],
            "NWFO": [
                {"name": "Санкт-Петербург", "code": "SPB"},
                {"name": "Ленинградская область", "code": "LEN"},
                {"name": "Архангельская область", "code": "ARK"},
                {"name": "Вологодская область", "code": "VOL"},
                {"name": "Калининградская область", "code": "KAL"},
                {"name": "Карелия", "code": "KAR"},
                {"name": "Коми", "code": "KOM"},
                {"name": "Мурманская область", "code": "MUR"},
                {"name": "Ненецкий автономный округ", "code": "NEN"},
                {"name": "Новгородская область", "code": "NOV"},
                {"name": "Псковская область", "code": "PSK"}
            ],
            "SFO": [
                {"name": "Адыгея", "code": "ADY"},
                {"name": "Астраханская область", "code": "AST"},
                {"name": "Волгоградская область", "code": "VOL"},
                {"name": "Калмыкия", "code": "KAL"},
                {"name": "Краснодарский край", "code": "KRA"},
                {"name": "Ростовская область", "code": "ROS"},
                {"name": "Крым", "code": "KRY"},
                {"name": "Севастополь", "code": "SEV"}
            ]
        }
        
        region_objects = []
        for fd_code, regions in regions_data.items():
            fd_obj = next(fd for fd in fd_objects if fd.code == fd_code)
            for region_data in regions:
                region = Region(
                    country_id=russia.id,
                    federal_district_id=fd_obj.id,
                    name=region_data["name"],
                    code=region_data["code"],
                    is_active=True
                )
                session.add(region)
                region_objects.append(region)
        
        await session.flush()
        
        # Создаем города для каждого региона
        cities_data = {
            "MOS": [
                {"name": "Москва", "population": 12615000, "is_million_city": True, "is_regional_center": True}
            ],
            "MOS_OBL": [
                {"name": "Подольск", "population": 300000, "is_million_city": False, "is_regional_center": False},
                {"name": "Химки", "population": 250000, "is_million_city": False, "is_regional_center": False},
                {"name": "Королёв", "population": 220000, "is_million_city": False, "is_regional_center": False},
                {"name": "Мытищи", "population": 200000, "is_million_city": False, "is_regional_center": False},
                {"name": "Люберцы", "population": 200000, "is_million_city": False, "is_regional_center": False},
                {"name": "Электросталь", "population": 150000, "is_million_city": False, "is_regional_center": False},
                {"name": "Железнодорожный", "population": 140000, "is_million_city": False, "is_regional_center": False},
                {"name": "Серпухов", "population": 130000, "is_million_city": False, "is_regional_center": False},
                {"name": "Одинцово", "population": 120000, "is_million_city": False, "is_regional_center": False},
                {"name": "Орехово-Зуево", "population": 120000, "is_million_city": False, "is_regional_center": False}
            ],
            "SPB": [
                {"name": "Санкт-Петербург", "population": 5400000, "is_million_city": True, "is_regional_center": True}
            ],
            "LEN": [
                {"name": "Гатчина", "population": 95000, "is_million_city": False, "is_regional_center": False},
                {"name": "Выборг", "population": 80000, "is_million_city": False, "is_regional_center": False},
                {"name": "Сосновый Бор", "population": 65000, "is_million_city": False, "is_regional_center": False},
                {"name": "Тихвин", "population": 60000, "is_million_city": False, "is_regional_center": False},
                {"name": "Кириши", "population": 50000, "is_million_city": False, "is_regional_center": False}
            ],
            "KRA": [
                {"name": "Краснодар", "population": 950000, "is_million_city": False, "is_regional_center": True},
                {"name": "Сочи", "population": 450000, "is_million_city": False, "is_regional_center": False},
                {"name": "Армавир", "population": 190000, "is_million_city": False, "is_regional_center": False},
                {"name": "Новороссийск", "population": 280000, "is_million_city": False, "is_regional_center": False},
                {"name": "Анапа", "population": 82000, "is_million_city": False, "is_regional_center": False},
                {"name": "Геленджик", "population": 80000, "is_million_city": False, "is_regional_center": False},
                {"name": "Ейск", "population": 85000, "is_million_city": False, "is_regional_center": False},
                {"name": "Кропоткин", "population": 80000, "is_million_city": False, "is_regional_center": False},
                {"name": "Славянск-на-Кубани", "population": 65000, "is_million_city": False, "is_regional_center": False},
                {"name": "Туапсе", "population": 60000, "is_million_city": False, "is_regional_center": False}
            ],
            "ROS": [
                {"name": "Ростов-на-Дону", "population": 1100000, "is_million_city": True, "is_regional_center": True},
                {"name": "Таганрог", "population": 250000, "is_million_city": False, "is_regional_center": False},
                {"name": "Шахты", "population": 230000, "is_million_city": False, "is_regional_center": False},
                {"name": "Волгодонск", "population": 170000, "is_million_city": False, "is_regional_center": False},
                {"name": "Новочеркасск", "population": 170000, "is_million_city": False, "is_regional_center": False},
                {"name": "Батайск", "population": 130000, "is_million_city": False, "is_regional_center": False},
                {"name": "Новошахтинск", "population": 110000, "is_million_city": False, "is_regional_center": False},
                {"name": "Каменск-Шахтинский", "population": 90000, "is_million_city": False, "is_regional_center": False},
                {"name": "Азов", "population": 82000, "is_million_city": False, "is_regional_center": False},
                {"name": "Гуково", "population": 65000, "is_million_city": False, "is_regional_center": False}
            ]
        }
        
        for region_code, cities in cities_data.items():
            region_obj = next(r for r in region_objects if r.code == region_code)
            fd_obj = next(fd for fd in fd_objects if fd.id == region_obj.federal_district_id)
            
            for city_data in cities:
                city = City(
                    country_id=russia.id,
                    region_id=region_obj.id,
                    federal_district_id=fd_obj.id,
                    name=city_data["name"],
                    population=city_data["population"],
                    is_million_city=city_data["is_million_city"],
                    is_regional_center=city_data["is_regional_center"],
                    is_active=True
                )
                session.add(city)
        
        await session.commit()
        print("✅ Тестовые данные успешно созданы!")
        print(f"📊 Создано:")
        print(f"   - 1 страна (Россия)")
        print(f"   - 8 федеральных округов")
        print(f"   - 30+ регионов")
        print(f"   - 50+ городов")


if __name__ == "__main__":
    asyncio.run(setup_database())
