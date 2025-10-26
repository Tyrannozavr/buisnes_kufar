from typing import Optional, Tuple, List

from sqlalchemy import select, func, or_, and_
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

    async def get_companies_with_filters(
            self,
            page: int = 1,
            per_page: int = 10,
            search: Optional[str] = None,
            cities: Optional[List[int]] = None
    ) -> Tuple[List[Company], int]:
        """
        Получить активные компании с фильтрацией по городам
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            search: Поиск по названию компании
            cities: Список ID городов для фильтрации
            
        Returns:
            Tuple[List[Company], int]: (список компаний, общее количество)
        """
        from sqlalchemy import text
        from app.api.common.models.city import City
        
        # Базовые условия
        conditions = [
            Company.is_active == True
        ]
        
        # Добавляем фильтр по названию
        if search:
            conditions.append(Company.name.ilike(f"%{search}%"))
        
        # Добавляем фильтр по городам
        if cities:
            # Получаем названия городов по их ID
            cities_query = select(City.name).where(City.id.in_(cities))
            cities_result = await self.session.execute(cities_query)
            city_names = [row[0] for row in cities_result]
            
            if city_names:
                conditions.append(Company.city.in_(city_names))
        
        # Получаем общее количество
        count_query = select(func.count(Company.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()
        
        # Получаем компании с пагинацией
        offset = (page - 1) * per_page
        query = select(Company).options(
            selectinload(Company.officials)
        ).where(and_(*conditions)).order_by(Company.registration_date.desc()).offset(offset).limit(per_page)
        
        result = await self.session.execute(query)
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
            per_page: int = 10,
            search: Optional[str] = None,
            country: Optional[str] = None,
            federal_district: Optional[str] = None,
            region: Optional[str] = None,
            city: Optional[str] = None
    ) -> Tuple[List[Company], int]:
        """
        Получить компании, предоставляющие услуги (включая те, что делают оба)
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            search: Поиск по названию компании
            country: Фильтр по стране
            federal_district: Фильтр по федеральному округу
            region: Фильтр по региону
            city: Фильтр по городу
            
        Returns:
            Tuple[List[Company], int]: (список компаний, общее количество)
        """
        # Базовые условия - все активные компании могут предоставлять услуги
        conditions = [
            Company.is_active == True
        ]
        
        # Добавляем фильтры
        if search:
            conditions.append(Company.name.ilike(f"%{search}%"))
        if country:
            conditions.append(Company.country == country)
        if federal_district:
            conditions.append(Company.federal_district == federal_district)
        if region:
            conditions.append(Company.region == region)
        if city:
            conditions.append(Company.city == city)
        
        base_query = select(Company).options(
            selectinload(Company.officials)
        ).where(*conditions).order_by(Company.registration_date.desc())

        # Получаем общее количество
        count_query = select(func.count(Company.id)).where(*conditions)
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
            search: str = None,
            cities: Optional[List[int]] = None
    ) -> Tuple[List[Company], int]:
        """
        Получить компании, производящие товары (включая те, что делают оба)
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            search: Поиск по названию компании
            cities: Список ID городов для фильтрации
            
        Returns:
            Tuple[List[Company], int]: (список компаний, общее количество)
        """
        from sqlalchemy import or_, func
        from app.api.common.models.city import City
        
        # Базовые условия
        conditions = [
            Company.is_active == True,
            or_(
                Company.business_type == BusinessType.GOODS,
                Company.business_type == BusinessType.BOTH
            )
        ]
        
        # Добавляем фильтр по названию
        if search:
            conditions.append(Company.name.ilike(f"%{search}%"))
        
        # Добавляем фильтр по городам
        if cities:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔍 Companies filter cities={cities}")
            
            # Получаем названия городов по их ID
            cities_query = select(City.name).where(City.id.in_(cities))
            cities_result = await self.session.execute(cities_query)
            city_names = [row[0] for row in cities_result]
            logger.info(f"🌆 City names: {city_names}")
            
            if city_names:
                # Фильтруем по названию города
                conditions.append(Company.city.in_(city_names))
                logger.info(f"✅ Added city filter")
        
        base_query = select(Company).options(
            selectinload(Company.officials)
        ).where(*conditions).order_by(Company.registration_date.desc())

        # Получаем общее количество
        count_query = select(func.count(Company.id)).where(*conditions)
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()

        # Применяем пагинацию
        offset = (page - 1) * per_page
        paginated_query = base_query.offset(offset).limit(per_page)

        # Выполняем запрос
        result = await self.session.execute(paginated_query)
        companies = result.scalars().all()

        return list(companies), total_count
