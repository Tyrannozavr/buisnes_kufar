from fastapi import APIRouter, Query
from typing import Optional

from ..common.schemas.location import LocationResponse
from ..common.utils.location_data import (
    get_countries,
    get_federal_districts,
    get_regions,
    get_cities
)

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("/countries", response_model=LocationResponse)
async def get_countries_list():
    """Получить список стран"""
    return {"data": get_countries()}

@router.get("/federal-districts", response_model=LocationResponse)
async def get_federal_districts_list():
    """Получить список федеральных округов"""
    return {"data": get_federal_districts()}

@router.get("/regions", response_model=LocationResponse)
async def get_regions_list(
    country: str = Query(..., description="Страна"),
    federal_district: Optional[str] = Query(None, description="Федеральный округ")
):
    """Получить список регионов по стране и федеральному округу"""
    return {"data": get_regions(country, federal_district)}

@router.get("/cities", response_model=LocationResponse)
async def get_cities_list(
    country: str = Query(..., description="Страна"),
    region: str = Query(..., description="Регион")
):
    """Получить список городов по стране и региону"""
    return {"data": get_cities(country, region)} 