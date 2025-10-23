from typing import Optional
from datetime import datetime, timedelta
import asyncio

from fastapi import APIRouter, Query, Path, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .routes.locations import location_api
from ..common.schemas.location import LocationResponse
from ..common.utils.caching import get_cached_regions, get_cached_cities
from ..common.utils.location_api import LocationAPIError
from ..common.utils.location_data import (
    get_countries,
    get_federal_districts,
)

router = APIRouter(tags=["locations"])

# Кэш для API локаций (30 минут)
class LocationAPICache:
    def __init__(self):
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_duration = timedelta(minutes=30)
        self._lock = asyncio.Lock()

    def _is_cache_valid(self, cache_key: str) -> bool:
        if cache_key not in self._cache_timestamps:
            return False
        return datetime.now() - self._cache_timestamps[cache_key] < self._cache_duration

    def _get_cache(self, cache_key: str):
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key)
        return None

    def _set_cache(self, cache_key: str, data):
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now()

    async def get_cached_data(self, cache_key: str, fetch_fn):
        async with self._lock:
            cached_data = self._get_cache(cache_key)
            if cached_data:
                return cached_data
            
            data = await fetch_fn()
            self._set_cache(cache_key, data)
            return data

# Глобальный экземпляр кэша
location_cache = LocationAPICache()

# Dependency для получения сессии базы данных
async def get_db():
    from app.db.base import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session


async def unify_list(items: list) -> list:
    return [{"label": item.get("label"), "value": item.get("label")} for item in items]


@router.get("/countries", response_model=LocationResponse)
async def get_countries():
    """Получить список всех стран"""
    try:
        countries = await get_countries()
        return LocationResponse(
            items=countries,
            total=len(countries)
        )
    except LocationAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/federal-districts", response_model=LocationResponse)
async def get_federal_districts(country: str = Query(..., description="Название страны")):
    """Получить список федеральных округов по стране"""
    try:
        districts = await get_federal_districts(country)
        return LocationResponse(
            items=districts,
            total=len(districts)
        )
    except LocationAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regions", response_model=LocationResponse)
async def get_regions(
    country: str = Query(..., description="Название страны"),
    federal_district: Optional[str] = Query(None, description="Название федерального округа")
):
    """Получить список регионов по стране и федеральному округу"""
    try:
        regions = await get_cached_regions(country, federal_district)
        return LocationResponse(
            items=regions,
            total=len(regions)
        )
    except LocationAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cities", response_model=LocationResponse)
async def get_cities(
    country: str = Query(..., description="Название страны"),
    region: Optional[str] = Query(None, description="Название региона"),
    federal_district: Optional[str] = Query(None, description="Название федерального округа"),
    search: Optional[str] = Query(None, description="Поиск по названию города"),
    million_cities_only: bool = Query(False, description="Только города-миллионники"),
    regional_centers_only: bool = Query(False, description="Только региональные центры")
):
    """Получить список городов по стране, региону и федеральному округу"""
    try:
        cities = await get_cached_cities(
            country, region, federal_district, search, 
            million_cities_only, regional_centers_only
        )
        return LocationResponse(
            items=cities,
            total=len(cities)
        )
    except LocationAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Новые endpoints для работы с базой данных (временно отключены)