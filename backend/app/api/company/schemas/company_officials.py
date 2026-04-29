from pydantic import BaseModel


class CompanyOfficialBase(BaseModel):
	position: str
	full_name: str
	is_base: bool = False
	base_document: str | None = None
	base_document_name: str | None = None


class CompanyOfficialCreate(CompanyOfficialBase):
    pass


class CompanyOfficialUpdate(BaseModel):
	position: str | None = None
	full_name: str | None = None
	is_base: bool | None = None
	base_document: str | None = None
	base_document_name: str | None = None


class CompanyOfficialPartialUpdate(BaseModel):
	position: str | None = None
	full_name: str | None = None
	is_base: bool | None = None
	base_document: str | None = None
	base_document_name: str | None = None

class CompanyOfficial(CompanyOfficialBase):
	id: int
	company_id: int
	is_base: bool = False
	base_document: str | None = None
	base_document_name: str | None = None

	class Config:
			from_attributes = True
