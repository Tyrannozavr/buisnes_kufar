#!/usr/bin/env python3
"""
Скрипт для заполнения единиц измерения с кодами ОКЕИ
Согласно техническому заданию
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.api.purchases.models import UnitOfMeasurement


async def fill_units_of_measurement():
    """Заполнение единиц измерения с кодами ОКЕИ"""
    
    # Данные из ТЗ
    units_data = [
        # Штучные единицы
        {"name": "Штука", "symbol": "шт", "code": "796"},
        {"name": "Бобина", "symbol": "боб", "code": "616"},
        {"name": "Лист", "symbol": "л.", "code": "625"},
        {"name": "Набор", "symbol": "набор", "code": "704"},
        {"name": "Пара", "symbol": "пар", "code": "715"},
        {"name": "Рулон", "symbol": "рул", "code": "736"},
        
        # Единицы длины
        {"name": "Миллиметр", "symbol": "мм", "code": "003"},
        {"name": "Сантиметр", "symbol": "см", "code": "004"},
        {"name": "Метр", "symbol": "м", "code": "006"},
        {"name": "Километр", "symbol": "км", "code": "008"},
        {"name": "Погонный метр", "symbol": "пог. м", "code": "018"},
        
        # Единицы площади
        {"name": "Квадратный миллиметр", "symbol": "мм2", "code": "050"},
        {"name": "Квадратный сантиметр", "symbol": "см2", "code": "051"},
        {"name": "Квадратный метр", "symbol": "м2", "code": "055"},
        {"name": "Квадратный километр", "symbol": "км2", "code": "061"},
        {"name": "Гектар", "symbol": "га", "code": "059"},
        
        # Единицы объема
        {"name": "Миллилитр", "symbol": "мл", "code": "111"},
        {"name": "Литр", "symbol": "л", "code": "112"},
        {"name": "Кубический миллиметр", "symbol": "мм3", "code": "110"},
        {"name": "Кубический сантиметр", "symbol": "см3", "code": "111"},
        {"name": "Кубический метр", "symbol": "м3", "code": "113"},
        
        # Единицы массы
        {"name": "Миллиграмм", "symbol": "мг", "code": "161"},
        {"name": "Грамм", "symbol": "г", "code": "163"},
        {"name": "Килограмм", "symbol": "кг", "code": "166"},
        {"name": "Тонна", "symbol": "т", "code": "168"},
    ]
    
    # Создаем подключение к базе данных
    engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost:5432/postgres')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Проверяем, есть ли уже данные
            from sqlalchemy import text
            result = await session.execute(text("SELECT COUNT(*) FROM units_of_measurement"))
            count = result.scalar()
            
            if count > 0:
                print(f"Единицы измерения уже заполнены ({count} записей)")
                return
            
            # Добавляем единицы измерения
            for unit_data in units_data:
                unit = UnitOfMeasurement(
                    name=unit_data["name"],
                    symbol=unit_data["symbol"],
                    code=unit_data["code"]
                )
                session.add(unit)
            
            await session.commit()
            print(f"Успешно добавлено {len(units_data)} единиц измерения")
            
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при заполнении единиц измерения: {e}")
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(fill_units_of_measurement())
