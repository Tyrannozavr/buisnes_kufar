from typing import Optional, List

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.company.models.announcement import Announcement
from app.api.company.schemas.announcements import AnnouncementCreate, AnnouncementUpdate


class AnnouncementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, announcement_id: int) -> Optional[Announcement]:
        """Получить объявление по ID"""
        query = select(Announcement).options(
            selectinload(Announcement.company)
        ).where(Announcement.id == announcement_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_company_id(self, company_id: int, page: int = 1, per_page: int = 10) -> tuple[
        List[Announcement], int]:
        """Получить все объявления компании с пагинацией"""
        # Общее количество объявлений
        count_query = select(func.count(Announcement.id)).where(Announcement.company_id == company_id)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Объявления с пагинацией
        offset = (page - 1) * per_page
        query = select(Announcement).options(
            selectinload(Announcement.company)
        ).where(Announcement.company_id == company_id).order_by(Announcement.created_at.desc()).offset(offset).limit(
            per_page)

        result = await self.session.execute(query)
        announcements = result.scalars().all()

        return list(announcements), total

    async def create(self, announcement_data: AnnouncementCreate, company_id: int) -> Announcement:
        """Создать новое объявление"""
        announcement = Announcement(
            **announcement_data.model_dump(),
            company_id=company_id
        )
        self.session.add(announcement)
        await self.session.commit()
        await self.session.refresh(announcement)
        return announcement

    async def update(self, announcement_id: int, announcement_data: AnnouncementUpdate) -> Optional[Announcement]:
        """Обновить объявление"""
        update_data = announcement_data.model_dump(exclude_unset=True)

        if update_data:
            await self.session.execute(
                update(Announcement)
                .where(Announcement.id == announcement_id)
                .values(**update_data)
            )
            await self.session.commit()

        return await self.get_by_id(announcement_id)

    async def delete(self, announcement_id: int) -> bool:
        """Удалить объявление"""
        result = await self.session.execute(
            delete(Announcement).where(Announcement.id == announcement_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def get_published_by_company_id(self, company_id: int, page: int = 1, per_page: int = 10) -> tuple[
        List[Announcement], int]:
        """Получить только опубликованные объявления компании"""
        # Общее количество опубликованных объявлений
        count_query = select(func.count(Announcement.id)).where(
            Announcement.company_id == company_id,
            Announcement.published == True
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Опубликованные объявления с пагинацией
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
