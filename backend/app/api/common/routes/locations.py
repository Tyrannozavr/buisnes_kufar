from typing import Optional

from fastapi import APIRouter, HTTPException

from app.api.common.schemas.location import (
    LocationResponse,
    CitySearchResponse
)
from app.api.common.utils.location_api import LocationAPI

router = APIRouter(prefix="/locations", tags=["locations"])
location_api = LocationAPI()


@router.get("/countries", response_model=LocationResponse)
async def get_countries():
    """
    Получить список стран.
    """
    try:
        countries = await location_api.get_countries()
        return LocationResponse(
            items=countries,
            total=len(countries)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regions/{country_code}", response_model=LocationResponse)
async def get_regions(country_code: str, federal_district: Optional[str] = Query(None)):
    """
    Получить список регионов для указанной страны.
    
    Args:
        country_code: Код страны (например, 'RU')
        federal_district: Название федерального округа (необязательно)
    """
    try:
        regions = await location_api.get_regions(country_code, federal_district)
        return LocationResponse(
            items=regions,
            total=len(regions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cities/{region_id}", response_model=LocationResponse)
async def get_cities(region_id: int, level: Optional[int] = None):
    """
    Получить список городов для указанного региона.
    """
    try:
        cities = await location_api.get_cities(region_id, level)
        return LocationResponse(
            items=cities,
            total=len(cities)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cities/search/{city_name}", response_model=CitySearchResponse)
async def search_cities(city_name: str):
    """
    Поиск городов по частичному совпадению названия.
    """
    try:
        cities = await location_api.search_cities(city_name)
        return CitySearchResponse(
            items=cities,
            total=len(cities)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/districts/{region_id}", response_model=LocationResponse)
async def get_districts(region_id: int):
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
