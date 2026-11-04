from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CompanyVehicleCreate(BaseModel):
	name: str = Field(..., min_length=1, max_length=200)
	plate_number: Optional[str] = Field(None, max_length=32)
	trailer_plate_number: Optional[str] = Field(None, max_length=32)
	trailer_length_m: Optional[float] = None
	trailer_width_m: Optional[float] = None
	trailer_height_m: Optional[float] = None
	load_date: Optional[date] = None
	body_type: Optional[str] = Field(None, max_length=100)
	loading_methods: list[str] = Field(default_factory=list)
	adr_classes: list[str] = Field(default_factory=list)
	from_locations: list[dict[str, Any]] = Field(default_factory=list)
	to_locations: list[dict[str, Any]] = Field(default_factory=list)
	partial_load: bool = False
	partial_load_weight_kg: Optional[float] = None
	partial_load_volume_m3: Optional[float] = None
	vehicle_type: Optional[str] = Field(None, max_length=100)
	capacity_tons: Optional[float] = None
	volume_m3: Optional[float] = None
	notes: Optional[str] = Field(None, max_length=500)
	is_active: bool = True


class CompanyVehicleUpdate(BaseModel):
	name: Optional[str] = Field(None, min_length=1, max_length=200)
	plate_number: Optional[str] = Field(None, max_length=32)
	trailer_plate_number: Optional[str] = Field(None, max_length=32)
	trailer_length_m: Optional[float] = None
	trailer_width_m: Optional[float] = None
	trailer_height_m: Optional[float] = None
	load_date: Optional[date] = None
	body_type: Optional[str] = Field(None, max_length=100)
	loading_methods: Optional[list[str]] = None
	adr_classes: Optional[list[str]] = None
	from_locations: Optional[list[dict[str, Any]]] = None
	to_locations: Optional[list[dict[str, Any]]] = None
	partial_load: Optional[bool] = None
	partial_load_weight_kg: Optional[float] = None
	partial_load_volume_m3: Optional[float] = None
	vehicle_type: Optional[str] = Field(None, max_length=100)
	capacity_tons: Optional[float] = None
	volume_m3: Optional[float] = None
	notes: Optional[str] = Field(None, max_length=500)
	is_active: Optional[bool] = None


class CompanyVehicleResponse(BaseModel):
	id: int
	company_id: int
	name: str
	plate_number: Optional[str] = None
	trailer_plate_number: Optional[str] = None
	trailer_length_m: Optional[float] = None
	trailer_width_m: Optional[float] = None
	trailer_height_m: Optional[float] = None
	load_date: Optional[date] = None
	body_type: Optional[str] = None
	loading_methods: list[str] = Field(default_factory=list)
	adr_classes: list[str] = Field(default_factory=list)
	from_locations: list[dict[str, Any]] = Field(default_factory=list)
	to_locations: list[dict[str, Any]] = Field(default_factory=list)
	partial_load: bool = False
	partial_load_weight_kg: Optional[float] = None
	partial_load_volume_m3: Optional[float] = None
	vehicle_type: Optional[str] = None
	capacity_tons: Optional[float] = None
	volume_m3: Optional[float] = None
	notes: Optional[str] = None
	is_active: bool
	created_at: datetime
	updated_at: Optional[datetime] = None

	model_config = ConfigDict(from_attributes=True)


class CompanyDriverCreate(BaseModel):
	full_name: str = Field(..., min_length=1, max_length=200)
	phone: Optional[str] = Field(None, max_length=32)
	license_number: Optional[str] = Field(None, max_length=64)
	inn: Optional[str] = Field(None, max_length=16)
	notes: Optional[str] = Field(None, max_length=500)
	is_active: bool = True


class CompanyDriverUpdate(BaseModel):
	full_name: Optional[str] = Field(None, min_length=1, max_length=200)
	phone: Optional[str] = Field(None, max_length=32)
	license_number: Optional[str] = Field(None, max_length=64)
	inn: Optional[str] = Field(None, max_length=16)
	notes: Optional[str] = Field(None, max_length=500)
	is_active: Optional[bool] = None


class CompanyDriverResponse(BaseModel):
	id: int
	company_id: int
	full_name: str
	phone: Optional[str] = None
	license_number: Optional[str] = None
	inn: Optional[str] = None
	notes: Optional[str] = None
	is_active: bool
	created_at: datetime
	updated_at: Optional[datetime] = None

	model_config = ConfigDict(from_attributes=True)
