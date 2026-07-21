from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ShipmentRequest(Base):
	__tablename__ = "shipment_requests"

	client_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
	carrier_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
	status: Mapped[str] = mapped_column(String(16), nullable=False, default="passive", index=True)
	is_highlighted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	search_filters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
	matched_vehicle_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
	activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
	expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class Shipment(Base):
	__tablename__ = "shipments"

	number: Mapped[str] = mapped_column(String(5), nullable=False)
	year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
	client_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
	carrier_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
	request_id: Mapped[int] = mapped_column(ForeignKey("shipment_requests.id", ondelete="CASCADE"), unique=True, index=True)
	deal_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)
	cargo_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
	vehicle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("company_vehicles.id", ondelete="SET NULL"), nullable=True)
	driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("company_drivers.id", ondelete="SET NULL"), nullable=True)
	transport_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class VehicleFavorite(Base):
	__tablename__ = "vehicle_favorites"
	__table_args__ = (UniqueConstraint("client_company_id", "vehicle_id", name="uq_vehicle_favorite_company_vehicle"),)

	client_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
	vehicle_id: Mapped[int] = mapped_column(ForeignKey("company_vehicles.id", ondelete="CASCADE"), index=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class RequestFavorite(Base):
	__tablename__ = "request_favorites"
	__table_args__ = (UniqueConstraint("carrier_company_id", "request_id", name="uq_request_favorite_company_request"),)

	carrier_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
	request_id: Mapped[int] = mapped_column(ForeignKey("shipment_requests.id", ondelete="CASCADE"), index=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
