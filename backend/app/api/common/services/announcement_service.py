from fastapi import HTTPException, status

from app.api.common.repositories.announcement_repository import PublicAnnouncementRepository
from app.api.common.schemas.announcements import PublicAnnouncementResponse, PublicAnnouncementListResponse


class PublicAnnouncementService:
    def __init__(self, announcement_repository: PublicAnnouncementRepository):
        self.announcement_repository = announcement_repository

    async def get_all_announcements(self, page: int = 1, per_page: int = 10) -> PublicAnnouncementListResponse:
        """Получить все опубликованные объявления"""
        announcements, total = await self.announcement_repository.get_all_published(page, per_page)

        return PublicAnnouncementListResponse(
            announcements=[PublicAnnouncementResponse.model_validate(announcement) for announcement in announcements],
            total=total,
            page=page,
            per_page=per_page
        )

    async def get_announcement_by_id(self, announcement_id: int) -> PublicAnnouncementResponse:
        """Получить опубликованное объявление по ID"""
        announcement = await self.announcement_repository.get_published_by_id(announcement_id)

        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found or not published"
            )

        return PublicAnnouncementResponse.model_validate(announcement)

    async def get_company_announcements(self, company_id: int, page: int = 1,
                                        per_page: int = 10) -> PublicAnnouncementListResponse:
        """Получить опубликованные объявления компании"""
        announcements, total = await self.announcement_repository.get_published_by_company_id(company_id, page,
                                                                                              per_page)

        return PublicAnnouncementListResponse(
            announcements=[PublicAnnouncementResponse.model_validate(announcement) for announcement in announcements],
            total=total,
            page=page,
            per_page=per_page
        )

    async def get_announcements_by_category(self, category: str, page: int = 1,
                                            per_page: int = 10) -> PublicAnnouncementListResponse:
        """Получить опубликованные объявления по категории"""
        announcements, total = await self.announcement_repository.get_published_by_category(category, page, per_page)

        return PublicAnnouncementListResponse(
            announcements=[PublicAnnouncementResponse.model_validate(announcement) for announcement in announcements],
            total=total,
            page=page,
            per_page=per_page
        )
