from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional

from .routes.locations import location_api
from ..common.schemas.location import LocationResponse
from ..common.utils.location_api import LocationAPIError
from ..common.utils.location_data import (
    get_countries,
    get_federal_districts,
)
from ..common.utils.caching import get_cached_regions, get_cached_cities

router = APIRouter(prefix="/locations", tags=["locations"])

async def unify_list(items: list) -> list:
    return [{"label": item.get("label"), "value": item.get("label")} for item in items]

@router.get("/countries", response_model=LocationResponse)
async def get_countries_list():
    """Получить список стран"""
    countries = get_countries()
    return {
        "items": countries,
        "total": len(countries)
    }

@router.get("/federal-districts", response_model=LocationResponse)
async def get_federal_districts_list():
    """Получить список федеральных округов"""
    federal_districts = await unify_list(get_federal_districts())
    return {
        "items": federal_districts,
        "total": len(federal_districts)
    }

@router.get("/regions/{country}", response_model=LocationResponse)
async def get_regions_list(
    country: str = Path(..., description="Страна"),
    federal_district: Optional[str] = Query(None, description="Федеральный округ")
):
    """
    Получить список регионов по стране и федеральному округу.
    Результаты кэшируются для одинаковых запросов.
    """
    try:
        country_code = country.upper() if len(country) == 2 else {
            "Россия": "RU",
            "Беларусь": "BY",
            "Казахстан": "KZ",
            "Украина": "UA",
            "Армения": "AM",
            "Азербайджан": "AZ",
            "Киргизия": "KG",
            "Молдова": "MD",
            "Таджикистан": "TJ",
            "Узбекистан": "UZ"
        }.get(country, country)

        _, regions = await get_cached_regions(country_code, federal_district)

        if federal_district and country_code == "RU":
            regions = [region for region in regions if region.get("okrug") == federal_district]

        regions = await unify_list(regions)
        return LocationResponse(
            items=regions,
            total=len(regions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cities", response_model=LocationResponse)
async def get_cities_list(
    country: str = Query(..., description="Страна"),
    region: str = Query(..., description="Регион"),
    name: str = Query(None, description="Название города")
):
    """Получить список городов по стране и региону"""
    country = "Беларусь"
    region = "Витебская область"
    if name is None:
        return {
            "items": [],
            "total": 0
        }
    _, cities = await get_cached_cities(country_code=country, region=region)
    cities = [city for city in cities if city.get("label").lower().startswith(name.lower())]
    cities = await unify_list(cities)
    return {
        "items": cities,
        "total": len(cities)
    }

@router.get("/districts/{region_id}", response_model=LocationResponse)
async def get_districts_list(
    region_id: int = Path(..., description="ID региона")
):
    """
    Получить список районов для указанного региона.
    """
    try:
        districts = await location_api.get_districts(region_id)
        return LocationResponse(
            items=districts,
            total=len(districts)
        )
    except LocationAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))