from typing import List, Optional
from pydantic import BaseModel


class FilterItem(BaseModel):
    label: str
    value: str


class CompanyFiltersResponse(BaseModel):
    countries: List[FilterItem]
    federal_districts: List[FilterItem]
    regions: List[FilterItem]
    cities: List[FilterItem]


class ProductFilterRequest(BaseModel):
    search: Optional[str] = None
    country: Optional[str] = None
    federal_district: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: Optional[bool] = None
    skip: int = 0
    limit: int = 100


class ServiceFilterRequest(BaseModel):
    search: Optional[str] = None
    country: Optional[str] = None
    federal_district: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: Optional[bool] = None
    skip: int = 0
    limit: int = 100 