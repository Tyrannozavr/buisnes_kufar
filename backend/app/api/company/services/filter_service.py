from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.api.company.schemas.filters import FilterItem, CompanyFiltersResponse
from app.api.products.services.cache_service import product_location_cache
from app.api.company.models.company import Company


class CompanyFilterService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _count_companies_by_country(self, country: str) -> int:
        """Подсчитывает количество компаний по стране"""
        query = select(func.count(Company.id)).where(
            and_(
                Company.country == country,
                Company.is_active == True
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def _count_companies_by_federal_district(self, federal_district: str) -> int:
        """Подсчитывает количество компаний по федеральному округу"""
        query = select(func.count(Company.id)).where(
            and_(
                Company.federal_district == federal_district,
                Company.is_active == True
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def _count_companies_by_region(self, region: str) -> int:
        """Подсчитывает количество компаний по региону"""
        query = select(func.count(Company.id)).where(
            and_(
                Company.region == region,
                Company.is_active == True
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def _count_companies_by_city(self, city: str) -> int:
        """Подсчитывает количество компаний по городу"""
        query = select(func.count(Company.id)).where(
            and_(
                Company.city == city,
                Company.is_active == True
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_cities_company_count(self) -> List[dict]:
        """Получает количество компаний для всех городов"""
        query = select(
            Company.city.label('city_name'),
            Company.region.label('region_name'),
            func.count(Company.id).label('company_count')
        ).where(
            and_(
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
                'company_count': row.company_count
            })
        
        return cities_data

    async def get_company_filters(self) -> CompanyFiltersResponse:
        """Получает фильтры для компаний с кэшированием и подсчетом компаний"""
        # Получаем кэшированные данные
        locations = await product_location_cache.get_company_locations(self.session)

        # Создаем списки с подсчетом компаний
        countries = []
        for country in sorted(locations['countries']):
            count = await self._count_companies_by_country(country)
            countries.append(FilterItem(label=country, value=country, count=count))

        federal_districts = []
        for district in sorted(locations['federal_districts']):
            count = await self._count_companies_by_federal_district(district)
            federal_districts.append(FilterItem(label=district, value=district, count=count))

        regions = []
        for region in sorted(locations['regions']):
            count = await self._count_companies_by_region(region)
            regions.append(FilterItem(label=region, value=region, count=count))

        cities = []
        for city in sorted(locations['cities']):
            count = await self._count_companies_by_city(city)
            cities.append(FilterItem(label=city, value=city, count=count))

        # Создаем ответ
        response = CompanyFiltersResponse(
            countries=countries,
            federal_districts=federal_districts,
            regions=regions,
            cities=cities
        )

        return response
