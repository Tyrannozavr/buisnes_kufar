from typing import List
from pydantic import BaseModel


class FilterItem(BaseModel):
    label: str
    value: str


class ProductFiltersResponse(BaseModel):
    countries: List[FilterItem]
    federal_districts: List[FilterItem]
    regions: List[FilterItem]
    cities: List[FilterItem]


class ServiceFiltersResponse(BaseModel):
    countries: List[FilterItem]
    federal_districts: List[FilterItem]
    regions: List[FilterItem]
    cities: List[FilterItem] 