import asyncio
from datetime import datetime, timedelta
from typing import Dict, Set, Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.company.models.company import Company
from app.api.products.models.product import Product, ProductType


class ProductLocationCache:
    """Кэш для хранения связей продуктов с локациями"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_duration = timedelta(minutes=20)
        self._lock = asyncio.Lock()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Проверяет, действителен ли кэш"""
        if cache_key not in self._cache_timestamps:
            return False
        return datetime.now() - self._cache_timestamps[cache_key] < self._cache_duration

    def _get_cache(self, cache_key: str) -> Any:
        """Получает данные из кэша"""
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key)
        return None

    def _set_cache(self, cache_key: str, data: Any) -> None:
        """Сохраняет данные в кэш"""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now()

    async def get_product_locations(self, session: AsyncSession) -> Dict[str, Set[str]]:
        """Получает кэшированные связи продуктов с локациями"""
        cache_key = "product_locations"
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return cached_data

        async with self._lock:
            # Проверяем еще раз после получения блокировки
            cached_data = self._get_cache(cache_key)
            if cached_data:
                return cached_data

            # Получаем все товары с их компаниями и локациями из старых полей
            query = text("""
                SELECT DISTINCT 
                    c.country as country_name,
                    c.federal_district as federal_district_name,
                    c.region as region_name,
                    c.city as city_name
                FROM products p
                JOIN companies c ON p.company_id = c.id
                WHERE p.type = 'GOOD' 
                    AND p.is_deleted = false 
                    AND p.is_hidden = false
                    AND c.is_active = true
                    AND c.country IS NOT NULL
                    AND c.country != ''
            """)

            result = await session.execute(query)
            locations_data = result.fetchall()

            # Создаем связи продукт -> локации
            product_locations = {
                'countries': set(),
                'federal_districts': set(),
                'regions': set(),
                'cities': set()
            }

            for row in locations_data:
                if row.country_name:
                    product_locations['countries'].add(row.country_name)
                if row.federal_district_name:
                    product_locations['federal_districts'].add(row.federal_district_name)
                if row.region_name:
                    product_locations['regions'].add(row.region_name)
                if row.city_name:
                    product_locations['cities'].add(row.city_name)

            self._set_cache(cache_key, product_locations)
            return product_locations

    async def get_service_locations(self, session: AsyncSession) -> Dict[str, Set[str]]:
        """Получает кэшированные связи услуг с локациями"""
        cache_key = "service_locations"
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return cached_data

        async with self._lock:
            # Проверяем еще раз после получения блокировки
            cached_data = self._get_cache(cache_key)
            if cached_data:
                return cached_data

            # Получаем все услуги с их компаниями и локациями из старых полей
            query = text("""
                SELECT DISTINCT 
                    c.country as country_name,
                    c.federal_district as federal_district_name,
                    c.region as region_name,
                    c.city as city_name
                FROM products p
                JOIN companies c ON p.company_id = c.id
                WHERE p.type = 'SERVICE' 
                    AND p.is_deleted = false 
                    AND p.is_hidden = false
                    AND c.is_active = true
                    AND c.country IS NOT NULL
                    AND c.country != ''
            """)

            result = await session.execute(query)
            locations_data = result.fetchall()

            # Создаем связи услуга -> локации
            service_locations = {
                'countries': set(),
                'federal_districts': set(),
                'regions': set(),
                'cities': set()
            }

            for row in locations_data:
                if row.country_name:
                    service_locations['countries'].add(row.country_name)
                if row.federal_district_name:
                    service_locations['federal_districts'].add(row.federal_district_name)
                if row.region_name:
                    service_locations['regions'].add(row.region_name)
                if row.city_name:
                    service_locations['cities'].add(row.city_name)

            self._set_cache(cache_key, service_locations)
            return service_locations

    async def get_company_locations(self, session: AsyncSession) -> Dict[str, Set[str]]:
        """Получает кэшированные локации компаний"""
        cache_key = "company_locations"
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return cached_data

        async with self._lock:
            # Проверяем еще раз после получения блокировки
            cached_data = self._get_cache(cache_key)
            if cached_data:
                return cached_data

            # Получаем все активные компании с локациями из новых таблиц
            query = text("""
                SELECT DISTINCT 
                    country.name as country_name,
                    fd.name as federal_district_name,
                    r.name as region_name,
                    city.name as city_name
                FROM companies c
                LEFT JOIN countries country ON c.country_id = country.id
                LEFT JOIN federal_districts fd ON c.federal_district_id = fd.id
                LEFT JOIN regions r ON c.region_id = r.id
                LEFT JOIN cities city ON c.city_id = city.id
                WHERE c.is_active = true
                    AND (country.is_active = true OR country.is_active IS NULL)
                    AND (fd.is_active = true OR fd.is_active IS NULL)
                    AND (r.is_active = true OR r.is_active IS NULL)
                    AND (city.is_active = true OR city.is_active IS NULL)
            """)

            result = await session.execute(query)
            locations_data = result.fetchall()

            # Создаем связи компания -> локации
            company_locations = {
                'countries': set(),
                'federal_districts': set(),
                'regions': set(),
                'cities': set()
            }

            for row in locations_data:
                if row.country_name:
                    company_locations['countries'].add(row.country_name)
                if row.federal_district_name:
                    company_locations['federal_districts'].add(row.federal_district_name)
                if row.region_name:
                    company_locations['regions'].add(row.region_name)
                if row.city_name:
                    company_locations['cities'].add(row.city_name)

            self._set_cache(cache_key, company_locations)
            return company_locations

    async def clear_cache(self) -> None:
        """Очищает весь кэш"""
        async with self._lock:
            self._cache.clear()
            self._cache_timestamps.clear()

    async def refresh_cache(self, session: AsyncSession) -> None:
        """Обновляет весь кэш"""
        async with self._lock:
            await self.clear_cache()
            await self.get_product_locations(session)
            await self.get_service_locations(session)
            await self.get_company_locations(session)


# Глобальный экземпляр кэша
product_location_cache = ProductLocationCache()
