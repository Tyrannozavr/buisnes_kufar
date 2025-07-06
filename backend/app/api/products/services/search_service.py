from typing import List, Tuple, Optional
from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.products.models.product import Product, ProductType
from app.api.company.models.company import Company
from app.api.products.schemas.product import ProductResponse, ProductListResponse
from app.api.company.schemas.filters import ProductFilterRequest, ServiceFilterRequest
from app.api.products.services.cache_service import product_location_cache


class ProductSearchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_products(self, filter_request: ProductFilterRequest) -> ProductListResponse:
        """Поиск товаров с фильтрацией"""
        # Базовый запрос
        base_conditions = [
            Product.type == ProductType.GOOD,
            Product.is_deleted == False,
            Product.is_hidden == False
        ]
        conditions = await self._get_conditions(filter_request)
        all_conditions = base_conditions + conditions

        # Основной запрос
        query = (
            select(Product)
            .options(selectinload(Product.company))
            .join(Company, Product.company_id == Company.id)
            .where(and_(*all_conditions))
        )

        # Подсчёт total
        count_query = (
            select(func.count(Product.id))
            .join(Company, Product.company_id == Company.id)
            .where(and_(*all_conditions))
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем продукты с пагинацией
        query = query.offset(filter_request.skip).limit(filter_request.limit)
        result = await self.session.execute(query)
        products = result.scalars().all()

        # Преобразуем в response
        product_responses = [ProductResponse.model_validate(product) for product in products]

        return ProductListResponse(
            products=product_responses,
            total=total,
            page=filter_request.skip // filter_request.limit + 1,
            per_page=filter_request.limit
        )

    async def search_services(self, filter_request: ServiceFilterRequest) -> ProductListResponse:
        """Поиск услуг с фильтрацией"""
        base_conditions = [
            Product.type == ProductType.SERVICE,
            Product.is_deleted == False,
            Product.is_hidden == False
        ]
        conditions = await self._get_conditions(filter_request)
        all_conditions = base_conditions + conditions

        query = (
            select(Product)
            .options(selectinload(Product.company))
            .join(Company, Product.company_id == Company.id)
            .where(and_(*all_conditions))
        )

        count_query = (
            select(func.count(Product.id))
            .join(Company, Product.company_id == Company.id)
            .where(and_(*all_conditions))
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        query = query.offset(filter_request.skip).limit(filter_request.limit)
        result = await self.session.execute(query)
        services = result.scalars().all()

        service_responses = [ProductResponse.model_validate(service) for service in services]

        return ProductListResponse(
            products=service_responses,
            total=total,
            page=filter_request.skip // filter_request.limit + 1,
            per_page=filter_request.limit
        )

    async def _get_conditions(self, filter_request):
        """Формирует условия для фильтрации"""
        conditions = []

        # Поиск по названию
        if filter_request.search:
            search_term = f"%{filter_request.search}%"
            conditions.append(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )

        # Фильтр по стране
        if filter_request.country:
            conditions.append(Company.country == filter_request.country)

        # Фильтр по федеральному округу
        if filter_request.federal_district:
            conditions.append(Company.federal_district == filter_request.federal_district)

        # Фильтр по региону
        if filter_request.region:
            conditions.append(Company.region == filter_request.region)

        # Фильтр по городу
        if filter_request.city:
            conditions.append(Company.city == filter_request.city)

        # Фильтр по цене
        if filter_request.min_price is not None:
            conditions.append(Product.price >= filter_request.min_price)

        if filter_request.max_price is not None:
            conditions.append(Product.price <= filter_request.max_price)

        # Фильтр по наличию
        if filter_request.in_stock is not None:
            # Здесь можно добавить логику для проверки наличия
            # Пока оставляем как есть
            pass

        return conditions

    async def _apply_filters(self, query, filter_request):
        # Не используется, оставлено для обратной совместимости
        return query 