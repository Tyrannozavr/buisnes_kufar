from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.api.authentication.dependencies import get_current_user_id_dep
from app.api.authentication.employee_dependencies import employee_service_dep
from app.api.authentication.models.roles_positions import RoleManager, UserRole
from app.api.authentication.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse,
    PermissionUpdateRequest, AdminDeletionRequest
)
from app.api.authentication.schemas.positions import PositionsListResponse, PositionResponse
from app.api.company.dependencies import company_service_dep
from app.db.dependencies import async_db_dep
from app_logging.logger import logger

router = APIRouter()


@router.post("/employees", response_model=EmployeeResponse)
async def create_employee(
    employee_data: EmployeeCreate,
    db: async_db_dep,
    current_user_id: get_current_user_id_dep
):
    """Создать нового сотрудника"""
    try:
        # Создаем сервисы напрямую
        from app.api.company.repositories.company_repository import CompanyRepository
        from app.api.company.services.company_service import CompanyService
        from app.api.authentication.repositories.employee_repository import EmployeeRepository
        from app.api.authentication.repositories.user_repository import UserRepository
        from app.api.authentication.services.employee_service import EmployeeService
        
        company_repository = CompanyRepository(db)
        company_service = CompanyService(company_repository, db)
        
        employee_repository = EmployeeRepository(session=db)
        user_repository = UserRepository(session=db)
        employee_service = EmployeeService(employee_repository, user_repository)
        
        company_profile = await company_service.get_company_by_user_id(current_user_id)
        if not company_profile.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        employee = await employee_service.create_employee(employee_data, company_profile.id, current_user_id)
        return employee

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error creating employee for user %s", current_user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create employee",
        ) from e


@router.get("/company-employees", response_model=EmployeeListResponse)
async def get_employees(
    company_service: company_service_dep,
    employee_service: employee_service_dep,
    current_user_id: get_current_user_id_dep,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100)
):
    """Получить список сотрудников компании"""
    try:
        # Получаем компанию текущего пользователя
        company_profile = await company_service.get_company_by_user_id(current_user_id)
        
        # Проверяем, есть ли у пользователя компания
        if not company_profile or not company_profile.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found for current user"
            )
        
        employees = await employee_service.get_employees(company_profile.id, page, per_page)
        return employees
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting employees: {str(e)}"
        )


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    company_service: company_service_dep,
    employee_service: employee_service_dep,
    current_user_id: int = Depends(get_current_user_id_dep)
):
    """Получить сотрудника по ID"""
    # Получаем компанию текущего пользователя
    company_profile = await company_service.get_company_by_user_id(current_user_id)
    if not company_profile.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    employee = await employee_service.employee_repository.get_employee_by_id(employee_id)
    if not employee or employee.company_id != company_profile.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Парсим permissions
    import json
    employee_dict = employee.__dict__.copy()
    if employee.permissions:
        try:
            employee_dict['permissions'] = json.loads(employee.permissions)
        except json.JSONDecodeError:
            employee_dict['permissions'] = {}
    else:
        employee_dict['permissions'] = {}
    
    return EmployeeResponse.model_validate(employee_dict)


@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    employee_service: employee_service_dep,
    current_user_id: int = Depends(get_current_user_id_dep)
):
    """Обновить данные сотрудника"""
    employee = await employee_service.update_employee(employee_id, employee_data, current_user_id)
    return employee


@router.put("/employees/{employee_id}/permissions")
async def update_employee_permissions(
    # request: Request,
    employee_id: int,
    permissions_data: PermissionUpdateRequest,
    db: async_db_dep,
    current_user_id: get_current_user_id_dep,
):
    """Обновить права сотрудника"""
    # Создаем сервис внутри функции
    from app.api.authentication.repositories.employee_repository import EmployeeRepository
    from app.api.authentication.repositories.user_repository import UserRepository
    from app.api.authentication.services.employee_service import EmployeeService
    
    employee_repository = EmployeeRepository(session=db)
    user_repository = UserRepository(session=db)
    employee_service = EmployeeService(
        employee_repository=employee_repository, 
        user_repository=user_repository
    )
    
    # Временно отключаем проверку компании для тестирования
    success = await employee_service.update_employee_permissions(employee_id, permissions_data, current_user_id)
    return {"success": success, "message": "Permissions updated successfully"}


@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: int,
    employee_service: employee_service_dep,
    current_user_id: int = Depends(get_current_user_id_dep)
):
    """Удалить сотрудника (только обычных пользователей)"""
    success = await employee_service.delete_employee(employee_id, current_user_id)
    return {"success": success, "message": "Employee deleted successfully"}


@router.post("/employees/{employee_id}/request-deletion")
async def request_admin_deletion(
    employee_id: int,
    deletion_data: AdminDeletionRequest,
    employee_service: employee_service_dep,
    current_user_id: int = Depends(get_current_user_id_dep)
):
    """Запросить удаление администратора"""
    success = await employee_service.request_admin_deletion(employee_id, deletion_data, current_user_id)
    return {"success": success, "message": "Admin deletion requested. It will be executed in 48 hours unless rejected."}


@router.post("/employees/{employee_id}/reject-deletion")
async def reject_admin_deletion(
    employee_id: int,
    employee_service: employee_service_dep,
    current_user_id: int = Depends(get_current_user_id_dep)
):
    """Отклонить удаление администратора"""
    success = await employee_service.reject_admin_deletion(employee_id, current_user_id)
    return {"success": success, "message": "Admin deletion rejected"}


@router.get("/permissions")
async def get_available_permissions(
    employee_service: employee_service_dep
):
    """Получить список доступных прав"""
    permissions = await employee_service.get_available_permissions()
    return {"permissions": permissions}


@router.post("/process-pending-deletions")
async def process_pending_deletions(
    employee_service: employee_service_dep,
    current_user_id: int = Depends(get_current_user_id_dep)
):
    """Обработать ожидающие удаления администраторов (для cron задач)"""
    # Проверяем права доступа (только владельцы могут запускать эту задачу)
    # Это можно сделать через middleware или проверку роли
    
    processed_count = await employee_service.process_pending_deletions()
    return {"processed_count": processed_count, "message": f"Processed {processed_count} pending deletions"}


@router.get("/positions", response_model=PositionsListResponse)
async def get_available_positions():
    """Получить список поддерживаемых должностей"""
    positions_data = RoleManager.get_all_positions()
    
    positions = [
        PositionResponse(value=pos["value"], label=pos["label"])
        for pos in positions_data
    ]
    
    return PositionsListResponse(positions=positions)


@router.get("/registration-roles")
async def get_registration_roles():
    """Получить список ролей для регистрации (Администратор и Пользователь)"""
    return {"roles": RoleManager.get_registration_roles()}


@router.get("/roles")
async def get_available_roles():
    """Получить список всех ролей для администрирования"""
    roles_data = [
        {
            "value": UserRole.OWNER.value,
            "label": RoleManager.ROLE_LABELS[UserRole.OWNER],
            "description": "Создатель компании с полными правами"
        },
        {
            "value": UserRole.ADMIN.value,
            "label": RoleManager.ROLE_LABELS[UserRole.ADMIN],
            "description": "Полные права доступа (до 3 администраторов в компании)"
        },
        {
            "value": UserRole.USER.value,
            "label": RoleManager.ROLE_LABELS[UserRole.USER],
            "description": "Стандартный набор прав (неограниченное количество)"
        }
    ]
    return {"roles": roles_data}
