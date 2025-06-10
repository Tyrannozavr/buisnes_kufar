from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.api.company.models.company import Company


class Message(Base):
    __tablename__ = "messages"

    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Foreign keys
    from_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    to_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)

    # Relationships
    from_company: Mapped["Company"] = relationship("Company", foreign_keys=[from_company_id],
                                                   back_populates="sent_messages")
    to_company: Mapped["Company"] = relationship("Company", foreign_keys=[to_company_id],
                                                 back_populates="received_messages")
