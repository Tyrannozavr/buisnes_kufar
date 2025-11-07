from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.api.company.models.company import Company
    from app.api.authentication.models import User
    from app.api.chats.models.chat import Chat


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    sender_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    sender_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    sender_company: Mapped["Company"] = relationship("Company", foreign_keys=[sender_company_id])
    sender_user: Mapped["User"] = relationship("User", foreign_keys=[sender_user_id])

    def __str__(self):
        return f"Message {self.id} in Chat {self.chat_id}"
