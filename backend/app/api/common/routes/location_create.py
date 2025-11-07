from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models import User
from app.api.common.models.country import Country
from app.api.common.models.federal_district import FederalDistrict
from app.api.common.models.region import Region
from app.api.common.models.city import City
from app.api.common.schemas.location import (
    CountryCreate,
    FederalDistrictCreate,
    RegionCreate,
    CityCreate,
    LocationCreateResponse
)
from app.db.base import AsyncSessionLocal
from app_logging.logger import logger

router = APIRouter(tags=["locations"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/countries", response_model=LocationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_country(
    country_data: CountryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новую страну (только для авторизованных пользователей)"""
    try:
        # Проверяем, существует ли страна с таким кодом
        result = await db.execute(
            select(Country).where(Country.code == country_data.code.upper())
        )
        existing_country = result.scalar_one_or_none()
        
        if existing_country:
            logger.info(f"Попытка создания существующей страны: код={country_data.code}, пользователь_id={current_user.id}")
            return LocationCreateResponse(
                success=False,
                message=f"Страна с кодом '{country_data.code}' уже существует",
                data={"id": existing_country.id, "code": existing_country.code, "name": existing_country.name}
            )
        
        # Создаем новую страну
        new_country = Country(
            code=country_data.code.upper(),
            name=country_data.name,
            is_active=True
        )
        
        db.add(new_country)
        await db.commit()
        await db.refresh(new_country)
        
        logger.info(f"Создана новая страна: id={new_country.id}, код={new_country.code}, название='{new_country.name}', пользователь_id={current_user.id}")
        
        return LocationCreateResponse(
            success=True,
            message="Страна успешно создана",
            data={"id": new_country.id, "code": new_country.code, "name": new_country.name}
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при создании страны: {str(e)}, пользователь_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/federal-districts", response_model=LocationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_federal_district(
    district_data: FederalDistrictCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый федеральный округ (только для авторизованных пользователей)"""
    try:
        # Находим страну
        result = await db.execute(
            select(Country).where(Country.code == district_data.country_code.upper())
        )
        country = result.scalar_one_or_none()
        
        if not country:
            logger.warning(f"Попытка создания федерального округа для несуществующей страны: код={district_data.country_code}, пользователь_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Страна с кодом '{district_data.country_code}' не найдена"
            )
        
        # Проверяем, существует ли федеральный округ с таким кодом
        result = await db.execute(
            select(FederalDistrict).where(
                FederalDistrict.country_id == country.id,
                FederalDistrict.code == district_data.code
            )
        )
        existing_district = result.scalar_one_or_none()
        
        if existing_district:
            logger.info(f"Попытка создания существующего федерального округа: код={district_data.code}, пользователь_id={current_user.id}")
            return LocationCreateResponse(
                success=False,
                message=f"Федеральный округ с кодом '{district_data.code}' уже существует",
                data={"id": existing_district.id, "code": existing_district.code, "name": existing_district.name}
            )
        
        # Создаем новый федеральный округ
        new_district = FederalDistrict(
            country_id=country.id,
            name=district_data.name,
            code=district_data.code,
            is_active=True
        )
        
        db.add(new_district)
        await db.commit()
        await db.refresh(new_district)
        
        logger.info(f"Создан новый федеральный округ: id={new_district.id}, код={new_district.code}, название='{new_district.name}', страна={district_data.country_code}, пользователь_id={current_user.id}")
        
        return LocationCreateResponse(
            success=True,
            message="Федеральный округ успешно создан",
            data={"id": new_district.id, "code": new_district.code, "name": new_district.name}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при создании федерального округа: {str(e)}, пользователь_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/regions", response_model=LocationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_region(
    region_data: RegionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый регион (только для авторизованных пользователей)"""
    try:
        # Находим страну
        result = await db.execute(
            select(Country).where(Country.code == region_data.country_code.upper())
        )
        country = result.scalar_one_or_none()
        
        if not country:
            logger.warning(f"Попытка создания региона для несуществующей страны: код={region_data.country_code}, пользователь_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Страна с кодом '{region_data.country_code}' не найдена"
            )
        
        # Находим федеральный округ, если указан
        federal_district = None
        if region_data.federal_district_code:
            result = await db.execute(
                select(FederalDistrict).where(
                    FederalDistrict.country_id == country.id,
                    FederalDistrict.code == region_data.federal_district_code
                )
            )
            federal_district = result.scalar_one_or_none()
            
            if not federal_district:
                logger.warning(f"Указан несуществующий федеральный округ: код={region_data.federal_district_code}, пользователь_id={current_user.id}")
                # Создаем регион без федерального округа (он опциональный)
        
        # Проверяем, существует ли регион с таким кодом ИЛИ именем
        query = select(Region).where(
            Region.country_id == country.id
        ).where(
            (Region.code == region_data.code) | (Region.name.ilike(region_data.name))
        )
        result = await db.execute(query)
        existing_region = result.scalar_one_or_none()
        
        if existing_region:
            logger.info(f"Попытка создания существующего региона: код={region_data.code}, название={region_data.name}, пользователь_id={current_user.id}")
            return LocationCreateResponse(
                success=False,
                message=f"Регион '{region_data.name}' уже существует",
                data={"id": existing_region.id, "code": existing_region.code, "name": existing_region.name}
            )
        
        # Создаем новый регион
        new_region = Region(
            country_id=country.id,
            federal_district_id=federal_district.id if federal_district else None,
            name=region_data.name,
            code=region_data.code,
            is_active=True
        )
        
        db.add(new_region)
        await db.commit()
        await db.refresh(new_region)
        
        federal_district_info = f" федеральный_округ={region_data.federal_district_code}" if federal_district else ""
        logger.info(f"Создан новый регион: id={new_region.id}, код={new_region.code}, название='{new_region.name}', страна={region_data.country_code}{federal_district_info}, пользователь_id={current_user.id}")
        
        return LocationCreateResponse(
            success=True,
            message="Регион успешно создан",
            data={"id": new_region.id, "code": new_region.code, "name": new_region.name}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при создании региона: {str(e)}, пользователь_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/cities", response_model=LocationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_city(
    city_data: CityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый город (только для авторизованных пользователей)"""
    try:
        # Находим страну
        result = await db.execute(
            select(Country).where(Country.code == city_data.country_code.upper())
        )
        country = result.scalar_one_or_none()
        
        if not country:
            logger.warning(f"Попытка создания города для несуществующей страны: код={city_data.country_code}, пользователь_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Страна с кодом '{city_data.country_code}' не найдена"
            )
        
        # Находим регион
        result = await db.execute(
            select(Region).where(
                Region.country_id == country.id,
                Region.name == city_data.region_name
            )
        )
        region = result.scalar_one_or_none()
        
        if not region:
            logger.warning(f"Попытка создания города для несуществующего региона: название='{city_data.region_name}', страна={city_data.country_code}, пользователь_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Регион '{city_data.region_name}' не найден для страны '{city_data.country_code}'"
            )
        
        # Находим федеральный округ, если указан
        federal_district = None
        if city_data.federal_district_code:
            result = await db.execute(
                select(FederalDistrict).where(
                    FederalDistrict.country_id == country.id,
                    FederalDistrict.code == city_data.federal_district_code
                )
            )
            federal_district = result.scalar_one_or_none()
            
            if not federal_district:
                logger.warning(f"Указан несуществующий федеральный округ: код={city_data.federal_district_code}, пользователь_id={current_user.id}")
                # Создаем город без федерального округа (он опциональный)
        
        # Проверяем, существует ли город в этом регионе (case-insensitive)
        query = select(City).where(
            City.country_id == country.id,
            City.region_id == region.id,
            City.name.ilike(city_data.name)
        )
        result = await db.execute(query)
        existing_city = result.scalar_one_or_none()
        
        if existing_city:
            logger.info(f"Попытка создания существующего города: название='{city_data.name}', регион='{city_data.region_name}', пользователь_id={current_user.id}")
            return LocationCreateResponse(
                success=False,
                message=f"Город '{city_data.name}' уже существует в регионе '{city_data.region_name}'",
                data={"id": existing_city.id, "name": existing_city.name}
            )
        
        # Создаем новый город
        new_city = City(
            country_id=country.id,
            region_id=region.id,
            federal_district_id=federal_district.id if federal_district else None,
            name=city_data.name,
            population=city_data.population,
            is_million_city=city_data.is_million_city,
            is_regional_center=city_data.is_regional_center,
            is_active=True
        )
        
        db.add(new_city)
        await db.commit()
        await db.refresh(new_city)
        
        federal_district_info = f" федеральный_округ={city_data.federal_district_code}" if federal_district else ""
        logger.info(f"Создан новый город: id={new_city.id}, название='{new_city.name}', регион='{city_data.region_name}', страна={city_data.country_code}{federal_district_info}, население={city_data.population}, пользователь_id={current_user.id}")
        
        return LocationCreateResponse(
            success=True,
            message="Город успешно создан",
            data={
                "id": new_city.id,
                "name": new_city.name,
                "region": city_data.region_name,
                "country": city_data.country_code
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при создании города: {str(e)}, пользователь_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
