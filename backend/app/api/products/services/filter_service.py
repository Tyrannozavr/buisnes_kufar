from typing import List

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.company.models.company import Company
from app.api.products.models.product import Product, ProductType
from app.api.products.schemas.filters import FilterItem, ProductFiltersResponse, ServiceFiltersResponse
from app.api.products.services.cache_service import product_location_cache


class FilterService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _counts_by_column(self, product_type: ProductType, column) -> dict[str, int]:
        """Один GROUP BY вместо N отдельных COUNT."""
        query = (
            select(column, func.count(Product.id))
            .join(Company, Product.company_id == Company.id)
            .where(
                and_(
                    Product.type == product_type,
                    Product.is_deleted == False,
                    Product.is_hidden == False,
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

    async def get_product_filters(self) -> ProductFiltersResponse:
        locations = await product_location_cache.get_product_locations(self.session)
        country_counts = await self._counts_by_column(ProductType.GOOD, Company.country)
        district_counts = await self._counts_by_column(ProductType.GOOD, Company.federal_district)
        region_counts = await self._counts_by_column(ProductType.GOOD, Company.region)
        city_counts = await self._counts_by_column(ProductType.GOOD, Company.city)
        return ProductFiltersResponse(
            countries=self._items(locations["countries"], country_counts),
            federal_districts=self._items(locations["federal_districts"], district_counts),
            regions=self._items(locations["regions"], region_counts),
            cities=self._items(locations["cities"], city_counts),
        )

    async def get_service_filters(self) -> ServiceFiltersResponse:
        locations = await product_location_cache.get_service_locations(self.session)
        country_counts = await self._counts_by_column(ProductType.SERVICE, Company.country)
        district_counts = await self._counts_by_column(ProductType.SERVICE, Company.federal_district)
        region_counts = await self._counts_by_column(ProductType.SERVICE, Company.region)
        city_counts = await self._counts_by_column(ProductType.SERVICE, Company.city)
        return ServiceFiltersResponse(
            countries=self._items(locations["countries"], country_counts),
            federal_districts=self._items(locations["federal_districts"], district_counts),
            regions=self._items(locations["regions"], region_counts),
            cities=self._items(locations["cities"], city_counts),
        )

    async def get_cities_product_count(self, product_type: ProductType) -> List[dict]:
        query = select(
            Company.city.label("city_name"),
            Company.region.label("region_name"),
            func.count(Product.id).label("product_count"),
        ).join(Company, Product.company_id == Company.id).where(
            and_(
                Product.type == product_type,
                Product.is_deleted == False,
                Product.is_hidden == False,
                Company.is_active == True,
                Company.city.isnot(None),
                Company.city != "",
                Company.region.isnot(None),
                Company.region != "",
            )
        ).group_by(Company.city, Company.region)

        result = await self.session.execute(query)
        return [
            {
                "city_name": row.city_name,
                "region_name": row.region_name,
                "product_count": row.product_count,
            }
            for row in result
        ]
