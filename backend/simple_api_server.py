#!/usr/bin/env python3
"""
Простой HTTP сервер для тестирования API фильтра городов
"""
import asyncio
import json
from aiohttp import web
import aiohttp_cors

from app.db.base import AsyncSessionLocal
from app.api.common.models.country import Country
from app.api.common.models.federal_district import FederalDistrict
from app.api.common.models.region import Region
from app.api.common.models.city import City
from sqlalchemy import select, and_


async def get_cities_stats():
    """Получить статистику по городам"""
    async with AsyncSessionLocal() as db:
        # Общее количество городов
        total_cities_result = await db.execute(
            select(City).where(City.is_active == True)
        )
        total_cities = len(total_cities_result.scalars().all())
        
        # Города-миллионники
        million_cities_result = await db.execute(
            select(City).where(and_(City.is_active == True, City.is_million_city == True))
        )
        million_cities = len(million_cities_result.scalars().all())
        
        # Региональные центры
        regional_centers_result = await db.execute(
            select(City).where(and_(City.is_active == True, City.is_regional_center == True))
        )
        regional_centers = len(regional_centers_result.scalars().all())
        
        # Количество федеральных округов
        fd_result = await db.execute(
            select(FederalDistrict).where(FederalDistrict.is_active == True)
        )
        total_federal_districts = len(fd_result.scalars().all())
        
        # Количество регионов
        regions_result = await db.execute(
            select(Region).where(Region.is_active == True)
        )
        total_regions = len(regions_result.scalars().all())
        
        return {
            "total_cities": total_cities,
            "million_cities": million_cities,
            "regional_centers": regional_centers,
            "total_federal_districts": total_federal_districts,
            "total_regions": total_regions
        }


async def get_cities_filter_tree():
    """Получить полное дерево локаций для фильтра городов"""
    async with AsyncSessionLocal() as db:
        # Получаем все страны
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
        
        return {
            "countries": location_tree,
            "total_countries": len(location_tree),
            "total_federal_districts": sum(len(country["federal_districts"]) for country in location_tree),
            "total_regions": sum(
                len(fd["regions"]) 
                for country in location_tree 
                for fd in country["federal_districts"]
            ),
            "total_cities": sum(
                len(region["cities"])
                for country in location_tree
                for fd in country["federal_districts"]
                for region in fd["regions"]
            )
        }


async def cities_stats_handler(request):
    """Обработчик для статистики городов"""
    try:
        result = await get_cities_stats()
        return web.json_response(result)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def cities_filter_handler(request):
    """Обработчик для дерева городов"""
    try:
        result = await get_cities_filter_tree()
        return web.json_response(result)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def create_app():
    """Создать приложение"""
    app = web.Application()
    
    # Настройка CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Добавляем маршруты
    app.router.add_get('/api/v1/cities-filter/cities-stats', cities_stats_handler)
    app.router.add_get('/api/v1/cities-filter/cities-filter', cities_filter_handler)
    
    # Настраиваем CORS для всех маршрутов
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app


if __name__ == '__main__':
    app = asyncio.run(create_app())
    web.run_app(app, host='0.0.0.0', port=8001)