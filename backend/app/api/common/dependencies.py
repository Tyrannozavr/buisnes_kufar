from typing import Annotated

from fastapi import Depends

from app.api.common.repositories.announcement_repository import PublicAnnouncementRepository
from app.api.common.services.announcement_service import PublicAnnouncementService
from app.db.dependencies import async_db_dep


def get_public_announcement_repository(session: async_db_dep) -> PublicAnnouncementRepository:
    """Зависимость для репозитория публичных объявлений"""
    return PublicAnnouncementRepository(session=session)


def get_public_announcement_service(

        repository: PublicAnnouncementRepository = Depends(get_public_announcement_repository)
) -> PublicAnnouncementService:
    """Зависимость для сервиса публичных объявлений"""
    return PublicAnnouncementService(announcement_repository=repository)


public_announcement_service_dep = Annotated[PublicAnnouncementService, Depends(get_public_announcement_service)]
