from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, computed_field, ConfigDict
from app.core.config import settings


class AnnouncementImagesMixin(BaseModel):
    images: Optional[List[str]] = Field(default=[], exclude=True)

    @computed_field
    @property
    def image_urls(self) -> List[str]:
        """Возвращает полные URL изображений"""
        if not self.images:
            return []
        return [f"{settings.BASE_IMAGE_URL}{image}" for image in self.images]


class AnnouncementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Заголовок объявления")
    content: str = Field(..., min_length=1, description="Содержание объявления")
    category: str = Field(..., min_length=1, max_length=100, description="Категория объявления")
    images: Optional[List[str]] = Field(default=[], description="Список относительных путей к изображениям")
    published: bool = Field(default=False, description="Статус публикации")


class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Заголовок объявления")
    content: str = Field(..., min_length=1, description="Содержание объявления")
    category: str = Field(..., min_length=1, max_length=100, description="Категория объявления")
    images: Optional[List[str]] = Field(default=[], description="Список изображений в формате base64")
    published: bool = Field(default=False, description="Статус публикации")


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Заголовок объявления")
    content: Optional[str] = Field(None, min_length=1, description="Содержание объявления")
    category: Optional[str] = Field(None, min_length=1, max_length=100, description="Категория объявления")
    images: Optional[List[str]] = Field(None, description="Список относительных путей к изображениям")
    published: Optional[bool] = Field(None, description="Статус публикации")


class AnnouncementResponse(AnnouncementImagesMixin):
    id: int
    title: str
    content: str
    category: str
    images: Optional[List[str]] = None
    published: bool
    company_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementListResponse(BaseModel):
    announcements: List[AnnouncementResponse]
    total: int
    page: int
    per_page: int 