#!/usr/bin/env python3
"""
Скрипт для обновления компаний с новыми FK полями локаций
"""
import asyncio
import sys
import os

# Добавляем путь к приложению
sys.path.append('/app')

from sqlalchemy import text
from app.db.base import AsyncSessionLocal


async def update_companies_locations():
    """Обновляет компании с новыми FK полями локаций"""
    async with AsyncSessionLocal() as session:
        try:
            print("🔄 Обновление компаний с новыми FK полями локаций...")
            
            # Обновляем компании с новыми FK полями
            update_query = text("""
                UPDATE companies 
                SET 
                    country_id = (
                        SELECT id FROM countries 
                        WHERE countries.name = companies.country 
                        AND countries.is_active = true
                        LIMIT 1
                    ),
                    federal_district_id = (
                        SELECT id FROM federal_districts 
                        WHERE federal_districts.name = companies.federal_district 
                        AND federal_districts.is_active = true
                        LIMIT 1
                    ),
                    region_id = (
                        SELECT id FROM regions 
                        WHERE regions.name = companies.region 
                        AND regions.is_active = true
                        LIMIT 1
                    ),
                    city_id = (
                        SELECT id FROM cities 
                        WHERE cities.name = companies.city 
                        AND cities.is_active = true
                        LIMIT 1
                    )
                WHERE is_active = true
            """)
            
            result = await session.execute(update_query)
            await session.commit()
            
            print(f"✅ Обновлено {result.rowcount} компаний")
            
            # Проверяем результат
            check_query = text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(country_id) as with_country,
                    COUNT(federal_district_id) as with_federal_district,
                    COUNT(region_id) as with_region,
                    COUNT(city_id) as with_city
                FROM companies 
                WHERE is_active = true
            """)
            
            result = await session.execute(check_query)
            stats = result.fetchone()
            
            print(f"📊 Статистика обновления:")
            print(f"   Всего компаний: {stats.total}")
            print(f"   С страной: {stats.with_country}")
            print(f"   С федеральным округом: {stats.with_federal_district}")
            print(f"   С регионом: {stats.with_region}")
            print(f"   С городом: {stats.with_city}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(update_companies_locations())
