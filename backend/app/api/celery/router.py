from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult

from app.celery_app import celery_app

# Задачи кэширования удалены - теперь используется прямой JOIN
# from app.tasks.cache_tasks import (
#     update_product_city_cache,
#     update_company_city_cache,
#     update_cities_product_count,
#     refresh_all_caches,
#     clear_all_caches
# )

router = APIRouter(prefix="/celery", tags=["celery"])


# Эндпоинты для кэширования удалены - теперь используется прямой JOIN и Redis
# @router.post("/tasks/update-product-city-cache")
# @router.post("/tasks/update-company-city-cache")
# @router.post("/tasks/update-cities-product-count")
# @router.post("/tasks/refresh-all-caches")
# @router.post("/tasks/clear-all-caches")


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Получает статус задачи по ID"""
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "status": "pending",
                "message": "Задача ожидает выполнения"
            }
        elif task_result.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "status": "progress",
                "current": task_result.info.get("current", 0),
                "total": task_result.info.get("total", 1),
                "percent": int((task_result.info.get("current", 0) / task_result.info.get("total", 1)) * 100)
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "status": "success",
                "result": task_result.result
            }
        elif task_result.state == "FAILURE":
            response = {
                "task_id": task_id,
                "status": "failure",
                "error": str(task_result.info)
            }
        else:
            response = {
                "task_id": task_id,
                "status": task_result.state,
                "result": task_result.result
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса задачи: {str(e)}")


@router.get("/tasks")
async def get_active_tasks() -> Dict[str, Any]:
    """Получает список активных задач"""
    try:
        # Получаем активные задачи из Celery
        inspect = celery_app.control.inspect()
        
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()
        
        return {
            "active": active_tasks,
            "scheduled": scheduled_tasks,
            "reserved": reserved_tasks
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения активных задач: {str(e)}")


@router.get("/stats")
async def get_celery_stats() -> Dict[str, Any]:
    """Получает статистику Celery"""
    try:
        inspect = celery_app.control.inspect()
        
        stats = inspect.stats()
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        
        return {
            "stats": stats,
            "active_tasks_count": len(active_tasks) if active_tasks else 0,
            "scheduled_tasks_count": len(scheduled_tasks) if scheduled_tasks else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")
