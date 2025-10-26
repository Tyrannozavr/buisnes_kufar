"""
Скрипт для заполнения таблицы единиц измерения данными из ТЗ
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from app.core.config import settings

# Импортируем только нужные модели
from app.api.purchases.models import UnitOfMeasurement

# Данные из ТЗ (страницы 15-107)
UNITS_DATA = [
    # Штучные единицы
    {"name": "Штука", "symbol": "шт", "code": "796"},
    {"name": "Бобина", "symbol": "боб", "code": "616"},
    {"name": "Лист", "symbol": "л.", "code": "625"},
    {"name": "Набор", "symbol": "набор", "code": "704"},
    {"name": "Пара", "symbol": "пар", "code": "715"},
    {"name": "Рулон", "symbol": "рул", "code": "736"},
    
    # Линейные единицы
    {"name": "Миллиметр", "symbol": "мм", "code": "003"},
    {"name": "Сантиметр", "symbol": "см", "code": "004"},
    {"name": "Метр", "symbol": "м", "code": "006"},
    {"name": "Километр", "symbol": "км", "code": "008"},
    {"name": "Погонный метр", "symbol": "пог. м", "code": "018"},
    
    # Единицы площади
    {"name": "Квадратный миллиметр", "symbol": "мм²", "code": "050"},
    {"name": "Квадратный сантиметр", "symbol": "см²", "code": "051"},
    {"name": "Квадратный метр", "symbol": "м²", "code": "055"},
    {"name": "Квадратный километр", "symbol": "км²", "code": "061"},
    {"name": "Гектар", "symbol": "га", "code": "059"},
    
    # Единицы объема
    {"name": "Миллилитр", "symbol": "мл", "code": "111"},
    {"name": "Литр", "symbol": "л", "code": "112"},
    {"name": "Кубический миллиметр", "symbol": "мм³", "code": "110"},
    {"name": "Кубический сантиметр", "symbol": "см³", "code": "111"},
    {"name": "Кубический метр", "symbol": "м³", "code": "113"},
    
    # Единицы массы
    {"name": "Миллиграмм", "symbol": "мг", "code": "161"},
    {"name": "Грамм", "symbol": "г", "code": "163"},
    {"name": "Килограмм", "symbol": "кг", "code": "166"},
    {"name": "Тонна", "symbol": "т", "code": "168"},
]


async def populate_units():
    """Заполнение таблицы единиц измерения"""
    # Создаем engine
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)
    
    # Создаем session maker
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Проверяем, есть ли уже данные
            from sqlalchemy import select, func
            result = await session.execute(select(func.count(UnitOfMeasurement.id)))
            count = result.scalar()
            
            if count > 0:
                print(f"Таблица уже содержит {count} записей. Пропускаем...")
                return
            
            # Добавляем единицы измерения
            print("Добавляем единицы измерения...")
            for unit_data in UNITS_DATA:
                unit = UnitOfMeasurement(**unit_data)
                session.add(unit)
            
            await session.commit()
            print(f"Успешно добавлено {len(UNITS_DATA)} единиц измерения")
            
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при добавлении данных: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(populate_units())

