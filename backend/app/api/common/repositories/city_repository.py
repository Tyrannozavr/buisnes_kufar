from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.db.base import AsyncSessionLocal
from app.api.common.models.city import City
from app.api.common.models.region import Region
from app.api.common.models.federal_district import FederalDistrict
from app.api.common.models.country import Country


class CityRepository:
    """Репозиторий для работы с городами"""
    
    @staticmethod
    async def find_or_create_city(
        city_name: str,
        region_name: str,
        federal_district_name: Optional[str] = None,
        country_name: str = "Россия"
    ) -> City:
        """Найти или создать город в БД"""
        async with AsyncSessionLocal() as db:
            # 1. Найти страну
            country_query = await db.execute(
                select(Country).where(Country.name == country_name)
            )
            country = country_query.scalar_one_or_none()
            if not country:
                # Создаем страну если не найдена (только для России)
                from app.db.base_class import Base
                country = Country(name=country_name, code="RU" if country_name == "Россия" else "")
                db.add(country)
                await db.commit()
                await db.refresh(country)
            
            # 2. Найти федеральный округ
            federal_district = None
            if federal_district_name:
                fd_query = await db.execute(
                    select(FederalDistrict)
                    .where(FederalDistrict.name == federal_district_name)
                    .where(FederalDistrict.country_id == country.id)
                )
                federal_district = fd_query.scalar_one_or_none()
                if not federal_district:
                    # Создаем федеральный округ если не найден
                    federal_district = FederalDistrict(
                        name=federal_district_name,
                        code=f"FD{hash(federal_district_name) % 1000}",  # Временный код
                        country_id=country.id
                    )
                    db.add(federal_district)
                    await db.commit()
                    await db.refresh(federal_district)
            
            # 3. Найти регион
            region = None
            if region_name:
                region_query = await db.execute(
                    select(Region)
                    .where(Region.name == region_name)
                    .where(Region.country_id == country.id)
                )
                region = region_query.scalar_one_or_none()
                if not region:
                    # Создаем регион если не найден
                    region = Region(
                        name=region_name,
                        code=f"REG{hash(region_name) % 10000}",  # Временный код
                        country_id=country.id,
                        federal_district_id=federal_district.id if federal_district else None
                    )
                    db.add(region)
                    await db.commit()
                    await db.refresh(region)
            
            # 4. Найти город
            city_query = await db.execute(
                select(City)
                .where(City.name == city_name)
                .where(City.region_id == region.id if region else True)
                .where(City.country_id == country.id)
            )
            city = city_query.scalar_one_or_none()
            
            if not city:
                # Создаем город если не найден
                city = City(
                    name=city_name,
                    region_id=region.id if region else None,
                    federal_district_id=federal_district.id if federal_district else None,
                    country_id=country.id
                )
                db.add(city)
                await db.commit()
                await db.refresh(city)
                print(f"✅ Создан новый город: {city_name} в регионе {region_name}")
            
            return city
    
    @staticmethod
    async def find_city_by_name(
        city_name: str,
        region_name: Optional[str] = None
    ) -> Optional[City]:
        """Найти город по названию"""
        async with AsyncSessionLocal() as db:
            query = select(City).where(City.name == city_name)
            
            if region_name:
                # Если указан регион, сначала находим его
                region_query = await db.execute(
                    select(Region).where(Region.name == region_name)
                )
                region = region_query.scalar_one_or_none()
                if region:
                    query = query.where(City.region_id == region.id)
            
            result = await db.execute(query)
            return result.scalar_one_or_none()

