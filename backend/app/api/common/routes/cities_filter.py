from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.api.common.services.cities_filter_service import CitiesFilterService

router = APIRouter()

# Простой in-memory кэш
_cache_data = None
_cache_timestamp = None
CACHE_TTL = 60  # 60 секунд


# Кэши для разных типов
_cache_products = None
_cache_services = None
_cache_companies = None
_timestamps = {}


async def _get_tree_response(location_tree):
    """Формирует стандартный ответ с деревом"""
    total_cities = sum(
        len(region["cities"])
        for country in location_tree
        for fd in country["federal_districts"]
        for region in fd["regions"]
    )
    
    return {
        "countries": location_tree,
        "total_countries": len(location_tree),
        "total_federal_districts": sum(len(country["federal_districts"]) for country in location_tree),
        "total_regions": sum(
            len(fd["regions"])
            for country in location_tree
            for fd in country["federal_districts"]
        ),
        "total_cities": total_cities
    }


@router.get("/products")
async def get_products_cities_filter_tree():
    """Получить дерево локаций с количеством товаров"""
    global _cache_products, _timestamps
    
    cache_key = "products"
    try:
        # Проверяем кэш
        if cache_key in _timestamps:
            age = (datetime.now() - _timestamps[cache_key]).total_seconds()
            if age < CACHE_TTL and _cache_products:
                print("✅ Products данные из кэша")
                return _cache_products
        
        print("🔄 Загрузка данных о товарах из БД...")
        location_tree = await CitiesFilterService.build_products_location_tree()
        response = await _get_tree_response(location_tree)
        
        _cache_products = response
        _timestamps[cache_key] = datetime.now()
        print(f"✅ Products данные сохранены в кэш")
        
        return response
    except Exception as e:
        print(f"❌ Ошибка в products: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services")
async def get_services_cities_filter_tree():
    """Получить дерево локаций с количеством услуг"""
    global _cache_services, _timestamps
    
    cache_key = "services"
    try:
        # Проверяем кэш
        if cache_key in _timestamps:
            age = (datetime.now() - _timestamps[cache_key]).total_seconds()
            if age < CACHE_TTL and _cache_services:
                print("✅ Services данные из кэша")
                return _cache_services
        
        print("🔄 Загрузка данных об услугах из БД...")
        location_tree = await CitiesFilterService.build_services_location_tree()
        response = await _get_tree_response(location_tree)
        
        _cache_services = response
        _timestamps[cache_key] = datetime.now()
        print(f"✅ Services данные сохранены в кэш")
        
        return response
    except Exception as e:
        print(f"❌ Ошибка в services: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies")
async def get_companies_cities_filter_tree():
    """Получить дерево локаций с количеством компаний"""
    global _cache_companies, _timestamps
    
    cache_key = "companies"
    try:
        # Проверяем кэш
        if cache_key in _timestamps:
            age = (datetime.now() - _timestamps[cache_key]).total_seconds()
            if age < CACHE_TTL and _cache_companies:
                print("✅ Companies данные из кэша")
                return _cache_companies
        
        print("🔄 Загрузка данных о компаниях из БД...")
        location_tree = await CitiesFilterService.build_companies_location_tree()
        response = await _get_tree_response(location_tree)
        
        _cache_companies = response
        _timestamps[cache_key] = datetime.now()
        print(f"✅ Companies данные сохранены в кэш")
        
        return response
    except Exception as e:
        print(f"❌ Ошибка в companies: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_cities_filter_tree():
    """Получить полное дерево локаций (по умолчанию - компании)"""
    # По умолчанию возвращаем компании
    return await get_companies_cities_filter_tree()


@router.get("/cities-stats")
async def get_cities_stats():
    """Получить статистику по городам"""
    try:
        return await CitiesFilterService.get_cities_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
