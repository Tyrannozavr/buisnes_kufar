from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.api.company.models.fill_address import FillAddressKind


class CompanyFillAddressCreate(BaseModel):
	kind: FillAddressKind
	address: str = Field(..., min_length=1, max_length=500)
	is_default: bool = False


class CompanyFillAddressUpdate(BaseModel):
	address: Optional[str] = Field(None, min_length=1, max_length=500)
	is_default: Optional[bool] = None


class CompanyFillAddressResponse(BaseModel):
	id: int
	company_id: int
	kind: FillAddressKind
	address: str
	is_default: bool
	created_at: datetime
	updated_at: Optional[datetime] = None

	model_config = ConfigDict(from_attributes=True)
