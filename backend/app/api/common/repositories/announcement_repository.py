from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.company.models.announcement import Announcement


class PublicAnnouncementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_published_by_id(self, announcement_id: int) -> Optional[Announcement]:
        """Получить опубликованное объявление по ID"""
        query = select(Announcement).options(
            selectinload(Announcement.company)
        ).where(
            Announcement.id == announcement_id,
            Announcement.published == True
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_published(self, page: int = 1, per_page: int = 10) -> tuple[List[Announcement], int]:
        """Получить все опубликованные объявления с пагинацией"""
        # Общее количество опубликованных объявлений
        count_query = select(func.count(Announcement.id)).where(Announcement.published == True)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Опубликованные объявления с пагинацией
        offset = (page - 1) * per_page
        query = select(Announcement).options(
            selectinload(Announcement.company)
        ).where(
            Announcement.published == True
        ).order_by(Announcement.created_at.desc()).offset(offset).limit(per_page)

        result = await self.session.execute(query)
        announcements = result.scalars().all()

        return list(announcements), total

    async def get_published_by_company_id(self, company_id: int, page: int = 1, per_page: int = 10) -> tuple[
        List[Announcement], int]:
        """Получить опубликованные объявления конкретной компании"""
        # Общее количество опубликованных объявлений компании
        count_query = select(func.count(Announcement.id)).where(
            Announcement.company_id == company_id,
            Announcement.published == True
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Опубликованные объявления компании с пагинацией
        offset = (page - 1) * per_page
        query = select(Announcement).options(
            selectinload(Announcement.company)
        ).where(
            Announcement.company_id == company_id,
            Announcement.published == True
        ).order_by(Announcement.created_at.desc()).offset(offset).limit(per_page)

        result = await self.session.execute(query)
        announcements = result.scalars().all()

        return list(announcements), total

    async def get_published_by_category(self, category: str, page: int = 1, per_page: int = 10) -> tuple[
        List[Announcement], int]:
        """Получить опубликованные объявления по категории"""
        # Общее количество опубликованных объявлений в категории
        count_query = select(func.count(Announcement.id)).where(
            Announcement.category == category,
            Announcement.published == True
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Опубликованные объявления в категории с пагинацией
        offset = (page - 1) * per_page
        query = select(Announcement).options(
            selectinload(Announcement.company)
        ).where(
            Announcement.category == category,
            Announcement.published == True
        ).order_by(Announcement.created_at.desc()).offset(offset).limit(per_page)

        result = await self.session.execute(query)
        announcements = result.scalars().all()

        return list(announcements), total
