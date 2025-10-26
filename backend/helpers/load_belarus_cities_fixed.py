#!/usr/bin/env python3
"""
Скрипт для загрузки городов Беларуси
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent))

from app.db.base import AsyncSessionLocal
from app.api.common.models.region import Region
from app.api.common.models.city import City
from sqlalchemy import text


async def add_belarus_regions():
    """Добавляем регионы Беларуси"""
    print("🗺️ Добавляем регионы Беларуси...")
    
    belarus_regions = [
        (86, 0, 3, 'Минская область', 'MINSK'),
        (87, 0, 3, 'Гомельская область', 'GOMEL'),
        (88, 0, 3, 'Могилёвская область', 'MOGILEV'),
        (89, 0, 3, 'Витебская область', 'VITEBSK'),
        (90, 0, 3, 'Гродненская область', 'GRODNO'),
        (91, 0, 3, 'Брестская область', 'BREST'),
    ]
    
    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        for region_id, federal_district_id, country_id, name, code in belarus_regions:
            region = Region(
                id=region_id,
                federal_district_id=federal_district_id if federal_district_id > 0 else None,
                country_id=country_id,
                name=name,
                code=code,
                is_active=True,
                created_at=now,
                updated_at=now
            )
            db.add(region)
        await db.commit()
    
    print(f"✅ Добавлено {len(belarus_regions)} регионов Беларуси")


async def add_belarus_cities():
    """Добавляем города Беларуси"""
    print("🏙️ Добавляем города Беларуси...")
    
    # Основные города Беларуси с населением и регионами
    belarus_cities = [
        # Минская область (86)
        (135, 0, 86, 3, 'Минск', 2000000, True, True),
        (136, 0, 86, 3, 'Борисов', 150000, False, False),
        (137, 0, 86, 3, 'Солигорск', 150000, False, False),
        (138, 0, 86, 3, 'Молодечно', 100000, False, False),
        (139, 0, 86, 3, 'Жодино', 70000, False, False),
        (140, 0, 86, 3, 'Слуцк', 60000, False, False),
        (141, 0, 86, 3, 'Вилейка', 30000, False, False),
        (142, 0, 86, 3, 'Дзержинск', 30000, False, False),
        (143, 0, 86, 3, 'Марьина Горка', 25000, False, False),
        (144, 0, 86, 3, 'Столбцы', 20000, False, False),
        (145, 0, 86, 3, 'Несвиж', 15000, False, False),
        (146, 0, 86, 3, 'Клецк', 12000, False, False),
        (147, 0, 86, 3, 'Любань', 10000, False, False),
        (148, 0, 86, 3, 'Старые Дороги', 8000, False, False),
        (149, 0, 86, 3, 'Копыль', 7000, False, False),
        (150, 0, 86, 3, 'Узда', 6000, False, False),
        (151, 0, 86, 3, 'Червень', 5000, False, False),
        (152, 0, 86, 3, 'Смолевичи', 5000, False, False),
        (153, 0, 86, 3, 'Логойск', 4000, False, False),
        (154, 0, 86, 3, 'Воложин', 4000, False, False),
        
        # Гомельская область (87)
        (155, 0, 87, 3, 'Гомель', 500000, False, True),
        (156, 0, 87, 3, 'Мозырь', 150000, False, False),
        (157, 0, 87, 3, 'Жлобин', 80000, False, False),
        (158, 0, 87, 3, 'Светлогорск', 70000, False, False),
        (159, 0, 87, 3, 'Речица', 60000, False, False),
        (160, 0, 87, 3, 'Калинковичи', 40000, False, False),
        (161, 0, 87, 3, 'Рогачёв', 35000, False, False),
        (162, 0, 87, 3, 'Добруш', 20000, False, False),
        (163, 0, 87, 3, 'Ветка', 15000, False, False),
        (164, 0, 87, 3, 'Чечерск', 10000, False, False),
        (165, 0, 87, 3, 'Буда-Кошелёво', 8000, False, False),
        (166, 0, 87, 3, 'Хойники', 7000, False, False),
        (167, 0, 87, 3, 'Наровля', 5000, False, False),
        (168, 0, 87, 3, 'Ельск', 5000, False, False),
        (169, 0, 87, 3, 'Лельчицы', 4000, False, False),
        (170, 0, 87, 3, 'Петриков', 4000, False, False),
        (171, 0, 87, 3, 'Октябрьский', 3000, False, False),
        (172, 0, 87, 3, 'Корма', 3000, False, False),
        (173, 0, 87, 3, 'Брагин', 2000, False, False),
        (174, 0, 87, 3, 'Лоев', 2000, False, False),
        
        # Могилёвская область (88)
        (175, 0, 88, 3, 'Могилёв', 400000, False, True),
        (176, 0, 88, 3, 'Бобруйск', 200000, False, False),
        (177, 0, 88, 3, 'Орша', 150000, False, False),
        (178, 0, 88, 3, 'Горки', 40000, False, False),
        (179, 0, 88, 3, 'Кричев', 30000, False, False),
        (180, 0, 88, 3, 'Осиповичи', 30000, False, False),
        (181, 0, 88, 3, 'Климовичи', 20000, False, False),
        (182, 0, 88, 3, 'Шклов', 20000, False, False),
        (183, 0, 88, 3, 'Костюковичи', 15000, False, False),
        (184, 0, 88, 3, 'Чаусы', 15000, False, False),
        (185, 0, 88, 3, 'Мстиславль', 10000, False, False),
        (186, 0, 88, 3, 'Чериков', 10000, False, False),
        (187, 0, 88, 3, 'Славгород', 8000, False, False),
        (188, 0, 88, 3, 'Краснополье', 6000, False, False),
        (189, 0, 88, 3, 'Хотимск', 5000, False, False),
        (190, 0, 88, 3, 'Круглое', 4000, False, False),
        (191, 0, 88, 3, 'Белыничи', 4000, False, False),
        (192, 0, 88, 3, 'Дрибин', 3000, False, False),
        (193, 0, 88, 3, 'Глуск', 3000, False, False),
        (194, 0, 88, 3, 'Кировск', 2000, False, False),
        
        # Витебская область (89)
        (195, 0, 89, 3, 'Витебск', 400000, False, True),
        (196, 0, 89, 3, 'Новополоцк', 100000, False, False),
        (197, 0, 89, 3, 'Полоцк', 80000, False, False),
        (198, 0, 89, 3, 'Лепель', 20000, False, False),
        (199, 0, 89, 3, 'Глубокое', 20000, False, False),
        (200, 0, 89, 3, 'Поставы', 20000, False, False),
        (201, 0, 89, 3, 'Браслав', 15000, False, False),
        (202, 0, 89, 3, 'Докшицы', 15000, False, False),
        (203, 0, 89, 3, 'Дубровно', 10000, False, False),
        (204, 0, 89, 3, 'Лиозно', 10000, False, False),
        (205, 0, 89, 3, 'Миоры', 10000, False, False),
        (206, 0, 89, 3, 'Россоны', 10000, False, False),
        (207, 0, 89, 3, 'Сенно', 10000, False, False),
        (208, 0, 89, 3, 'Толочин', 10000, False, False),
        (209, 0, 89, 3, 'Ушачи', 8000, False, False),
        (210, 0, 89, 3, 'Чашники', 8000, False, False),
        (211, 0, 89, 3, 'Шарковщина', 6000, False, False),
        (212, 0, 89, 3, 'Шумилино', 6000, False, False),
        (213, 0, 89, 3, 'Верхнедвинск', 5000, False, False),
        
        # Гродненская область (90)
        (214, 0, 90, 3, 'Гродно', 400000, False, True),
        (215, 0, 90, 3, 'Лида', 100000, False, False),
        (216, 0, 90, 3, 'Слоним', 50000, False, False),
        (217, 0, 90, 3, 'Волковыск', 50000, False, False),
        (218, 0, 90, 3, 'Сморгонь', 40000, False, False),
        (219, 0, 90, 3, 'Новогрудок', 30000, False, False),
        (220, 0, 90, 3, 'Ошмяны', 20000, False, False),
        (221, 0, 90, 3, 'Щучин', 20000, False, False),
        (222, 0, 90, 3, 'Ивье', 15000, False, False),
        (223, 0, 90, 3, 'Кореличи', 15000, False, False),
        (224, 0, 90, 3, 'Мосты', 15000, False, False),
        (225, 0, 90, 3, 'Зельва', 10000, False, False),
        (226, 0, 90, 3, 'Свислочь', 10000, False, False),
        (227, 0, 90, 3, 'Берестовица', 8000, False, False),
        (228, 0, 90, 3, 'Дятлово', 8000, False, False),
        (229, 0, 90, 3, 'Вороново', 6000, False, False),
        (230, 0, 90, 3, 'Островец', 6000, False, False),
        (231, 0, 90, 3, 'Скидель', 5000, False, False),
        (232, 0, 90, 3, 'Берёзовка', 4000, False, False),
        (233, 0, 90, 3, 'Любча', 3000, False, False),
        
        # Брестская область (91)
        (234, 0, 91, 3, 'Брест', 350000, False, True),
        (235, 0, 91, 3, 'Барановичи', 200000, False, False),
        (236, 0, 91, 3, 'Пинск', 150000, False, False),
        (237, 0, 91, 3, 'Кобрин', 50000, False, False),
        (238, 0, 91, 3, 'Берёза', 30000, False, False),
        (239, 0, 91, 3, 'Лунинец', 30000, False, False),
        (240, 0, 91, 3, 'Ивацевичи', 25000, False, False),
        (241, 0, 91, 3, 'Пружаны', 25000, False, False),
        (242, 0, 91, 3, 'Жабинка', 20000, False, False),
        (243, 0, 91, 3, 'Микашевичи', 15000, False, False),
        (244, 0, 91, 3, 'Столин', 15000, False, False),
        (245, 0, 91, 3, 'Дрогичин', 15000, False, False),
        (246, 0, 91, 3, 'Малорита', 10000, False, False),
        (247, 0, 91, 3, 'Ганцевичи', 10000, False, False),
        (248, 0, 91, 3, 'Каменец', 10000, False, False),
        (249, 0, 91, 3, 'Ляховичи', 10000, False, False),
        (250, 0, 91, 3, 'Высокое', 5000, False, False),
        (251, 0, 91, 3, 'Коссово', 3000, False, False),
        (252, 0, 91, 3, 'Телеханы', 2000, False, False),
    ]
    
    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        for city_id, federal_district_id, region_id, country_id, name, population, is_million_city, is_regional_center in belarus_cities:
            city = City(
                id=city_id,
                federal_district_id=federal_district_id if federal_district_id > 0 else None,
                region_id=region_id if region_id > 0 else None,
                country_id=country_id,
                name=name,
                population=population,
                is_million_city=is_million_city,
                is_regional_center=is_regional_center,
                is_active=True,
                created_at=now,
                updated_at=now
            )
            db.add(city)
        await db.commit()
    
    print(f"✅ Добавлено {len(belarus_cities)} городов Беларуси")


async def clear_old_belarus_data():
    """Очищаем старые данные Беларуси"""
    print("🧹 Очищаем старые данные Беларуси...")
    
    async with AsyncSessionLocal() as db:
        # Удаляем старые города Беларуси
        await db.execute(text("DELETE FROM cities WHERE country_id = 3"))
        # Удаляем старые регионы Беларуси
        await db.execute(text("DELETE FROM regions WHERE country_id = 3"))
        await db.commit()
    
    print("✅ Старые данные очищены")


async def main():
    """Основная функция"""
    print("🚀 Начинаем загрузку городов Беларуси...")
    
    try:
        await clear_old_belarus_data()
        await add_belarus_regions()
        await add_belarus_cities()
        
        print("\n🎉 Загрузка городов Беларуси завершена успешно!")
        
        # Проверяем результат
        async with AsyncSessionLocal() as db:
            from sqlalchemy import text
            result = await db.execute(text("SELECT COUNT(*) FROM regions WHERE country_id = 3"))
            regions_count = result.scalar()
            result = await db.execute(text("SELECT COUNT(*) FROM cities WHERE country_id = 3"))
            cities_count = result.scalar()
            
            print(f"\n📊 Итоговая статистика:")
            print(f"   🗺️ Регионов Беларуси: {regions_count}")
            print(f"   🏙️ Городов Беларуси: {cities_count}")
            
    except Exception as e:
        print(f"❌ Ошибка при загрузке городов Беларуси: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
