"""
Скрипт для добавления индексов для оптимизации запросов фильтрации городов
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.db.base import AsyncSessionLocal


async def add_indexes():
    """Добавляет индексы для оптимизации запросов"""
    print("🔧 Добавление индексов для оптимизации запросов...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Индексы для cities
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cities_is_active 
                ON cities(is_active);
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cities_region_id 
                ON cities(region_id);
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cities_federal_district_id 
                ON cities(federal_district_id);
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cities_country_id 
                ON cities(country_id);
            """))
            
            # Индексы для companies
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_companies_is_active 
                ON companies(is_active);
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_companies_city_id 
                ON companies(city_id);
            """))
            
            # Индексы для products
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_type 
                ON products(type);
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_is_deleted 
                ON products(is_deleted);
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_is_hidden 
                ON products(is_hidden);
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_company_id 
                ON products(company_id);
            """))
            
            # Композитный индекс для быстрого поиска активных продуктов
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_active_lookup 
                ON products(type, is_deleted, is_hidden);
            """))
            
            await session.commit()
            print("✅ Индексы успешно добавлены")
            
        except Exception as e:
            print(f"❌ Ошибка при добавлении индексов: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(add_indexes())

