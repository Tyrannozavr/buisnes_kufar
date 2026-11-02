from datetime import date, datetime, timedelta
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class TransportSearchFilters(BaseModel):
	body_types: list[str] = Field(default_factory=list)
	loading_methods: list[str] = Field(default_factory=list)
	adr_classes: list[str] = Field(default_factory=list)
	capacity_min_kg: Optional[float] = None
	capacity_max_kg: Optional[float] = None
	cargo_weight_kg: Optional[float] = None
	volume_min_m3: Optional[float] = None
	volume_max_m3: Optional[float] = None
	cargo_volume_m3: Optional[float] = None
	partial_load: bool = False
	load_date: Optional[date] = None
	from_locations: list[dict[str, Any]] = Field(default_factory=list)
	to_locations: list[dict[str, Any]] = Field(default_factory=list)


class CargoUpdate(BaseModel):
	loading_date: Optional[date] = None
	loading_time: Optional[str] = Field(default=None, max_length=32)
	loading_address: Optional[str] = Field(default=None, max_length=500)
	unloading_date: Optional[date] = None
	unloading_time: Optional[str] = Field(default=None, max_length=32)
	unloading_address: Optional[str] = Field(default=None, max_length=500)
	route: Optional[str] = Field(default=None, max_length=500)
	contact_loading: Optional[dict[str, Any]] = None
	contact_unloading: Optional[dict[str, Any]] = None
	cargo_name: Optional[str] = Field(default=None, max_length=300)
	transport_conditions: Optional[str] = Field(default=None, max_length=1000)
	net_weight: Optional[float] = None
	gross_weight: Optional[float] = None
	places_count: Optional[int] = Field(default=None, ge=0, le=1_000_000)
	volume: Optional[float] = None
	marking: Optional[str] = Field(default=None, max_length=300)
	packaging_type: Optional[str] = Field(default=None, max_length=200)
	packaging: Optional[str] = Field(default=None, max_length=300)
	seal: Optional[str] = Field(default=None, max_length=200)
	rate: Optional[float] = None
	payment_terms: Optional[str] = Field(default=None, max_length=500)
	declared_value: Optional[float] = None
	dangerous_goods: Optional[list[str]] = Field(default=None, max_length=50)
	attached_documents: Optional[list[Any]] = Field(default=None, max_length=30)
	identity_document_requisites: Optional[str] = Field(default=None, max_length=1000)


class TransportUpdate(BaseModel):
	vehicle_id: Optional[int] = None
	driver_id: Optional[int] = None


class DealUpdate(BaseModel):
	deal_id: int


class CompanyBrief(BaseModel):
	id: int
	name: str
	slug: str
	type: Optional[str] = None
	model_config = ConfigDict(from_attributes=True)


class ShipmentRequestResponse(BaseModel):
	id: int
	client_company_id: int
	carrier_company_id: int
	status: str
	is_highlighted: bool
	search_filters: dict[str, Any]
	matched_vehicle_ids: list[int]
	created_at: datetime
	updated_at: datetime
	activated_at: Optional[datetime] = None
	expires_at: datetime
	model_config = ConfigDict(from_attributes=True)


class ShipmentResponse(BaseModel):
	id: int
	number: str
	year: int
	client_company_id: int
	carrier_company_id: int
	request_id: int
	deal_id: Optional[int] = None
	cargo_data: dict[str, Any]
	vehicle_id: Optional[int] = None
	driver_id: Optional[int] = None
	transport_snapshot: dict[str, Any]
	created_at: datetime
	updated_at: datetime
	client_company: Optional[CompanyBrief] = None
	carrier_company: Optional[CompanyBrief] = None
	model_config = ConfigDict(from_attributes=True)


class ShipmentListItem(BaseModel):
	"""Лента перевозок без тяжёлых cargo/transport — их грузим отдельными GET."""
	id: int
	number: str
	year: int
	client_company_id: int
	carrier_company_id: int
	request_id: int
	deal_id: Optional[int] = None
	created_at: datetime
	updated_at: datetime
	client_company: Optional[CompanyBrief] = None
	carrier_company: Optional[CompanyBrief] = None
	model_config = ConfigDict(from_attributes=True)


class CargoDetailResponse(BaseModel):
	shipment_id: int
	cargo_data: dict[str, Any]


class TransportDetailResponse(BaseModel):
	shipment_id: int
	vehicle_id: Optional[int] = None
	driver_id: Optional[int] = None
	transport_snapshot: dict[str, Any]
