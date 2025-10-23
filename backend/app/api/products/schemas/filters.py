from typing import List

from pydantic import BaseModel


class FilterItem(BaseModel):
    label: str
    value: str
    count: int = 0  # Количество товаров для этого фильтра


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


class CityProductCount(BaseModel):
    city_name: str
    region_name: str
    product_count: int


class CitiesProductCountResponse(BaseModel):
    cities: List[CityProductCount]
