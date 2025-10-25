from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status

from app.api.authentication.repositories.employee_repository import EmployeeRepository
from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse,
    PermissionUpdateRequest, AdminDeletionRequest, AdminDeletionRejectRequest,
    AVAILABLE_PERMISSIONS
)
from app.api.authentication.models.employee import EmployeeRole, EmployeeStatus, Employee
from app_logging.logger import logger
import json


class EmployeeService:
    def __init__(self, employee_repository: EmployeeRepository, user_repository: UserRepository):
        self.employee_repository = employee_repository
        self.user_repository = user_repository

    async def create_employee(self, employee_data: EmployeeCreate, company_id: int, created_by: int) -> EmployeeResponse:
        """Создать нового сотрудника"""
        # Проверяем, что сотрудник с таким email еще не существует в компании
        existing_employee = await self.employee_repository.get_employee_by_email_and_company(
            employee_data.email, company_id
        )
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee with this email already exists in the company"
            )
        
        # Устанавливаем права по умолчанию для обычных пользователей
        if employee_data.role.value == "user" and not employee_data.permissions:
            employee_data.permissions = {key: False for key in AVAILABLE_PERMISSIONS.keys()}
        
        employee = await self.employee_repository.create_employee(employee_data, company_id, created_by)
        return EmployeeResponse.model_validate(employee)

    async def get_employees(self, company_id: int, page: int = 1, per_page: int = 50) -> EmployeeListResponse:
        """Получить список сотрудников компании"""
        employees, total = await self.employee_repository.get_employees_by_company(company_id, page, per_page)
        
        employee_responses = []
        for employee in employees:
            employee_dict = employee.__dict__.copy()
            # Парсим permissions из JSON
            if employee.permissions:
                try:
                    employee_dict['permissions'] = json.loads(employee.permissions)
                except json.JSONDecodeError:
                    employee_dict['permissions'] = {}
            else:
                employee_dict['permissions'] = {}
            
            employee_responses.append(EmployeeResponse.model_validate(employee_dict))
        
        return EmployeeListResponse(
            employees=employee_responses,
            total=total,
            page=page,
            per_page=per_page
        )

    async def update_employee(self, employee_id: int, employee_data: EmployeeUpdate, current_user_id: int) -> EmployeeResponse:
        """Обновить данные сотрудника"""
        employee = await self.employee_repository.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Проверяем права доступа
        current_user_employee = await self.get_employee_by_user_id(current_user_id, employee.company_id)
        if not current_user_employee or current_user_employee.role not in [EmployeeRole.OWNER, EmployeeRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        updated_employee = await self.employee_repository.update_employee(employee_id, employee_data)
        if not updated_employee:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update employee"
            )
        
        # Парсим permissions
        employee_dict = updated_employee.__dict__.copy()
        if updated_employee.permissions:
            try:
                employee_dict['permissions'] = json.loads(updated_employee.permissions)
            except json.JSONDecodeError:
                employee_dict['permissions'] = {}
        else:
            employee_dict['permissions'] = {}
        
        return EmployeeResponse.model_validate(employee_dict)

    async def update_employee_permissions(self, employee_id: int, permissions_data: PermissionUpdateRequest, current_user_id: int) -> bool:
        """Обновить права сотрудника"""
        employee = await self.employee_repository.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Проверяем права доступа
        current_user_employee = await self.get_employee_by_user_id(current_user_id, employee.company_id)
        if not current_user_employee or current_user_employee.role not in [EmployeeRole.OWNER, EmployeeRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Валидируем права
        for permission_key in permissions_data.permissions.keys():
            if permission_key not in AVAILABLE_PERMISSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid permission: {permission_key}"
                )
        
        success = await self.employee_repository.update_employee_permissions(employee_id, permissions_data.permissions)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update permissions"
            )
        
        logger.info(f"Updated permissions for employee {employee_id}")
        return True

    async def delete_employee(self, employee_id: int, current_user_id: int) -> bool:
        """Удалить сотрудника (только обычных пользователей)"""
        employee = await self.employee_repository.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Проверяем права доступа
        current_user_employee = await self.get_employee_by_user_id(current_user_id, employee.company_id)
        if not current_user_employee or current_user_employee.role not in [EmployeeRole.OWNER, EmployeeRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Нельзя удалять администраторов через этот метод
        if employee.role == EmployeeRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use admin deletion request for administrators"
            )
        
        success = await self.employee_repository.delete_employee(employee_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete employee"
            )
        
        logger.info(f"Deleted employee {employee_id}")
        return True

    async def request_admin_deletion(self, employee_id: int, deletion_data: AdminDeletionRequest, current_user_id: int) -> bool:
        """Запросить удаление администратора"""
        employee = await self.employee_repository.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        if employee.role != EmployeeRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee is not an administrator"
            )
        
        # Проверяем права доступа
        current_user_employee = await self.get_employee_by_user_id(current_user_id, employee.company_id)
        if not current_user_employee or current_user_employee.role not in [EmployeeRole.OWNER, EmployeeRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Проверяем, что это не единственный админ
        admins_count = await self.employee_repository.count_admins_in_company(employee.company_id)
        if admins_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the only administrator"
            )
        
        success = await self.employee_repository.request_admin_deletion(employee_id, current_user_id, deletion_data.reason)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to request admin deletion"
            )
        
        logger.info(f"Requested deletion for admin {employee_id}")
        return True

    async def reject_admin_deletion(self, employee_id: int, current_user_id: int) -> bool:
        """Отклонить удаление администратора"""
        employee = await self.employee_repository.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Только сам администратор может отклонить свое удаление
        if employee.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the administrator can reject their own deletion"
            )
        
        success = await self.employee_repository.reject_admin_deletion(employee_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reject admin deletion"
            )
        
        logger.info(f"Rejected deletion for admin {employee_id}")
        return True

    async def get_employee_by_user_id(self, user_id: int, company_id: int) -> Optional[EmployeeResponse]:
        """Получить сотрудника по ID пользователя и компании"""
        from sqlalchemy import select
        result = await self.employee_repository.session.execute(
            select(Employee).where(
                Employee.user_id == user_id,
                Employee.company_id == company_id
            )
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            return None
        
        # Парсим permissions
        employee_dict = employee.__dict__.copy()
        if employee.permissions:
            try:
                employee_dict['permissions'] = json.loads(employee.permissions)
            except json.JSONDecodeError:
                employee_dict['permissions'] = {}
        else:
            employee_dict['permissions'] = {}
        
        return EmployeeResponse.model_validate(employee_dict)

    async def get_available_permissions(self) -> Dict[str, str]:
        """Получить список доступных прав"""
        return AVAILABLE_PERMISSIONS

    async def process_pending_deletions(self) -> int:
        """Обработать ожидающие удаления администраторов"""
        pending_deletions = await self.employee_repository.get_pending_deletions()
        processed_count = 0
        
        for employee in pending_deletions:
            success = await self.employee_repository.execute_admin_deletion(employee.id)
            if success:
                processed_count += 1
        
        logger.info(f"Processed {processed_count} pending admin deletions")
        return processed_count
