from datetime import datetime
from typing import Optional, List

from fastapi import Form
from pydantic import BaseModel, Field, ConfigDict

from app.api.company.schemas.company import CompanyLogoUrlMixin
from app.api.company.models.company import TradeActivity, BusinessType
from app.api.company.schemas.company_officials import CompanyOfficial


class CompanyListItem(CompanyLogoUrlMixin):
    """Схема для элемента списка компаний"""
    id: int
    name: str
    slug: str
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
    created_at: datetime = Field(..., alias="registrationDate")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PaginationInfo(BaseModel):
    """Информация о пагинации"""
    total: int
    page: int
    per_page: int = Field(..., alias="perPage")
    total_pages: int = Field(..., alias="totalPages")


class CompaniesResponse(BaseModel):
    """Ответ с списком компаний и пагинацией"""
    data: List[CompanyListItem]
    pagination: PaginationInfo 