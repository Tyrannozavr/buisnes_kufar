from pydantic import BaseModel


class CompanyOfficialBase(BaseModel):
    position: str
    full_name: str


class CompanyOfficialCreate(CompanyOfficialBase):
    pass


class CompanyOfficialUpdate(BaseModel):
    pass


class CompanyOfficialPartialUpdate(BaseModel):
    position: str | None = None
    full_name: str | None = None


class CompanyOfficial(CompanyOfficialBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True
