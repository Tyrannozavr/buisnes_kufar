"""
Модель формы документа по сделке.
Одна запись на пару (deal_id, document_type). updated_by_company_id нужен для диалога «Контрагент изменил данные».
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.api.company.models.company import Company
    from app.api.purchases.models import Order  # noqa: F401


class DealDocumentForm(Base):
    """Payload формы редактора документа (заказ, счёт, договор и т.д.) по сделке."""
    __tablename__ = "deal_document_forms"
    __table_args__ = (
        UniqueConstraint("deal_id", "document_type", name="uq_deal_document_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    deal_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), nullable=True
    )

    # Для проверки «контрагент изменил» на фронте: если updated_by_company_id != company_id текущего юзера
    # и updated_at > last_seen — показать «Обновить данные?».
    updated_by_company: Mapped[Optional["Company"]] = relationship("Company", foreign_keys=[updated_by_company_id])
    order: Mapped["Order"] = relationship("Order")
