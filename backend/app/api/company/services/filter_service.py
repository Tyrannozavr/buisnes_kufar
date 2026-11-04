from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.api.company.schemas.filters import FilterItem, CompanyFiltersResponse
from app.api.products.services.cache_service import product_location_cache
from app.api.company.models.company import Company


class CompanyFilterService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _counts_by_column(self, column) -> dict[str, int]:
        """Один GROUP BY вместо N отдельных COUNT."""
        query = (
            select(column, func.count(Company.id))
            .where(
                and_(
                    Company.is_active == True,
                    column.isnot(None),
                    column != "",
                )
            )
            .group_by(column)
        )
        result = await self.session.execute(query)
        return {str(name): int(count) for name, count in result.all() if name}

    def _items(self, names: set, counts: dict[str, int]) -> List[FilterItem]:
        return [
            FilterItem(label=name, value=name, count=counts.get(name, 0))
            for name in sorted(names)
        ]

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
        return [
            {
                'city_name': row.city_name,
                'region_name': row.region_name,
                'company_count': row.company_count,
            }
            for row in result
        ]

    async def get_company_filters(self) -> CompanyFiltersResponse:
        """Получает фильтры для компаний с кэшированием и подсчетом компаний"""
        locations = await product_location_cache.get_company_locations(self.session)
        country_counts = await self._counts_by_column(Company.country)
        district_counts = await self._counts_by_column(Company.federal_district)
        region_counts = await self._counts_by_column(Company.region)
        city_counts = await self._counts_by_column(Company.city)

        return CompanyFiltersResponse(
            countries=self._items(locations['countries'], country_counts),
            federal_districts=self._items(locations['federal_districts'], district_counts),
            regions=self._items(locations['regions'], region_counts),
            cities=self._items(locations['cities'], city_counts),
        )
