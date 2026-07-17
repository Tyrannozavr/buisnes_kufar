from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
	from app.api.company.models.company import Company


class CompanyVehicle(Base):
	"""Транспортное средство компании (ЛК → Транспорт)."""

	__tablename__ = "company_vehicles"

	company_id: Mapped[int] = mapped_column(
		ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
	)
	name: Mapped[str] = mapped_column(String(200), nullable=False)
	plate_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
	vehicle_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
	capacity_tons: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	volume_m3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at: Mapped[Optional[datetime]] = mapped_column(
		DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
	)

	company: Mapped["Company"] = relationship("Company", backref="vehicles")


class CompanyDriver(Base):
	"""Водитель компании (ЛК → Водители)."""

	__tablename__ = "company_drivers"

	company_id: Mapped[int] = mapped_column(
		ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
	)
	full_name: Mapped[str] = mapped_column(String(200), nullable=False)
	phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
	license_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
	notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at: Mapped[Optional[datetime]] = mapped_column(
		DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
	)

	company: Mapped["Company"] = relationship("Company", backref="drivers")
