from typing import Optional, List, Tuple

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.company.models.company import Company
from app.api.products.models.product import Product, ProductType
from app.api.products.schemas.products import ProductsResponse, ProductListItem, PaginationInfo


class CompanyProductsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Получить продукт по ID (только активные и не скрытые)"""
        query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.id == product_id,
                Product.is_deleted == False,
                Product.is_hidden == False
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Product]:
        """Получить продукт по slug (только активные и не скрытые)"""
        query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.slug == slug,
                Product.is_deleted == False,
                Product.is_hidden == False
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_article(self, article: str) -> Optional[Product]:
        """Получить продукт по article (только активные и не скрытые)"""
        query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.article == article,
                Product.is_deleted == False,
                Product.is_hidden == False
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_company_id(
            self,
            company_id: int,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Получить все продукты компании с пагинацией"""
        # Базовые условия
        conditions = [
            Product.company_id == company_id,
            Product.is_deleted == False
        ]
        
        if not include_hidden:
            conditions.append(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем продукты с пагинацией
        query = select(Product).options(
            selectinload(Product.company)
        ).where(and_(*conditions)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        products = result.scalars().all()

        return list(products), total

    async def get_by_company_slug(
            self,
            company_slug: str,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Получить все продукты компании по slug с пагинацией"""
        # Базовые условия
        conditions = [Product.is_deleted == False]
        
        if not include_hidden:
            conditions.append(Product.is_hidden == False)

        # Получаем общее количество с join на компанию
        count_query = (
            select(func.count(Product.id))
            .join(Company, Product.company_id == Company.id)
            .where(and_(*conditions))
            .where(Company.slug == company_slug)
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем продукты с пагинацией
        query = (
            select(Product)
            .options(selectinload(Product.company))
            .join(Company, Product.company_id == Company.id)
            .where(and_(*conditions))
            .where(Company.slug == company_slug)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        products = result.scalars().all()

        return list(products), total

    async def get_all_products(
            self,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Получить все продукты всех компаний с пагинацией"""
        # Базовые условия
        conditions = [Product.is_deleted == False]
        
        if not include_hidden:
            conditions.append(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем продукты с пагинацией
        query = select(Product).options(
            selectinload(Product.company)
        ).where(and_(*conditions)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        products = result.scalars().all()

        return list(products), total

    async def get_all_services(
            self,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Получить все услуги всех компаний с пагинацией"""
        # Базовые условия
        conditions = [
            Product.type == ProductType.SERVICE,
            Product.is_deleted == False
        ]
        
        if not include_hidden:
            conditions.append(Product.is_hidden == False)
        
        # Получаем общее количество
        count_query = select(func.count(Product.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем услуги с пагинацией
        query = select(Product).options(
            selectinload(Product.company)
        ).where(and_(*conditions)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        services = result.scalars().all()

        return list(services), total

    async def get_all_services_with_company(
            self,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Получить все услуги всех компаний с пагинацией и загруженными данными компании"""
        # Базовые условия
        conditions = [
            Product.type == ProductType.SERVICE,
            Product.is_deleted == False
        ]
        
        if not include_hidden:
            conditions.append(Product.is_hidden == False)

        # Получаем общее количество напрямую из БД без JOIN
        # Используем прямой SQL чтобы избежать cartesian product
        from sqlalchemy import text
        count_sql = text("SELECT COUNT(*) FROM products WHERE type = 'SERVICE' AND is_deleted = false AND is_hidden = false")
        count_result = await self.session.execute(count_sql)
        total = count_result.scalar()

        # Получаем услуги с пагинацией
        query = select(Product).options(
            selectinload(Product.company)
        ).where(and_(*conditions)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        services = result.scalars().all()

        return list(services), total

    async def get_all_goods(
            self,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Получить все товары всех компаний с пагинацией"""
        # Базовый запрос для товаров
        base_query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.type == ProductType.GOOD,
                Product.is_deleted == False
            )
        )

        # Добавляем фильтр по видимости
        if not include_hidden:
            base_query = base_query.where(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).where(
            and_(
                Product.type == ProductType.GOOD,
                Product.is_deleted == False
            )
        )
        if not include_hidden:
            count_query = count_query.where(Product.is_hidden == False)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем товары с пагинацией
        query = base_query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        goods = result.scalars().all()

        return list(goods), total

    async def get_all_goods_with_company(
            self,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Получить все товары всех компаний с пагинацией и загруженными данными компании"""
        # Базовые условия
        conditions = [
            Product.type == ProductType.GOOD,
            Product.is_deleted == False
        ]
        
        if not include_hidden:
            conditions.append(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем товары с пагинацией
        query = select(Product).options(
            selectinload(Product.company)
        ).where(and_(*conditions)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        goods = result.scalars().all()

        return list(goods), total

    async def get_services_by_company_id(
            self,
            company_id: int,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Получить все услуги конкретной компании с пагинацией"""
        # Базовые условия
        conditions = [
            Product.company_id == company_id,
            Product.type == ProductType.SERVICE,
            Product.is_deleted == False
        ]
        
        if not include_hidden:
            conditions.append(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id.distinct())).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем услуги с пагинацией
        query = select(Product).options(
            selectinload(Product.company)
        ).where(and_(*conditions)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        services = result.scalars().all()

        return list(services), total

    async def get_goods_by_company_id(
            self,
            company_id: int,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Получить все товары конкретной компании с пагинацией"""
        # Базовые условия
        conditions = [
            Product.company_id == company_id,
            Product.type == ProductType.GOOD,
            Product.is_deleted == False
        ]
        
        if not include_hidden:
            conditions.append(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id.distinct())).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем товары с пагинацией
        query = select(Product).options(
            selectinload(Product.company)
        ).where(and_(*conditions)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        goods = result.scalars().all()

        return list(goods), total

    async def search_products(
            self,
            search_term: str,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Поиск продуктов по названию или описанию"""
        from sqlalchemy import or_

        # Базовые условия
        conditions = [
            Product.is_deleted == False,
            or_(
                Product.name.ilike(f"%{search_term}%"),
                Product.description.ilike(f"%{search_term}%"),
                Product.article.ilike(f"%{search_term}%")
            )
        ]
        
        if not include_hidden:
            conditions.append(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id.distinct())).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем продукты с пагинацией
        query = select(Product).options(
            selectinload(Product.company)
        ).where(and_(*conditions)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        products = result.scalars().all()

        return list(products), total

    async def get_products_by_price_range(
            self,
            min_price: float,
            max_price: float,
            skip: int = 0,
            limit: int = 100,
            include_hidden: bool = False
    ) -> Tuple[List[Product], int]:
        """Получить продукты в диапазоне цен"""
        # Базовые условия
        conditions = [
            Product.is_deleted == False,
            Product.price >= min_price,
            Product.price <= max_price
        ]
        
        if not include_hidden:
            conditions.append(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id.distinct())).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем продукты с пагинацией
        query = select(Product).options(
            selectinload(Product.company)
        ).where(and_(*conditions)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        products = result.scalars().all()

        return list(products), total

    async def get_latest_products(
            self,
            limit: int = 20,
            include_hidden: bool = False
    ) -> List[Product]:
        """Получить последние добавленные продукты"""
        from sqlalchemy import desc

        # Базовый запрос для последних продуктов
        base_query = select(Product).options(
            selectinload(Product.company)
        ).where(Product.is_deleted == False)

        # Добавляем фильтр по видимости
        if not include_hidden:
            base_query = base_query.where(Product.is_hidden == False)

        # Сортируем по дате создания и ограничиваем количество
        query = base_query.order_by(desc(Product.created_at)).limit(limit)
        result = await self.session.execute(query)
        products = result.scalars().all()

        return list(products)

    async def get_company_products(
            self,
            company_id: Optional[int] = None,
            company_slug: Optional[str] = None,
            page: int = 1,
            per_page: int = 10
    ) -> Tuple[List[Product], int]:
        """
        Получить продукты компании с пагинацией
        
        Args:
            company_id: ID компании (опционально)
            company_slug: Slug компании (опционально)
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            
        Returns:
            Tuple[List[Product], int]: (список продуктов, общее количество)
        """
        if company_id is None and company_slug is None:
            raise ValueError("Необходимо указать либо company_id, либо company_slug")

        # Базовые условия
        conditions = [
            Product.is_deleted == False,
            Product.is_hidden == False
        ]
        
        if company_id:
            conditions.append(Company.id == company_id)
            count_join = Company.id == Product.company_id
            count_query = (
                select(func.count(Product.id.distinct()))
                .join(Company, count_join)
                .where(and_(*conditions))
            )
        else:
            conditions.append(Company.slug == company_slug)
            count_join = Company.id == Product.company_id
            count_query = (
                select(func.count(Product.id.distinct()))
                .join(Company, count_join)
                .where(and_(*conditions))
            )

        # Получаем общее количество
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()

        # Получаем продукты с пагинацией
        offset = (page - 1) * per_page
        paginated_query = (
            select(Product)
            .join(Company)
            .where(and_(*conditions))
            .offset(offset)
            .limit(per_page)
        )
        result = await self.session.execute(paginated_query)
        products = result.scalars().all()

        return list(products), total_count

    async def get_company_paginated_products(
            self,
            company_id: Optional[int] = None,
            company_slug: Optional[str] = None,
            page: int = 1,
            per_page: int = 10
    ) -> ProductsResponse:
        """
        Получить пагинированный ответ с продуктами компании
        
        Args:
            company_id: ID компании (опционально)
            company_slug: Slug компании (опционально)
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            
        Returns:
            ProductsResponse: Ответ с списком продуктов и информацией о пагинации
        """
        products, total_count = await self.get_company_products(
            company_id=company_id,
            company_slug=company_slug,
            page=page,
            per_page=per_page
        )

        total_pages = (total_count + per_page - 1) // per_page

        return ProductsResponse(
            data=[ProductListItem.model_validate(product) for product in products],
            pagination=PaginationInfo(
                total=total_count,
                page=page,
                perPage=per_page,
                totalPages=total_pages
            )
        )
