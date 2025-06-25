from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, computed_field, ConfigDict
from app.core.config import settings


class CompanyInfo(BaseModel):
    id: int
    name: str
    logo: Optional[str] = None
    
    @computed_field
    @property
    def logo_url(self) -> Optional[str]:
        """Возвращает полный URL логотипа компании"""
        if not self.logo:
            return None
        return f"{settings.BASE_IMAGE_URL}{self.logo}"
    
    model_config = ConfigDict(from_attributes=True)


class AnnouncementImagesMixin(BaseModel):
    images: Optional[List[str]] = Field(default=[], exclude=True)

    @computed_field
    @property
    def image_urls(self) -> List[str]:
        """Возвращает полные URL изображений"""
        if not self.images:
            return []
        return [f"{settings.BASE_IMAGE_URL}{image}" for image in self.images]

    @computed_field
    @property
    def image_url(self) -> Optional[str]:
        """Возвращает URL первого изображения для отображения в списке"""
        if not self.images:
            return None
        return f"{settings.BASE_IMAGE_URL}{self.images[0]}"


class PublicAnnouncementResponse(AnnouncementImagesMixin):
    id: int
    title: str
    content: str
    category: str
    images: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    company: CompanyInfo

    model_config = ConfigDict(from_attributes=True)


class PublicAnnouncementListResponse(BaseModel):
    announcements: List[PublicAnnouncementResponse]
    total: int
    page: int
    per_page: int 