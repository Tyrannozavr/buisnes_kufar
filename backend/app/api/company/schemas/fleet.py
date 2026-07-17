from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CompanyVehicleCreate(BaseModel):
	name: str = Field(..., min_length=1, max_length=200)
	plate_number: Optional[str] = Field(None, max_length=32)
	vehicle_type: Optional[str] = Field(None, max_length=100)
	capacity_tons: Optional[float] = None
	volume_m3: Optional[float] = None
	notes: Optional[str] = Field(None, max_length=500)
	is_active: bool = True


class CompanyVehicleUpdate(BaseModel):
	name: Optional[str] = Field(None, min_length=1, max_length=200)
	plate_number: Optional[str] = Field(None, max_length=32)
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
	notes: Optional[str] = Field(None, max_length=500)
	is_active: bool = True


class CompanyDriverUpdate(BaseModel):
	full_name: Optional[str] = Field(None, min_length=1, max_length=200)
	phone: Optional[str] = Field(None, max_length=32)
	license_number: Optional[str] = Field(None, max_length=64)
	notes: Optional[str] = Field(None, max_length=500)
	is_active: Optional[bool] = None


class CompanyDriverResponse(BaseModel):
	id: int
	company_id: int
	full_name: str
	phone: Optional[str] = None
	license_number: Optional[str] = None
	notes: Optional[str] = None
	is_active: bool
	created_at: datetime
	updated_at: Optional[datetime] = None

	model_config = ConfigDict(from_attributes=True)
