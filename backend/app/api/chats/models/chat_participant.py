from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.api.chats.models.chat import Chat
    from app.api.company.models.company import Company
    from app.api.authentication.models import User


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    left_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="participants")
    company: Mapped["Company"] = relationship("Company")
    user: Mapped["User"] = relationship("User")

    def __str__(self):
        return f"ChatParticipant {self.id} in Chat {self.chat_id}"
