from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.company.models.company import Company


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
        Получить компании с пагинацией, отсортированные по дате регистрации
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            limit: Ограничение общего количества (опционально)
            
        Returns:
            Tuple[List[Company], int]: (список компаний, общее количество)
        """
        # Базовый запрос с загрузкой связанных данных
        base_query = select(Company).options(
            selectinload(Company.officials)
        ).order_by(Company.registration_date.desc())
        
        # Получаем общее количество компаний
        count_query = select(func.count(Company.id))
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
        Получить последние компании
        
        Args:
            limit: Количество компаний
            
        Returns:
            List[Company]: Список последних компаний
        """
        query = select(Company).options(
            selectinload(Company.officials)
        ).order_by(Company.registration_date.desc()).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all()) 