from datetime import datetime, date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, ForeignKey, Boolean, DateTime, Float, JSON
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
	trailer_plate_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
	trailer_length_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	trailer_width_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	trailer_height_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	load_date: Mapped[Optional[date]] = mapped_column(nullable=True)
	body_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
	loading_methods: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
	adr_classes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
	from_locations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
	to_locations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
	partial_load: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	partial_load_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	partial_load_volume_m3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
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
	inn: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
	notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at: Mapped[Optional[datetime]] = mapped_column(
		DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
	)

	company: Mapped["Company"] = relationship("Company", backref="drivers")
