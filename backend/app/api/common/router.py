from typing import Optional

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

# Dependency для получения сессии базы данных
async def get_db():
    from app.db.base import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session


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
    """Получить список городов из базы данных по стране и региону"""
    try:
        from sqlalchemy import select
        from app.db.base import AsyncSessionLocal
        from app.api.company.models.company import Company
        
        # Логируем полученные параметры
        print(f"DEBUG: Received country='{country}', region='{region}', name='{name}'")
        
        async with AsyncSessionLocal() as session:
            # Получаем города из базы данных
            query = select(Company.city).where(
                Company.is_active == True,
                Company.country == country,
                Company.region == region
            ).distinct()
            
            result = await session.execute(query)
            cities = result.scalars().all()
            
            print(f"DEBUG: Found cities: {cities}")
            
            # Фильтруем по имени города если указано
            if name:
                cities = [city for city in cities if city.lower().startswith(name.lower())]
            
            # Формируем ответ
            city_items = [{"label": city, "value": city} for city in sorted(cities)]
            
            print(f"DEBUG: Returning {len(city_items)} cities")
            
            return LocationResponse(
                items=city_items,
                total=len(city_items)
            )
    except Exception as e:
        print(f"DEBUG: Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


# Новые endpoints для работы с базой данных
@router.get("/v2/countries", response_model=LocationResponse)
async def get_countries_v2(db: AsyncSession = Depends(get_db)):
    """Получить список всех стран из базы данных"""
    try:
        result = await db.execute(text("SELECT code, name FROM countries WHERE is_active = true ORDER BY name"))
        countries = result.fetchall()
        
        items = [{"label": country[1], "value": country[0]} for country in countries]
        
        return LocationResponse(
            items=items,
            total=len(items)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v2/federal-districts", response_model=LocationResponse)
async def get_federal_districts_v2(
    country_code: str = Query(..., description="Код страны"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список федеральных округов по стране"""
    try:
        result = await db.execute(text("""
            SELECT fd.code, fd.name 
            FROM federal_districts fd
            JOIN countries c ON fd.country_id = c.id
            WHERE c.code = :country_code AND fd.is_active = true AND c.is_active = true
            ORDER BY fd.name
        """), {"country_code": country_code})
        
        districts = result.fetchall()
        items = [{"label": district[1], "value": district[0]} for district in districts]
        
        return LocationResponse(
            items=items,
            total=len(items)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v2/regions", response_model=LocationResponse)
async def get_regions_v2(
    country_code: str = Query(..., description="Код страны"),
    federal_district_code: Optional[str] = Query(None, description="Код федерального округа"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список регионов по стране и федеральному округу"""
    try:
        query = """
            SELECT r.code, r.name 
            FROM regions r
            JOIN countries c ON r.country_id = c.id
            WHERE c.code = :country_code AND r.is_active = true AND c.is_active = true
        """
        params = {"country_code": country_code}
        
        if federal_district_code:
            query += " AND EXISTS (SELECT 1 FROM federal_districts fd WHERE fd.id = r.federal_district_id AND fd.code = :fd_code AND fd.is_active = true)"
            params["fd_code"] = federal_district_code
        
        query += " ORDER BY r.name"
        
        result = await db.execute(text(query), params)
        regions = result.fetchall()
        
        items = [{"label": region[1], "value": region[0]} for region in regions]
        
        return LocationResponse(
            items=items,
            total=len(items)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v2/cities", response_model=LocationResponse)
async def get_cities_v2(
    country_code: str = Query(..., description="Код страны"),
    region_code: Optional[str] = Query(None, description="Код региона"),
    federal_district_code: Optional[str] = Query(None, description="Код федерального округа"),
    search: Optional[str] = Query(None, description="Поиск по названию города"),
    million_cities_only: bool = Query(False, description="Только города-миллионники"),
    regional_centers_only: bool = Query(False, description="Только региональные центры"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список городов по стране, региону и федеральному округу"""
    try:
        query = """
            SELECT c.name, c.population, c.is_million_city, c.is_regional_center
            FROM cities c
            JOIN countries co ON c.country_id = co.id
            WHERE co.code = :country_code AND c.is_active = true AND co.is_active = true
        """
        params = {"country_code": country_code}
        
        if region_code:
            query += " AND EXISTS (SELECT 1 FROM regions r WHERE r.id = c.region_id AND r.code = :region_code AND r.is_active = true)"
            params["region_code"] = region_code
        
        if federal_district_code:
            query += " AND EXISTS (SELECT 1 FROM federal_districts fd WHERE fd.id = c.federal_district_id AND fd.code = :fd_code AND fd.is_active = true)"
            params["fd_code"] = federal_district_code
        
        if million_cities_only:
            query += " AND c.is_million_city = true"
        
        if regional_centers_only:
            query += " AND c.is_regional_center = true"
        
        if search:
            query += " AND c.name ILIKE :search"
            params["search"] = f"%{search}%"
        
        query += " ORDER BY c.name"
        
        result = await db.execute(text(query), params)
        cities = result.fetchall()
        
        items = [{"label": city[0], "value": city[0]} for city in cities]
        
        return LocationResponse(
            items=items,
            total=len(items)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
