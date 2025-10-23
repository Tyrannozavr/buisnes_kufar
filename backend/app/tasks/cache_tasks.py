import logging
from datetime import datetime
from typing import List, Dict, Any
import asyncio

from sqlalchemy import text, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.db.base import AsyncSessionLocal
from app.api.common.models.active_cities_cache import ActiveCitiesCache, ProductCityMapping
from app.api.company.models.company import Company
from app.api.products.models.product import Product, ProductType

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.cache_tasks.update_product_city_cache")
def update_product_city_cache(self):
    """Обновляет кэш связей продуктов с городами"""
    try:
        logger.info("🔄 Начинаем обновление кэша продуктов и городов")
        
        # Выполняем асинхронную функцию в event loop
        result = asyncio.run(_update_product_city_cache_async())
        
        logger.info(f"✅ Кэш продуктов и городов обновлен: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении кэша продуктов и городов: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


async def _update_product_city_cache_async() -> Dict[str, Any]:
    """Асинхронная функция для обновления кэша продуктов и городов"""
    
    # Получаем сессию базы данных
    async with AsyncSessionLocal() as session:
        
        # 1. Очищаем старые записи
        await session.execute(delete(ProductCityMapping))
        await session.execute(delete(ActiveCitiesCache).where(ActiveCitiesCache.cache_type == "products"))
        
        # 2. Получаем все активные продукты с их компаниями и городами
        query = text("""
            SELECT DISTINCT 
                p.id as product_id,
                c.id as company_id,
                c.city_id,
                c.city as city_name,
                c.region as region_name,
                c.federal_district as federal_district_name,
                c.country as country_name
            FROM products p
            JOIN companies c ON p.company_id = c.id
            WHERE p.type = 'GOOD' 
                AND p.is_deleted = false 
                AND p.is_hidden = false
                AND c.is_active = true
                AND c.city_id IS NOT NULL
                AND c.city IS NOT NULL
                AND c.city != ''
        """)
        
        result = await session.execute(query)
        products_data = result.fetchall()
        
        # 3. Создаем новые записи в ProductCityMapping
        mapping_records = []
        active_city_ids = set()
        
        for row in products_data:
            mapping_records.append({
                "product_id": row.product_id,
                "company_id": row.company_id,
                "city_id": row.city_id
            })
            active_city_ids.add(row.city_id)
        
        if mapping_records:
            await session.execute(insert(ProductCityMapping), mapping_records)
        
        # 4. Создаем запись в ActiveCitiesCache
        cache_record = ActiveCitiesCache(
            cache_type="products",
            active_city_ids=list(active_city_ids),
            total_cities=len(active_city_ids),
            total_companies=len(set(row.company_id for row in products_data)),
            total_products=len(products_data),
            last_updated=datetime.utcnow(),
            is_active=True
        )
        
        session.add(cache_record)
        await session.commit()
        
        return {
            "total_products": len(products_data),
            "total_companies": len(set(row.company_id for row in products_data)),
            "total_cities": len(active_city_ids),
            "mapping_records": len(mapping_records)
        }


@celery_app.task(bind=True, name="app.tasks.cache_tasks.update_company_city_cache")
def update_company_city_cache(self):
    """Обновляет кэш связей компаний с городами"""
    try:
        logger.info("🔄 Начинаем обновление кэша компаний и городов")
        
        # Выполняем асинхронную функцию в event loop
        result = asyncio.run(_update_company_city_cache_async())
        
        logger.info(f"✅ Кэш компаний и городов обновлен: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении кэша компаний и городов: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


async def _update_company_city_cache_async() -> Dict[str, Any]:
    """Асинхронная функция для обновления кэша компаний и городов"""
    
    # Получаем сессию базы данных
    async with AsyncSessionLocal() as session:
        
        # 1. Очищаем старые записи для компаний
        await session.execute(delete(ActiveCitiesCache).where(ActiveCitiesCache.cache_type == "companies"))
        
        # 2. Получаем все активные компании с городами
        query = text("""
            SELECT DISTINCT 
                c.id as company_id,
                c.city_id,
                c.city as city_name,
                c.region as region_name,
                c.federal_district as federal_district_name,
                c.country as country_name
            FROM companies c
            WHERE c.is_active = true
                AND c.city_id IS NOT NULL
                AND c.city IS NOT NULL
                AND c.city != ''
        """)
        
        result = await session.execute(query)
        companies_data = result.fetchall()
        
        # 3. Создаем запись в ActiveCitiesCache для компаний
        active_city_ids = set(row.city_id for row in companies_data)
        
        cache_record = ActiveCitiesCache(
            cache_type="companies",
            active_city_ids=list(active_city_ids),
            total_cities=len(active_city_ids),
            total_companies=len(companies_data),
            total_products=0,  # Для компаний не считаем продукты
            last_updated=datetime.utcnow(),
            is_active=True
        )
        
        session.add(cache_record)
        await session.commit()
        
        return {
            "total_companies": len(companies_data),
            "total_cities": len(active_city_ids)
        }


@celery_app.task(bind=True, name="app.tasks.cache_tasks.update_cities_product_count")
def update_cities_product_count(self):
    """Обновляет количество товаров по городам"""
    try:
        logger.info("🔄 Начинаем обновление количества товаров по городам")
        
        # Выполняем асинхронную функцию в event loop
        result = asyncio.run(_update_cities_product_count_async())
        
        logger.info(f"✅ Количество товаров по городам обновлено: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении количества товаров по городам: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


async def _update_cities_product_count_async() -> Dict[str, Any]:
    """Асинхронная функция для обновления количества товаров по городам"""
    
    # Получаем сессию базы данных
    async with AsyncSessionLocal() as session:
        
        # Получаем количество товаров по городам для товаров
        goods_query = text("""
            SELECT 
                c.city as city_name,
                c.region as region_name,
                COUNT(p.id) as product_count
            FROM companies c
            JOIN products p ON c.id = p.company_id
            WHERE p.type = 'GOOD'
                AND p.is_deleted = false 
                AND p.is_hidden = false
                AND c.is_active = true
                AND c.city IS NOT NULL
                AND c.city != ''
            GROUP BY c.city, c.region
            ORDER BY product_count DESC
        """)
        
        goods_result = await session.execute(goods_query)
        goods_data = goods_result.fetchall()
        
        # Получаем количество услуг по городам
        services_query = text("""
            SELECT 
                c.city as city_name,
                c.region as region_name,
                COUNT(p.id) as service_count
            FROM companies c
            JOIN products p ON c.id = p.company_id
            WHERE p.type = 'SERVICE'
                AND p.is_deleted = false 
                AND p.is_hidden = false
                AND c.is_active = true
                AND c.city IS NOT NULL
                AND c.city != ''
            GROUP BY c.city, c.region
            ORDER BY service_count DESC
        """)
        
        services_result = await session.execute(services_query)
        services_data = services_result.fetchall()
        
        # Получаем количество компаний по городам
        companies_query = text("""
            SELECT 
                c.city as city_name,
                c.region as region_name,
                COUNT(c.id) as company_count
            FROM companies c
            WHERE c.is_active = true
                AND c.city IS NOT NULL
                AND c.city != ''
            GROUP BY c.city, c.region
            ORDER BY company_count DESC
        """)
        
        companies_result = await session.execute(companies_query)
        companies_data = companies_result.fetchall()
        
        return {
            "goods_cities": len(goods_data),
            "services_cities": len(services_data),
            "companies_cities": len(companies_data),
            "total_goods": sum(row.product_count for row in goods_data),
            "total_services": sum(row.service_count for row in services_data),
            "total_companies": sum(row.company_count for row in companies_data)
        }


@celery_app.task(bind=True, name="app.tasks.cache_tasks.refresh_all_caches")
def refresh_all_caches(self):
    """Полное обновление всех кэшей"""
    try:
        logger.info("🔄 Начинаем полное обновление всех кэшей")
        
        # Выполняем все обновления
        results = {}
        
        # Обновляем кэш продуктов и городов
        results["product_city_cache"] = asyncio.run(_update_product_city_cache_async())
        
        # Обновляем кэш компаний и городов
        results["company_city_cache"] = asyncio.run(_update_company_city_cache_async())
        
        # Обновляем количество товаров по городам
        results["cities_product_count"] = asyncio.run(_update_cities_product_count_async())
        
        logger.info(f"✅ Все кэши обновлены: {results}")
        return results
        
    except Exception as e:
        logger.error(f"❌ Ошибка при полном обновлении кэшей: {e}")
        raise self.retry(exc=e, countdown=120, max_retries=2)


@celery_app.task(bind=True, name="app.tasks.cache_tasks.clear_all_caches")
def clear_all_caches(self):
    """Очищает все кэши"""
    try:
        logger.info("🔄 Начинаем очистку всех кэшей")
        
        # Выполняем асинхронную функцию в event loop
        result = asyncio.run(_clear_all_caches_async())
        
        logger.info("✅ Все кэши очищены")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка при очистке кэшей: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


async def _clear_all_caches_async() -> Dict[str, Any]:
    """Асинхронная функция для очистки всех кэшей"""
    
    # Получаем сессию базы данных
    async with AsyncSessionLocal() as session:
        
        # Очищаем все кэш-таблицы
        await session.execute(delete(ProductCityMapping))
        await session.execute(delete(ActiveCitiesCache))
        await session.commit()
        
        return {"status": "success", "message": "All caches cleared"}
