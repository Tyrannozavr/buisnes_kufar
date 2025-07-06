from typing import Optional, Tuple, List
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.company.models.company import Company, BusinessType


class CompaniesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_companies_paginated(
        self, 
        page: int = 1, 
        per_page: int = 10, 
        limit: Optional[int] = None
    ) -> Tuple[List[Company], int]:
        """
        Получить активные компании с пагинацией, отсортированные по дате регистрации
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            limit: Ограничение общего количества (опционально)
            
        Returns:
            Tuple[List[Company], int]: (список активных компаний, общее количество)
        """
        # Базовый запрос с загрузкой связанных данных и фильтром по активным компаниям
        base_query = select(Company).options(
            selectinload(Company.officials)
        ).where(Company.is_active == True).order_by(Company.registration_date.desc())
        
        # Получаем общее количество активных компаний
        count_query = select(func.count(Company.id)).where(Company.is_active == True)
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()
        
        # Применяем лимит если указан
        if limit is not None:
            total_count = min(total_count, limit)
            base_query = base_query.limit(limit)
        
        # Применяем пагинацию
        offset = (page - 1) * per_page
        paginated_query = base_query.offset(offset).limit(per_page)
        
        # Выполняем запрос
        result = await self.session.execute(paginated_query)
        companies = result.scalars().all()
        
        return list(companies), total_count

    async def get_latest_companies(self, limit: int = 6) -> List[Company]:
        """
        Получить последние активные компании
        
        Args:
            limit: Количество компаний
            
        Returns:
            List[Company]: Список последних активных компаний
        """
        query = select(Company).options(
            selectinload(Company.officials)
        ).where(Company.is_active == True).order_by(Company.registration_date.desc()).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """
        Получить компанию по ID

        Args:
            company_id: ID компании
        Returns:
            Optional[Company]: Компания или None
        """
        query = select(Company).options(
            selectinload(Company.officials)
        ).where(Company.id == company_id).where(Company.is_active == True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_company_by_slug(self, company_slug: str, include_products: bool = False) -> Optional[Company]:
        """
        Получить компанию по slug

        Args:
            company_slug: Slug компании
            include_products: Загружать ли продукты компании
        Returns:
            Optional[Company]: Компания или None
        """
        query = select(Company).options(
            selectinload(Company.officials)
        )
        
        if include_products:
            query = query.options(selectinload(Company.products))
            
        query = query.where(Company.slug == company_slug).where(Company.is_active == True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()



    async def get_services_companies(
        self, 
        page: int = 1, 
        per_page: int = 10
    ) -> Tuple[List[Company], int]:
        """
        Получить компании, предоставляющие услуги (включая те, что делают оба)
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            
        Returns:
            Tuple[List[Company], int]: (список компаний, общее количество)
        """
        base_query = select(Company).options(
            selectinload(Company.officials)
        ).where(
            Company.is_active == True,
            or_(
                Company.business_type == BusinessType.SERVICES,
                Company.business_type == BusinessType.BOTH
            )
        ).order_by(Company.registration_date.desc())
        
        # Получаем общее количество
        count_query = select(func.count(Company.id)).where(
            Company.is_active == True,
            or_(
                Company.business_type == BusinessType.SERVICES,
                Company.business_type == BusinessType.BOTH
            )
        )
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()
        
        # Применяем пагинацию
        offset = (page - 1) * per_page
        paginated_query = base_query.offset(offset).limit(per_page)
        
        # Выполняем запрос
        result = await self.session.execute(paginated_query)
        companies = result.scalars().all()
        
        return list(companies), total_count

    async def get_product_companies(
        self, 
        page: int = 1, 
        per_page: int = 10,
        search: str = None
    ) -> Tuple[List[Company], int]:
        """
        Получить компании, производящие товары (включая те, что делают оба)
        """
        from sqlalchemy import or_, func
        base_query = select(Company).options(
            selectinload(Company.officials)
        ).where(
            Company.is_active == True,
            or_(
                Company.business_type == BusinessType.GOODS,
                Company.business_type == BusinessType.BOTH
            )
        )
        if search:
            base_query = base_query.where(Company.name.ilike(f"%{search}%"))
        base_query = base_query.order_by(Company.registration_date.desc())
        
        # Получаем общее количество
        count_query = select(func.count(Company.id)).where(
            Company.is_active == True,
            or_(
                Company.business_type == BusinessType.GOODS,
                Company.business_type == BusinessType.BOTH
            )
        )
        if search:
            count_query = count_query.where(Company.name.ilike(f"%{search}%"))
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()
        
        # Применяем пагинацию
        offset = (page - 1) * per_page
        paginated_query = base_query.offset(offset).limit(per_page)
        
        # Выполняем запрос
        result = await self.session.execute(paginated_query)
        companies = result.scalars().all()
        
        return list(companies), total_count