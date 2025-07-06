from sqlalchemy.ext.asyncio import AsyncSession

from app.api.products.schemas.filters import FilterItem, ProductFiltersResponse, ServiceFiltersResponse
from app.api.products.services.cache_service import product_location_cache


class FilterService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_product_filters(self) -> ProductFiltersResponse:
        """Получает фильтры для товаров с кэшированием"""
        # Получаем кэшированные данные
        locations = await product_location_cache.get_product_locations(self.session)

        # Создаем ответ
        response = ProductFiltersResponse(
            countries=[FilterItem(label=country, value=country) for country in sorted(locations['countries'])],
            federal_districts=[FilterItem(label=district, value=district) for district in
                               sorted(locations['federal_districts'])],
            regions=[FilterItem(label=region, value=region) for region in sorted(locations['regions'])],
            cities=[FilterItem(label=city, value=city) for city in sorted(locations['cities'])]
        )

        return response

    async def get_service_filters(self) -> ServiceFiltersResponse:
        """Получает фильтры для услуг с кэшированием"""
        # Получаем кэшированные данные
        locations = await product_location_cache.get_service_locations(self.session)

        # Создаем ответ
        response = ServiceFiltersResponse(
            countries=[FilterItem(label=country, value=country) for country in sorted(locations['countries'])],
            federal_districts=[FilterItem(label=district, value=district) for district in
                               sorted(locations['federal_districts'])],
            regions=[FilterItem(label=region, value=region) for region in sorted(locations['regions'])],
            cities=[FilterItem(label=city, value=city) for city in sorted(locations['cities'])]
        )

        return response
