"""
Service для работы с фильтром городов
Агрегирует данные из repository и формирует дерево локаций
"""
from app.api.common.repositories.cities_filter_repository import CitiesFilterRepository


class CitiesFilterService:
    """Service для агрегации данных о городах"""
    
    @staticmethod
    async def _build_tree_from_cities_data(cities_data):
        """Вспомогательный метод для построения дерева из данных городов"""
        if not cities_data:
            return []
        
        # Получаем уникальные ID для регионов, округов и стран
        region_ids = list(set([c['region_id'] for c in cities_data.values()]))
        fd_ids = list(set([c['federal_district_id'] for c in cities_data.values()]))
        country_ids = list(set([c['country_id'] for c in cities_data.values()]))
        
        # Получаем связанные данные
        regions = await CitiesFilterRepository.get_regions_by_ids(region_ids)
        federal_districts = await CitiesFilterRepository.get_federal_districts_by_ids(fd_ids)
        countries = await CitiesFilterRepository.get_countries_by_ids(country_ids)
        
        # Создаем маппинги для быстрого доступа
        regions_dict = {r.id: r for r in regions}
        fds_dict = {fd.id: fd for fd in federal_districts}
        countries_dict = {c.id: c for c in countries}
        
        # Строим дерево
        location_tree = []
        
        for country_id, country in countries_dict.items():
            country_data = {
                "id": country.id,
                "code": country.code,
                "name": country.name,
                "federal_districts": [],
                "products_count": 0
            }
            
            # Находим федеральные округа для этой страны
            for fd_id in fd_ids:
                city_info = next((c for c in cities_data.values() if c['federal_district_id'] == fd_id), None)
                if not city_info or city_info['country_id'] != country_id:
                    continue
                
                fd = fds_dict.get(fd_id)
                if not fd:
                    continue
                    
                fd_data = {
                    "id": fd.id,
                    "name": fd.name,
                    "code": fd.code,
                    "regions": [],
                    "products_count": 0
                }
                
                # Находим регионы для этого округа
                for region_id in region_ids:
                    city_info = next((c for c in cities_data.values() if c['region_id'] == region_id), None)
                    if not city_info or city_info['federal_district_id'] != fd_id:
                        continue
                    
                    region = regions_dict.get(region_id)
                    if not region:
                        continue
                    
                    region_data = {
                        "id": region.id,
                        "name": region.name,
                        "code": region.code,
                        "cities": [],
                        "products_count": 0
                    }
                    
                    # Добавляем города с количеством товаров
                    for city_id, city_info in cities_data.items():
                        if city_info['region_id'] == region_id:
                            region_data["cities"].append({
                                "id": city_info['id'],
                                "name": city_info['name'],
                                "products_count": city_info['products_count']
                            })
                            # Суммируем количество товаров для региона
                            region_data["products_count"] += city_info['products_count']
                    
                    if region_data["cities"]:
                        fd_data["regions"].append(region_data)
                        # Суммируем количество товаров для федерального округа
                        fd_data["products_count"] += region_data["products_count"]
                
                if fd_data["regions"]:
                    country_data["federal_districts"].append(fd_data)
                    # Суммируем количество товаров для страны
                    country_data["products_count"] += fd_data["products_count"]
            
            if country_data["federal_districts"]:
                location_tree.append(country_data)
        
        return location_tree
    
    @staticmethod
    async def build_products_location_tree():
        """Построить дерево локаций с количеством товаров"""
        cities_data = await CitiesFilterRepository.get_cities_with_products_count()
        return await CitiesFilterService._build_tree_from_cities_data(cities_data)
    
    @staticmethod
    async def build_services_location_tree():
        """Построить дерево локаций с количеством услуг"""
        cities_data = await CitiesFilterRepository.get_cities_with_services_count()
        return await CitiesFilterService._build_tree_from_cities_data(cities_data)
    
    @staticmethod
    async def build_companies_location_tree():
        """Построить дерево локаций с количеством компаний"""
        cities_result = await CitiesFilterRepository.get_cities_with_companies_count()
        
        # Если это плоская структура (без иерархии - города не найдены в cities)
        if isinstance(cities_result, dict) and 'cities' in cities_result:
            # Создаем упрощенное дерево без иерархии
            return [{
                "id": 1,
                "code": "RU",
                "name": "Россия",
                "federal_districts": [{
                    "id": 1,
                    "name": "Все города",
                    "code": "ALL",
                    "regions": [{
                        "id": 1,
                        "name": "Все города",
                        "code": "ALL_CITIES",
                        "cities": cities_result['cities'],
                        "products_count": cities_result['total_companies']
                    }],
                    "products_count": cities_result['total_companies']
                }],
                "products_count": cities_result['total_companies']
            }]
        
        # Обычная иерархическая структура
        return await CitiesFilterService._build_tree_from_cities_data(cities_result)
    
    @staticmethod
    async def build_location_tree():
        """Построить дерево локаций с количеством компаний (по умолчанию)"""
        return await CitiesFilterService.build_companies_location_tree()
    
    @staticmethod
    async def get_cities_stats():
        """Получить статистику по городам"""
        from sqlalchemy import select, and_
        from app.db.base import AsyncSessionLocal
        from app.api.common.models.city import City
        from app.api.common.models.federal_district import FederalDistrict
        from app.api.common.models.region import Region
        
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

