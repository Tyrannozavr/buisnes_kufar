from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional, Dict, Tuple
from functools import lru_cache

from ..common.schemas.location import LocationResponse
from ..common.utils.location_api import LocationAPI, LocationAPIError
from ..common.utils.location_data import (
    get_countries,
    get_federal_districts,
    get_cities
)

router = APIRouter(prefix="/locations", tags=["locations"])
location_api = LocationAPI()

async def unify_list(items: list) -> list:
    return [{"label": item.get("label"), "value": item.get("label")} for item in items]

# Cache for regions data
@lru_cache(maxsize=None)
async def get_cached_regions(country_code: str, federal_district: Optional[str] = None) -> Tuple[str, list]:
    """
    Get regions with caching. Returns a tuple of (cache_key, regions) to ensure proper caching.
    The cache key is used to differentiate between different combinations of country and federal district.
    """
    try:
        regions = await location_api.get_regions(country_code)

        return f"{country_code}:{federal_district or ''}", regions
    except LocationAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    Результаты кэшируются навсегда для одинаковых запросов.
    """
    try:
        # Convert country name to code if needed
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

        # Get cached regions
        _, regions = await get_cached_regions(country_code, federal_district)

        # Filter by federal district if provided (only for Russia)
        if federal_district and country_code == "RU":
            regions = [region for region in regions if region.get("okrug") == federal_district]

        regions = [{"label": region.get("label"), "value": region.get("label")} for region in regions]

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
    region: str = Query(..., description="Регион")
):
    """Получить список городов по стране и региону"""
    return {"data": get_cities(country, region)}

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 