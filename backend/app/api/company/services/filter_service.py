from typing import List, Dict, Any
from sqlalchemy import select, distinct, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import asyncio
from datetime import datetime, timedelta

from app.api.company.models.company import Company
from app.api.company.schemas.filters import FilterItem, CompanyFiltersResponse
from app.api.products.services.cache_service import product_location_cache


class CompanyFilterService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_company_filters(self) -> CompanyFiltersResponse:
        """Получает фильтры для компаний с кэшированием"""
        # Получаем кэшированные данные
        locations = await product_location_cache.get_company_locations(self.session)
        
        # Создаем ответ
        response = CompanyFiltersResponse(
            countries=[FilterItem(label=country, value=country) for country in sorted(locations['countries'])],
            federal_districts=[FilterItem(label=district, value=district) for district in sorted(locations['federal_districts'])],
            regions=[FilterItem(label=region, value=region) for region in sorted(locations['regions'])],
            cities=[FilterItem(label=city, value=city) for city in sorted(locations['cities'])]
        )
        
        return response 