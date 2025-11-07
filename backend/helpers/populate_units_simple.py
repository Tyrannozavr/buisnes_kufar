"""
Простой скрипт для заполнения единиц измерения через raw SQL
"""
import asyncio
import asyncpg
from app.core.config import settings

# Данные из ТЗ (страницы 15-107)
UNITS_DATA = [
    # Штучные единицы
    ("Штука", "шт", "796"),
    ("Бобина", "боб", "616"),
    ("Лист", "л.", "625"),
    ("Набор", "набор", "704"),
    ("Пара", "пар", "715"),
    ("Рулон", "рул", "736"),
    
    # Линейные единицы
    ("Миллиметр", "мм", "003"),
    ("Сантиметр", "см", "004"),
    ("Метр", "м", "006"),
    ("Километр", "км", "008"),
    ("Погонный метр", "пог. м", "018"),
    
    # Единицы площади
    ("Квадратный миллиметр", "мм²", "050"),
    ("Квадратный сантиметр", "см²", "051"),
    ("Квадратный метр", "м²", "055"),
    ("Квадратный километр", "км²", "061"),
    ("Гектар", "га", "059"),
    
    # Единицы объема
    ("Миллилитр", "мл", "111"),
    ("Литр", "л", "112"),
    ("Кубический миллиметр", "мм³", "110"),
    ("Кубический сантиметр", "см³", "111"),
    ("Кубический метр", "м³", "113"),
    
    # Единицы массы
    ("Миллиграмм", "мг", "161"),
    ("Грамм", "г", "163"),
    ("Килограмм", "кг", "166"),
    ("Тонна", "т", "168"),
]


async def populate_units():
    """Заполнение таблицы единиц измерения через raw SQL"""
    # Получаем URL базы данных
    db_url = settings.SQLALCHEMY_DATABASE_URL
    if not db_url:
        # Если URL не задан, используем значения по умолчанию
        db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
    
    try:
        # Подключаемся к базе данных
        conn = await asyncpg.connect(db_url)
        
        # Проверяем, есть ли уже данные
        count = await conn.fetchval("SELECT COUNT(*) FROM units_of_measurement")
        
        if count > 0:
            print(f"Таблица уже содержит {count} записей. Пропускаем...")
            await conn.close()
            return
        
        # Добавляем единицы измерения
        print("Добавляем единицы измерения...")
        for name, symbol, code in UNITS_DATA:
            await conn.execute(
                "INSERT INTO units_of_measurement (name, symbol, code, created_at, updated_at) VALUES ($1, $2, $3, NOW(), NOW())",
                name, symbol, code
            )
        
        await conn.close()
        print(f"Успешно добавлено {len(UNITS_DATA)} единиц измерения")
        
    except Exception as e:
        print(f"Ошибка при добавлении данных: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(populate_units())
