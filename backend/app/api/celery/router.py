from typing import Annotated, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from celery.result import AsyncResult

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models import User
from app.api.authentication.models.roles_positions import UserRole
from app.celery_app import celery_app

router = APIRouter(prefix="/celery", tags=["celery"])


async def require_celery_admin(
	current_user: Annotated[User, Depends(get_current_user)],
) -> User:
	"""Celery introspection — only company OWNER/ADMIN."""
	role = getattr(current_user, "role", None)
	if role not in (UserRole.OWNER, UserRole.ADMIN):
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Insufficient permissions",
		)
	return current_user


@router.get("/tasks/{task_id}")
async def get_task_status(
	task_id: str,
	_: Annotated[User, Depends(require_celery_admin)],
) -> Dict[str, Any]:
	"""Получает статус задачи по ID"""
	try:
		task_result = AsyncResult(task_id, app=celery_app)

		if task_result.state == "PENDING":
			response = {
				"task_id": task_id,
				"status": "pending",
				"message": "Задача ожидает выполнения",
			}
		elif task_result.state == "PROGRESS":
			response = {
				"task_id": task_id,
				"status": "progress",
				"current": task_result.info.get("current", 0),
				"total": task_result.info.get("total", 1),
				"percent": int(
					(task_result.info.get("current", 0) / task_result.info.get("total", 1)) * 100
				),
			}
		elif task_result.state == "SUCCESS":
			response = {
				"task_id": task_id,
				"status": "success",
				"result": task_result.result,
			}
		elif task_result.state == "FAILURE":
			response = {
				"task_id": task_id,
				"status": "failure",
				"error": str(task_result.info),
			}
		else:
			response = {
				"task_id": task_id,
				"status": task_result.state,
				"result": task_result.result,
			}

		return response

	except Exception as e:
		raise HTTPException(status_code=500, detail="Ошибка получения статуса задачи") from e


@router.get("/tasks")
async def get_active_tasks(
	_: Annotated[User, Depends(require_celery_admin)],
) -> Dict[str, Any]:
	"""Получает список активных задач"""
	try:
		inspect = celery_app.control.inspect()
		return {
			"active": inspect.active(),
			"scheduled": inspect.scheduled(),
			"reserved": inspect.reserved(),
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail="Ошибка получения активных задач") from e


@router.get("/stats")
async def get_celery_stats(
	_: Annotated[User, Depends(require_celery_admin)],
) -> Dict[str, Any]:
	"""Получает статистику Celery"""
	try:
		inspect = celery_app.control.inspect()
		stats = inspect.stats()
		active_tasks = inspect.active()
		scheduled_tasks = inspect.scheduled()
		return {
			"stats": stats,
			"active_tasks_count": len(active_tasks) if active_tasks else 0,
			"scheduled_tasks_count": len(scheduled_tasks) if scheduled_tasks else 0,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail="Ошибка получения статистики") from e
