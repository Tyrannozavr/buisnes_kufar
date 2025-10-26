from fastapi import APIRouter, HTTPException
from app.api.common.services.cities_filter_service import CitiesFilterService
from app.core.cache import redis_cache

router = APIRouter()

CACHE_KEY = "cities_filter_tree"
CACHE_TTL = 60  # 60 секунд


@router.get("/cities-filter")
async def get_cities_filter_tree():
    """Получить полное дерево локаций для фильтра городов с Redis кэшированием"""
    try:
        # Проверяем кэш Redis
        cached_data = await redis_cache.get(CACHE_KEY)
        if cached_data:
            print("✅ Данные получены из Redis кэша")
            return cached_data
        
        # Загружаем данные через service
        print("🔄 Загрузка данных из БД...")
        location_tree = await CitiesFilterService.build_location_tree()
        
        # Подсчитываем статистику
        total_cities = sum(
            len(region["cities"])
            for country in location_tree
            for fd in country["federal_districts"]
            for region in fd["regions"]
        )
        
        # Формируем ответ
        response = {
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
        
        # Сохраняем в Redis кэш
        await redis_cache.set(CACHE_KEY, response, expire=CACHE_TTL)
        print(f"✅ Данные сохранены в Redis кэш ({total_cities} городов)")
        
        return response
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cities-stats")
async def get_cities_stats():
    """Получить статистику по городам"""
    try:
        return await CitiesFilterService.get_cities_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
