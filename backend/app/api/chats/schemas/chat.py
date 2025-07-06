from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.api.chats.schemas.chat_participant import ChatParticipantResponse


class ChatCreate(BaseModel):
    participant_company_id: int
    title: Optional[str] = None


class ChatResponse(BaseModel):
    id: int
    title: Optional[str]
    is_group: bool
    participants: List[ChatParticipantResponse]
    current_company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatListResponse(BaseModel):
    id: int
    title: Optional[str]
    is_group: bool
    participants: List[ChatParticipantResponse]
    last_message: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
