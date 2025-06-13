from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, EmailStr, HttpUrl, constr, conint
from app.api.company.models.company import TradeActivity, BusinessType

class CompanyOfficialBase(BaseModel):
    position: str
    full_name: str

class CompanyOfficialCreate(CompanyOfficialBase):
    pass

class CompanyOfficialUpdate(CompanyOfficialBase):
    pass

class CompanyOfficial(CompanyOfficialBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True

class CompanyBase(BaseModel):
    name: str
    type: str
    trade_activity: TradeActivity
    business_type: BusinessType
    activity_type: str
    description: Optional[str] = None
    
    # Location
    country: str
    federal_district: str
    region: str
    city: str
    
    # Legal information
    full_name: str
    inn: constr(min_length=10, max_length=12)
    ogrn: constr(min_length=13, max_length=15)
    kpp: constr(min_length=9, max_length=9)
    registration_date: datetime
    legal_address: str
    production_address: Optional[str] = None
    
    # Contact information
    phone: constr(min_length=10, max_length=20)
    email: EmailStr
    website: Optional[HttpUrl] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    logo: Optional[str] = None
    type: Optional[str] = None
    trade_activity: Optional[TradeActivity] = None
    business_type: Optional[BusinessType] = None
    activity_type: Optional[str] = None
    description: Optional[str] = None
    
    # Location
    country: Optional[str] = None
    federal_district: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    
    # Legal information
    full_name: Optional[str] = None
    inn: Optional[constr(min_length=10, max_length=12)] = None
    ogrn: Optional[Union[
        str, int
        # constr(min_length=13, max_length=15),
        # conint(ge=10**12, lt=10**15)
    ]] = None
    kpp: Optional[Union[
        str,
        int,
        # constr(min_length=9, max_length=9),
        # conint(ge=10**8, lt=10**9)
    ]] = None
    registration_date: Optional[datetime] = None
    legal_address: Optional[str] = None
    production_address: Optional[str] = None
    
    # Contact information
    phone: Optional[constr(min_length=10, max_length=20)] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    
    # Officials
    officials: Optional[List[CompanyOfficialUpdate]] = None

class Company(CompanyBase):
    id: int
    slug: str
    logo: Optional[str] = None
    total_views: int
    monthly_views: int
    total_purchases: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    officials: List[CompanyOfficial]

    class Config:
        from_attributes = True

class CompanyResponse(BaseModel):
    id: int
    name: str
    slug: str
    logo: Optional[str] = None
    type: str
    trade_activity: TradeActivity
    business_type: BusinessType
    activity_type: str
    description: Optional[str] = None
    country: str
    federal_district: str
    region: str
    city: str
    full_name: str
    inn: str
    ogrn: str
    kpp: str
    registration_date: datetime
    legal_address: str
    production_address: Optional[str] = None
    phone: str
    email: str
    website: Optional[str] = None
    officials: List[CompanyOfficial]
    total_views: int
    monthly_views: int
    total_purchases: int
    created_at: datetime
    updated_at: datetime

class CompanyProfileResponse(BaseModel):
    """Response model that combines user and company data for profile display"""
    id: Optional[int] = None
    name: Optional[str] = None
    logo: Optional[str] = None
    email: str
    inn: str
    position: Optional[str] = None
    is_company_created: bool = False

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": None,
                "name": None,
                "logo": None,
                "email": "user@example.com",
                "inn": "1234567890",
                "position": "Manager",
                "is_company_created": False
            }
        }

    @classmethod
    def create_default(cls, user: "User") -> "CompanyProfileResponse":
        """Create a default response with user data when company doesn't exist"""
        return cls(
            id=None,
            name=None,
            logo=None,
            email=user.email,
            inn=user.inn,
            position=user.position,
            is_company_created=False
        )

    @classmethod
    def create_with_company(cls, company: "Company", user: "User") -> "CompanyProfileResponse":
        """Create a response with both user and company data"""
        return cls(
            id=company.id,
            name=company.name,
            logo=company.logo,
            email=user.email,
            inn=user.inn,
            position=user.position,
            is_company_created=True
        )