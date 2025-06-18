from typing import Optional, Tuple

from diskcache import Cache
from fastapi import HTTPException

from ..utils.location_api import LocationAPI, LocationAPIError

# Initialize the cache
cache = Cache("./cache")
location_api = LocationAPI()

async def get_cached_regions(country_code: str, federal_district: Optional[str] = None) -> Tuple[str, list]:
    """
    Get regions with caching using diskcache. Returns a tuple of (cache_key, regions).
    """
    cache_key = f"regions:{country_code}:{federal_district or ''}"
    
    if cache_key in cache:
        return cache_key, cache[cache_key]
    
    try:
        regions = await location_api.get_regions(country_code)
        cache[cache_key] = regions
        return cache_key, regions
    except LocationAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_cached_cities(country_code: str, region: str) -> Tuple[str, list]:
    """
    Get cities with caching using diskcache. Returns a tuple of (cache_key, cities).
    """
    cache_key = f"cities:{country_code}:{region}"
    
    if cache_key in cache:
        return cache_key, cache[cache_key]
    
    try:
        _, regions = await get_cached_regions(country_code)
        region_id = next((region_item["value"] for region_item in regions if region_item["label"] == region), None)
        
        if region_id is None:
            raise HTTPException(status_code=404, detail="Region not found")
        
        cities = await location_api.get_cities(region_id=region_id)
        cache[cache_key] = cities
        return cache_key, cities
    except LocationAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
