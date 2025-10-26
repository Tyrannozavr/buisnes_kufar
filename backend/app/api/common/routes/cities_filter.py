from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.api.common.services.cities_filter_service import CitiesFilterService

router = APIRouter()

# Простой in-memory кэш
_cache_data = None
_cache_timestamp = None
CACHE_TTL = 60  # 60 секунд


@router.get("/cities-filter")
async def get_cities_filter_tree():
    """Получить полное дерево локаций для фильтра городов с кэшированием"""
    global _cache_data, _cache_timestamp
    
    try:
        # Проверяем in-memory кэш
        if _cache_data and _cache_timestamp:
            age = (datetime.now() - _cache_timestamp).total_seconds()
            if age < CACHE_TTL:
                print("✅ Данные получены из in-memory кэша")
                return _cache_data
        
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
        
        # Сохраняем в in-memory кэш
        _cache_data = response
        _cache_timestamp = datetime.now()
        print(f"✅ Данные сохранены в in-memory кэш ({total_cities} городов)")
        
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
