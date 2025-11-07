from typing import Optional, Tuple

from diskcache import Cache
from fastapi import HTTPException

from ..utils.location_data import get_regions

# Initialize the cache
cache = Cache("./cache")


def get_cached_regions(country_code: str, federal_district: Optional[str] = None) -> Tuple[str, list]:
    """
    Get regions with caching using diskcache. Returns a tuple of (cache_key, regions).
    """
    cache_key = f"regions:{country_code}:{federal_district or ''}"

    if cache_key in cache:
        return cache_key, cache[cache_key]

    try:
        regions = get_regions(country_code, federal_district)
        cache[cache_key] = regions
        return cache_key, regions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_cached_cities(
    country: str, 
    region: Optional[str] = None, 
    federal_district: Optional[str] = None, 
    search: Optional[str] = None, 
    million_cities_only: bool = False, 
    regional_centers_only: bool = False
) -> Tuple[str, list]:
    """
    Get cities with caching using diskcache. Returns a tuple of (cache_key, cities).
    """
    cache_key = f"cities:{country}:{region or ''}:{federal_district or ''}:{search or ''}:{million_cities_only}:{regional_centers_only}"

    if cache_key in cache:
        return cache_key, cache[cache_key]

    try:
        from ..utils.location_data import get_cities
        cities = get_cities(country, region, federal_district, search, million_cities_only, regional_centers_only)
        cache[cache_key] = cities
        return cache_key, cities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
