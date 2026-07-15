import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
	from app.api.company.models.company import Company


class FillAddressKind(str, enum.Enum):
	LOADING = "loading"
	RECEIVING = "receiving"


class CompanyFillAddress(Base):
	"""Адрес погрузки / приёма груза в «Данные заполнения» (ТЗ_15 §7.2)."""

	__tablename__ = "company_fill_addresses"

	company_id: Mapped[int] = mapped_column(
		ForeignKey("companies.id", ondelete="CASCADE"),
		nullable=False,
		index=True,
	)
	kind: Mapped[FillAddressKind] = mapped_column(
		Enum(FillAddressKind, name="filladdresskind", values_callable=lambda x: [e.value for e in x]),
		nullable=False,
		index=True,
	)
	address: Mapped[str] = mapped_column(String(500), nullable=False)
	is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at: Mapped[Optional[datetime]] = mapped_column(
		DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
	)

	company: Mapped["Company"] = relationship("Company", backref="fill_addresses")
