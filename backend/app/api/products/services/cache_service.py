import asyncio
from datetime import datetime, timedelta
from typing import Dict, Set, Any

from sqlalchemy import select
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

            # Получаем все товары с их компаниями
            query = (
                select(Product, Company)
                .join(Company, Product.company_id == Company.id)
                .where(
                    Product.type == ProductType.GOOD,
                    Product.is_deleted == False,
                    Product.is_hidden == False
                )
            )

            result = await session.execute(query)
            products_with_companies = result.all()

            # Создаем связи продукт -> локации
            product_locations = {
                'countries': set(),
                'federal_districts': set(),
                'regions': set(),
                'cities': set()
            }

            for product, company in products_with_companies:
                if company.country:
                    product_locations['countries'].add(company.country)
                if company.federal_district:
                    product_locations['federal_districts'].add(company.federal_district)
                if company.region:
                    product_locations['regions'].add(company.region)
                if company.city:
                    product_locations['cities'].add(company.city)

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

            # Получаем все услуги с их компаниями
            query = (
                select(Product, Company)
                .join(Company, Product.company_id == Company.id)
                .where(
                    Product.type == ProductType.SERVICE,
                    Product.is_deleted == False,
                    Product.is_hidden == False
                )
            )

            result = await session.execute(query)
            services_with_companies = result.all()

            # Создаем связи услуга -> локации
            service_locations = {
                'countries': set(),
                'federal_districts': set(),
                'regions': set(),
                'cities': set()
            }

            for service, company in services_with_companies:
                if company.country:
                    service_locations['countries'].add(company.country)
                if company.federal_district:
                    service_locations['federal_districts'].add(company.federal_district)
                if company.region:
                    service_locations['regions'].add(company.region)
                if company.city:
                    service_locations['cities'].add(company.city)

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

            # Получаем все активные компании
            query = (
                select(Company)
                .where(Company.is_active == True)
            )

            result = await session.execute(query)
            companies = result.scalars().all()

            # Создаем связи компания -> локации
            company_locations = {
                'countries': set(),
                'federal_districts': set(),
                'regions': set(),
                'cities': set()
            }

            for company in companies:
                if company.country:
                    company_locations['countries'].add(company.country)
                if company.federal_district:
                    company_locations['federal_districts'].add(company.federal_district)
                if company.region:
                    company_locations['regions'].add(company.region)
                if company.city:
                    company_locations['cities'].add(company.city)

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
