from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.products.models.product import Product, ProductType
from app.api.company.models.company import Company


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

    async def get_by_slug(self, slug: str, company_id: int) -> Optional[Product]:
        """Получить продукт по slug и company_id (только активные и не скрытые)"""
        query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.slug == slug,
                Product.company_id == company_id,
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
        # Базовый запрос
        base_query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.company_id == company_id,
                Product.is_deleted == False
            )
        )

        # Добавляем фильтр по видимости
        if not include_hidden:
            base_query = base_query.where(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем продукты с пагинацией
        query = base_query.offset(skip).limit(limit)
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
        # Базовый запрос
        base_query = select(Product).options(
            selectinload(Product.company)
        ).where(Product.is_deleted == False)

        # Добавляем фильтр по видимости
        if not include_hidden:
            base_query = base_query.where(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем продукты с пагинацией
        query = base_query.offset(skip).limit(limit)
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
        # Базовый запрос для услуг
        base_query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.type == ProductType.SERVICE,
                Product.is_deleted == False
            )
        )

        # Добавляем фильтр по видимости
        if not include_hidden:
            base_query = base_query.where(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем услуги с пагинацией
        query = base_query.offset(skip).limit(limit)
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
        count_query = select(func.count(Product.id)).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем товары с пагинацией
        query = base_query.offset(skip).limit(limit)
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
        # Базовый запрос для услуг компании
        base_query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.company_id == company_id,
                Product.type == ProductType.SERVICE,
                Product.is_deleted == False
            )
        )

        # Добавляем фильтр по видимости
        if not include_hidden:
            base_query = base_query.where(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем услуги с пагинацией
        query = base_query.offset(skip).limit(limit)
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
        # Базовый запрос для товаров компании
        base_query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.company_id == company_id,
                Product.type == ProductType.GOOD,
                Product.is_deleted == False
            )
        )

        # Добавляем фильтр по видимости
        if not include_hidden:
            base_query = base_query.where(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем товары с пагинацией
        query = base_query.offset(skip).limit(limit)
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

        # Базовый запрос с поиском
        base_query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.is_deleted == False,
                or_(
                    Product.name.ilike(f"%{search_term}%"),
                    Product.description.ilike(f"%{search_term}%"),
                    Product.article.ilike(f"%{search_term}%")
                )
            )
        )

        # Добавляем фильтр по видимости
        if not include_hidden:
            base_query = base_query.where(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем продукты с пагинацией
        query = base_query.offset(skip).limit(limit)
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
        # Базовый запрос с фильтром по цене
        base_query = select(Product).options(
            selectinload(Product.company)
        ).where(
            and_(
                Product.is_deleted == False,
                Product.price >= min_price,
                Product.price <= max_price
            )
        )

        # Добавляем фильтр по видимости
        if not include_hidden:
            base_query = base_query.where(Product.is_hidden == False)

        # Получаем общее количество
        count_query = select(func.count(Product.id)).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем продукты с пагинацией
        query = base_query.offset(skip).limit(limit)
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