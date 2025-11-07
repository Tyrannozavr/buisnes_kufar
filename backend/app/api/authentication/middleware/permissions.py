from typing import Optional, Callable, Any
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.api.authentication.repositories.employee_repository import EmployeeRepository
from app.api.authentication.models.employee import EmployeeRole
from app_logging.logger import logger
import json


class PermissionChecker:
    def __init__(self, employee_repository: EmployeeRepository):
        self.employee_repository = employee_repository

    async def check_permission(self, user_id: int, company_id: int, permission_key: str) -> bool:
        """Проверить право доступа пользователя"""
        try:
            # Получаем сотрудника
            employee = await self.employee_repository.get_employee_by_user_id(user_id, company_id)
            if not employee:
                logger.warning(f"Employee not found for user {user_id} in company {company_id}")
                return False

            # Владелец имеет все права
            if employee.role == EmployeeRole.OWNER:
                return True

            # Администратор имеет все права кроме администрирования
            if employee.role == EmployeeRole.ADMIN and permission_key != "administration":
                return True

            # Проверяем конкретное право
            if employee.permissions:
                try:
                    permissions = json.loads(employee.permissions)
                    return permissions.get(permission_key, False)
                except json.JSONDecodeError:
                    logger.error(f"Invalid permissions JSON for employee {employee.id}")
                    return False

            return False
        except Exception as e:
            logger.error(f"Error checking permission: {str(e)}")
            return False

    async def require_permission(self, permission_key: str):
        """Декоратор для проверки прав доступа"""
        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                # Извлекаем user_id и company_id из аргументов
                # Это нужно будет адаптировать под конкретные эндпоинты
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                
                if not request:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Request object not found"
                    )

                # Получаем user_id из токена (нужно будет реализовать)
                user_id = await self._get_user_id_from_request(request)
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not authenticated"
                    )

                # Получаем company_id (нужно будет адаптировать под конкретные эндпоинты)
                company_id = await self._get_company_id_from_request(request, kwargs)
                if not company_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Company ID not found"
                    )

                # Проверяем права
                has_permission = await self.check_permission(user_id, company_id, permission_key)
                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions: {permission_key} required"
                    )

                return await func(*args, **kwargs)
            return wrapper
        return decorator

    async def _get_user_id_from_request(self, request: Request) -> Optional[int]:
        """Получить user_id из токена в запросе"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        try:
            # Извлекаем токен из заголовка
            token = auth_header.split(" ")[1]
            
            # Импортируем функцию декодирования токена
            from app.core.security import decode_token
            
            # Декодируем токен
            payload = decode_token(token)
            user_id: str = payload.get("sub")
            
            if user_id is None:
                return None
                
            return int(user_id)
        except Exception:
            return None

    async def _get_company_id_from_request(self, request: Request, kwargs: dict) -> Optional[int]:
        """Получить company_id из запроса"""
        # Проверяем параметры функции
        if 'company_id' in kwargs:
            return kwargs['company_id']
        
        # Проверяем query параметры
        company_id = request.query_params.get('company_id')
        if company_id:
            return int(company_id)
        
        # Проверяем path параметры
        if hasattr(request, 'path_params') and 'company_id' in request.path_params:
            return int(request.path_params['company_id'])
        
        return None


def create_permission_checker(employee_repository: EmployeeRepository) -> PermissionChecker:
    """Создать экземпляр проверки прав"""
    return PermissionChecker(employee_repository)


# Глобальные права доступа
PERMISSIONS = {
    "company_management": "Управление компанией",
    "company_data": "Данные компании", 
    "products": "Продукция",
    "announcements": "Объявления",
    "business_connections": "Бизнес-связи",
    "partners": "Партнеры",
    "suppliers": "Поставщики", 
    "buyers": "Покупатели",
    "documents": "Документы",
    "contracts": "Договоры",
    "sales": "Продажи",
    "purchases": "Закупки",
    "communications": "Коммуникации",
    "messages": "Сообщения",
    "administration": "Администрирование"
}


async def check_user_permission(user_id: int, company_id: int, permission_key: str, employee_repository: EmployeeRepository) -> bool:
    """Проверить право доступа пользователя (упрощенная версия)"""
    checker = PermissionChecker(employee_repository)
    return await checker.check_permission(user_id, company_id, permission_key)
