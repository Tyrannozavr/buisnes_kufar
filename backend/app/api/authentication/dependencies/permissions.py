from typing import Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.repositories.employee_repository import EmployeeRepository
from app.api.authentication.middleware.permissions import PermissionChecker, check_user_permission
from app.api.authentication.dependencies import get_current_user
from app.api.authentication.schemas.user import User
from app.api.company.dependencies import company_service_dep
from app.db.dependencies import async_db_dep
from app_logging.logger import logger


async def get_employee_repository(db: async_db_dep) -> EmployeeRepository:
    """Получить репозиторий сотрудников"""
    return EmployeeRepository(session=db)


async def get_permission_checker(employee_repository: EmployeeRepository = Depends(get_employee_repository)) -> PermissionChecker:
    """Получить проверку прав"""
    return PermissionChecker(employee_repository)


async def get_current_employee(
    current_user: User = Depends(get_current_user),
    company_service: company_service_dep = Depends(),
    employee_repository: EmployeeRepository = Depends(get_employee_repository)
):
    """Получить текущего сотрудника"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    # Получаем компанию пользователя
    company = await company_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Получаем сотрудника
    employee = await employee_repository.get_employee_by_user_id(current_user.id, company.id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an employee of this company"
        )
    
    return employee


def require_permission(permission_key: str):
    """Декоратор для проверки прав доступа"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Извлекаем зависимости
            current_user = None
            company_service = None
            employee_repository = None
            
            for arg in args:
                if isinstance(arg, User):
                    current_user = arg
                elif hasattr(arg, 'get_company_by_user_id'):
                    company_service = arg
                elif hasattr(arg, 'get_employee_by_user_id'):
                    employee_repository = arg
            
            if not all([current_user, company_service, employee_repository]):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Required dependencies not found"
                )
            
            # Получаем компанию
            company = await company_service.get_company_by_user_id(current_user.id)
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )
            
            # Проверяем права
            has_permission = await check_user_permission(current_user.id, company.id, permission_key, employee_repository)
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {permission_key} required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def check_permission_dependency(
    permission_key: str,
    current_user: User = Depends(get_current_user),
    company_service: company_service_dep = Depends(),
    employee_repository: EmployeeRepository = Depends(get_employee_repository)
) -> bool:
    """Зависимость для проверки конкретного права"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    # Получаем компанию
    company = await company_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Проверяем права
    has_permission = await check_user_permission(current_user.id, company.id, permission_key, employee_repository)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions: {permission_key} required"
        )
    
    return True


# Специфичные зависимости для разных прав
def require_company_management():
    return Depends(lambda: check_permission_dependency("company_management"))


def require_company_data():
    return Depends(lambda: check_permission_dependency("company_data"))


def require_products():
    return Depends(lambda: check_permission_dependency("products"))


def require_announcements():
    return Depends(lambda: check_permission_dependency("announcements"))


def require_business_connections():
    return Depends(lambda: check_permission_dependency("business_connections"))


def require_partners():
    return Depends(lambda: check_permission_dependency("partners"))


def require_suppliers():
    return Depends(lambda: check_permission_dependency("suppliers"))


def require_buyers():
    return Depends(lambda: check_permission_dependency("buyers"))


def require_documents():
    return Depends(lambda: check_permission_dependency("documents"))


def require_contracts():
    return Depends(lambda: check_permission_dependency("contracts"))


def require_sales():
    return Depends(lambda: check_permission_dependency("sales"))


def require_purchases():
    return Depends(lambda: check_permission_dependency("purchases"))


def require_communications():
    return Depends(lambda: check_permission_dependency("communications"))


def require_messages():
    return Depends(lambda: check_permission_dependency("messages"))


def require_administration():
    return Depends(lambda: check_permission_dependency("administration"))
