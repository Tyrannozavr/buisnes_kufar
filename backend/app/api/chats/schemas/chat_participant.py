from datetime import datetime

from pydantic import BaseModel, computed_field

from app.core.config import settings


class ChatParticipantResponse(BaseModel):
    id: int
    company_id: int
    user_id: int
    company_name: str
    company_slug: str
    company_logo: str = None  # Keep for backward compatibility
    user_name: str
    is_admin: bool
    joined_at: datetime

    @computed_field
    @property
    def company_logo_url(self) -> str:
        if self.company_logo:
            return f"{settings.BASE_IMAGE_URL}{self.company_logo}"
        return ""

    class Config:
        from_attributes = True
