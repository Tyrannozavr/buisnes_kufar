from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from fastapi import Query as FastAPIQuery
import logging

from app.db.base import AsyncSessionLocal
from app.api.common.models.country import Country
from app.api.common.models.federal_district import FederalDistrict
from app.api.common.models.region import Region
from app.api.common.models.city import City
from app.api.common.schemas.location import LocationItem, LocationResponse

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/countries", response_model=LocationResponse)
async def get_countries(db = Depends(get_db)):
    """Получить список всех стран"""
    try:
        result = await db.execute(
            select(Country).where(Country.is_active == True).order_by(Country.name)
        )
        countries = result.scalars().all()
        
        items = [{"label": country.name, "value": country.code} for country in countries]
        
        return LocationResponse(
            items=items,
            total=len(items)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/federal-districts", response_model=LocationResponse)
async def get_federal_districts(
    country_code: str = Query(..., description="Код страны"),
    db = Depends(get_db)
):
    """Получить список федеральных округов по стране"""
    try:
        # Сначала получаем страну
        country_result = await db.execute(
            select(Country).where(Country.code == country_code, Country.is_active == True)
        )
        country = country_result.scalar_one_or_none()
        
        if not country:
            raise HTTPException(status_code=404, detail="Страна не найдена")
        
        # Получаем федеральные округа
        result = await db.execute(
            select(FederalDistrict)
            .where(FederalDistrict.country_id == country.id, FederalDistrict.is_active == True)
            .order_by(FederalDistrict.name)
        )
        districts = result.scalars().all()
        
        items = [{"label": district.name, "value": district.code} for district in districts]
        
        return LocationResponse(
            items=items,
            total=len(items)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regions", response_model=LocationResponse)
async def get_regions(
    country_code: str = Query(..., description="Код страны"),
    federal_district_code: Optional[str] = Query(None, description="Код федерального округа"),
    db = Depends(get_db)
):
    """Получить список регионов по стране и федеральному округу"""
    try:
        # Сначала получаем страну
        country_result = await db.execute(
            select(Country).where(Country.code == country_code, Country.is_active == True)
        )
        country = country_result.scalar_one_or_none()
        
        if not country:
            raise HTTPException(status_code=404, detail="Страна не найдена")
        
        # Строим запрос
        query = select(Region).where(Region.country_id == country.id, Region.is_active == True)
        
        # Если указан федеральный округ, фильтруем по нему
        if federal_district_code:
            fd_result = await db.execute(
                select(FederalDistrict)
                .where(FederalDistrict.code == federal_district_code, FederalDistrict.is_active == True)
            )
            federal_district = fd_result.scalar_one_or_none()
            
            if federal_district:
                query = query.where(Region.federal_district_id == federal_district.id)
        
        query = query.order_by(Region.name)
        result = await db.execute(query)
        regions = result.scalars().all()
        
        items = [{"label": region.name, "value": region.code} for region in regions]
        
        return LocationResponse(
            items=items,
            total=len(items)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cities", response_model=LocationResponse)
async def get_cities(
    country_code: str = Query(..., description="Код страны"),
    region_code: Optional[str] = Query(default=None, description="Код региона"),
    federal_district_code: Optional[str] = Query(default=None, description="Код федерального округа"),
    search: Optional[str] = Query(default=None, description="Поиск по названию города"),
    million_cities_only: bool = Query(False, description="Только города-миллионники"),
    regional_centers_only: bool = Query(False, description="Только региональные центры"),
    db = Depends(get_db)
):
    """Получить список городов по стране, региону и федеральному округу"""
    print(f"🔍 Запрос городов: country_code={country_code}, region_code={region_code}, federal_district_code={federal_district_code}, search={search}")
    try:
        # Сначала получаем страну (сначала по коду, потом по названию)
        country_result = await db.execute(
            select(Country).where(Country.code == country_code, Country.is_active == True)
        )
        country = country_result.scalar_one_or_none()
        
        # Если не нашли по коду, пробуем найти по названию (для обратной совместимости)
        if not country:
            country_result = await db.execute(
                select(Country).where(Country.name == country_code, Country.is_active == True)
            )
            country = country_result.scalar_one_or_none()
        
        if not country:
            raise HTTPException(status_code=404, detail="Страна не найдена")
        
        logger.info(f"🔍 DEBUG: Найдена страна {country.name} с ID {country.id}")
        
        # Строим запрос
        query = select(City).where(City.country_id == country.id, City.is_active == True)
        
        # Если указан регион, фильтруем по нему
        if region_code:
            # Сначала пробуем найти по коду
            region_result = await db.execute(
                select(Region)
                .where(Region.code == region_code, Region.is_active == True)
            )
            region = region_result.scalar_one_or_none()
            
            # Если не нашли по коду, пробуем найти по названию (для обратной совместимости)
            if not region:
                region_result = await db.execute(
                    select(Region)
                    .where(Region.name == region_code, Region.is_active == True)
                )
                region = region_result.scalar_one_or_none()
            
            if region:
                query = query.where(City.region_id == region.id)
                logger.info(f"🔍 DEBUG: Найден регион {region.name} с ID {region.id}")
            else:
                logger.warning(f"❌ DEBUG: Регион с кодом/названием {region_code} не найден")
        
        # Если указан федеральный округ, фильтруем по нему
        if federal_district_code and isinstance(federal_district_code, str):
            # Сначала пробуем найти по коду
            fd_result = await db.execute(
                select(FederalDistrict)
                .where(FederalDistrict.code == federal_district_code, FederalDistrict.is_active == True)
            )
            federal_district = fd_result.scalar_one_or_none()
            
            # Если не нашли по коду, пробуем найти по названию (для обратной совместимости)
            if not federal_district:
                fd_result = await db.execute(
                    select(FederalDistrict)
                    .where(FederalDistrict.name == federal_district_code, FederalDistrict.is_active == True)
                )
                federal_district = fd_result.scalar_one_or_none()
            
            if federal_district:
                query = query.where(City.federal_district_id == federal_district.id)
                logger.info(f"🔍 DEBUG: Найден федеральный округ {federal_district.name} с ID {federal_district.id}")
            else:
                logger.warning(f"❌ DEBUG: Федеральный округ с кодом/названием {federal_district_code} не найден")
        
        # Фильтры по типу города
        if million_cities_only:
            query = query.where(City.is_million_city == True)
        
        if regional_centers_only:
            query = query.where(City.is_regional_center == True)
        
        # Поиск по названию
        if search:
            query = query.where(City.name.ilike(f"%{search}%"))
        
        query = query.order_by(City.name)
        result = await db.execute(query)
        cities = result.scalars().all()
        
        logger.info(f"🔍 DEBUG: Найдено {len(cities)} городов")
        if cities:
            logger.info(f"🔍 DEBUG: Первые 3 города: {[city.name for city in cities[:3]]}")
        
        items = [{"label": city.name, "value": city.name} for city in cities]
        
        return LocationResponse(
            items=items,
            total=len(items)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/location-tree", response_model=dict)
async def get_location_tree(db = Depends(get_db)):
    """Получить полное дерево локаций для фронтенда"""
    try:
        # Получаем все страны с их федеральными округами, регионами и городами
        countries_result = await db.execute(
            select(Country).where(Country.is_active == True).order_by(Country.name)
        )
        countries = countries_result.scalars().all()
        
        location_tree = []
        
        for country in countries:
            country_data = {
                "id": country.id,
                "code": country.code,
                "name": country.name,
                "federal_districts": []
            }
            
            # Получаем федеральные округа для страны
            fd_result = await db.execute(
                select(FederalDistrict)
                .where(FederalDistrict.country_id == country.id, FederalDistrict.is_active == True)
                .order_by(FederalDistrict.name)
            )
            federal_districts = fd_result.scalars().all()
            
            for fd in federal_districts:
                fd_data = {
                    "id": fd.id,
                    "name": fd.name,
                    "code": fd.code,
                    "regions": []
                }
                
                # Получаем регионы для федерального округа
                regions_result = await db.execute(
                    select(Region)
                    .where(Region.federal_district_id == fd.id, Region.is_active == True)
                    .order_by(Region.name)
                )
                regions = regions_result.scalars().all()
                
                for region in regions:
                    region_data = {
                        "id": region.id,
                        "name": region.name,
                        "code": region.code,
                        "cities": []
                    }
                    
                    # Получаем города для региона
                    cities_result = await db.execute(
                        select(City)
                        .where(City.region_id == region.id, City.is_active == True)
                        .order_by(City.name)
                    )
                    cities = cities_result.scalars().all()
                    
                    for city in cities:
                        city_data = {
                            "id": city.id,
                            "name": city.name,
                            "population": city.population,
                            "is_million_city": city.is_million_city,
                            "is_regional_center": city.is_regional_center
                        }
                        region_data["cities"].append(city_data)
                    
                    fd_data["regions"].append(region_data)
                
                country_data["federal_districts"].append(fd_data)
            
            location_tree.append(country_data)
        
        return {"countries": location_tree}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
