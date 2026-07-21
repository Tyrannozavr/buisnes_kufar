from datetime import date, datetime
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
	loading_time: Optional[str] = None
	loading_address: Optional[str] = None
	unloading_date: Optional[date] = None
	unloading_time: Optional[str] = None
	unloading_address: Optional[str] = None
	route: Optional[str] = None
	contact_loading: Optional[dict[str, Any]] = None
	contact_unloading: Optional[dict[str, Any]] = None
	cargo_name: Optional[str] = None
	transport_conditions: Optional[str] = None
	net_weight: Optional[float] = None
	gross_weight: Optional[float] = None
	places_count: Optional[int] = None
	volume: Optional[float] = None
	marking: Optional[str] = None
	packaging_type: Optional[str] = None
	packaging: Optional[str] = None
	seal: Optional[str] = None
	rate: Optional[float] = None
	payment_terms: Optional[str] = None
	declared_value: Optional[float] = None
	dangerous_goods: Optional[list[str]] = None
	attached_documents: Optional[list[Any]] = None
	identity_document_requisites: Optional[str] = None


class TransportUpdate(BaseModel):
	vehicle_id: Optional[int] = None
	driver_id: Optional[int] = None


class DealUpdate(BaseModel):
	deal_id: int


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
	model_config = ConfigDict(from_attributes=True)
