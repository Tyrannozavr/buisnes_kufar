from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.api.products.schemas.filters import FilterItem, ProductFiltersResponse, ServiceFiltersResponse
from app.api.products.services.cache_service import product_location_cache
from app.api.products.models.product import Product, ProductType
from app.api.company.models.company import Company


class FilterService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _count_products_by_country(self, country: str, product_type: ProductType) -> int:
        """Подсчитывает количество товаров по стране"""
        query = select(func.count(Product.id)).join(Company, Product.company_id == Company.id).where(
            and_(
                Product.type == product_type,
                Product.is_deleted == False,
                Product.is_hidden == False,
                Company.country == country
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def _count_products_by_federal_district(self, federal_district: str, product_type: ProductType) -> int:
        """Подсчитывает количество товаров по федеральному округу"""
        query = select(func.count(Product.id)).join(Company, Product.company_id == Company.id).where(
            and_(
                Product.type == product_type,
                Product.is_deleted == False,
                Product.is_hidden == False,
                Company.federal_district == federal_district
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def _count_products_by_region(self, region: str, product_type: ProductType) -> int:
        """Подсчитывает количество товаров по региону"""
        query = select(func.count(Product.id)).join(Company, Product.company_id == Company.id).where(
            and_(
                Product.type == product_type,
                Product.is_deleted == False,
                Product.is_hidden == False,
                Company.region == region
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def _count_products_by_city(self, city: str, product_type: ProductType) -> int:
        """Подсчитывает количество товаров по городу"""
        query = select(func.count(Product.id)).join(Company, Product.company_id == Company.id).where(
            and_(
                Product.type == product_type,
                Product.is_deleted == False,
                Product.is_hidden == False,
                Company.city == city
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_product_filters(self) -> ProductFiltersResponse:
        """Получает фильтры для товаров с кэшированием и подсчетом товаров"""
        # Получаем кэшированные данные
        locations = await product_location_cache.get_product_locations(self.session)

        # Создаем фильтры с подсчетом товаров
        countries = []
        for country in sorted(locations['countries']):
            count = await self._count_products_by_country(country, ProductType.GOOD)
            countries.append(FilterItem(label=country, value=country, count=count))

        federal_districts = []
        for district in sorted(locations['federal_districts']):
            count = await self._count_products_by_federal_district(district, ProductType.GOOD)
            federal_districts.append(FilterItem(label=district, value=district, count=count))

        regions = []
        for region in sorted(locations['regions']):
            count = await self._count_products_by_region(region, ProductType.GOOD)
            regions.append(FilterItem(label=region, value=region, count=count))

        cities = []
        for city in sorted(locations['cities']):
            count = await self._count_products_by_city(city, ProductType.GOOD)
            cities.append(FilterItem(label=city, value=city, count=count))

        response = ProductFiltersResponse(
            countries=countries,
            federal_districts=federal_districts,
            regions=regions,
            cities=cities
        )

        return response

    async def get_service_filters(self) -> ServiceFiltersResponse:
        """Получает фильтры для услуг с кэшированием и подсчетом услуг"""
        # Получаем кэшированные данные
        locations = await product_location_cache.get_service_locations(self.session)

        # Создаем фильтры с подсчетом услуг
        countries = []
        for country in sorted(locations['countries']):
            count = await self._count_products_by_country(country, ProductType.SERVICE)
            countries.append(FilterItem(label=country, value=country, count=count))

        federal_districts = []
        for district in sorted(locations['federal_districts']):
            count = await self._count_products_by_federal_district(district, ProductType.SERVICE)
            federal_districts.append(FilterItem(label=district, value=district, count=count))

        regions = []
        for region in sorted(locations['regions']):
            count = await self._count_products_by_region(region, ProductType.SERVICE)
            regions.append(FilterItem(label=region, value=region, count=count))

        cities = []
        for city in sorted(locations['cities']):
            count = await self._count_products_by_city(city, ProductType.SERVICE)
            cities.append(FilterItem(label=city, value=city, count=count))

        response = ServiceFiltersResponse(
            countries=countries,
            federal_districts=federal_districts,
            regions=regions,
            cities=cities
        )

        return response

    async def get_cities_product_count(self, product_type: ProductType) -> List[dict]:
        """Получает количество товаров для всех городов"""
        query = select(
            Company.city.label('city_name'),
            Company.region.label('region_name'),
            func.count(Product.id).label('product_count')
        ).join(Company, Product.company_id == Company.id).where(
            and_(
                Product.type == product_type,
                Product.is_deleted == False,
                Product.is_hidden == False,
                Company.is_active == True,
                Company.city.isnot(None),
                Company.city != '',
                Company.region.isnot(None),
                Company.region != ''
            )
        ).group_by(Company.city, Company.region)
        
        result = await self.session.execute(query)
        cities_data = []
        for row in result:
            cities_data.append({
                'city_name': row.city_name,
                'region_name': row.region_name,
                'product_count': row.product_count
            })
        
        return cities_data
