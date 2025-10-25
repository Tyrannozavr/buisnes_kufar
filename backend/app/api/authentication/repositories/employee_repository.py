from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.models.employee import Employee, EmployeePermission, EmployeeRole, EmployeeStatus
from app.api.authentication.schemas.employee import EmployeeCreate, EmployeeUpdate, PermissionUpdateRequest
from app_logging.logger import logger
import json


class EmployeeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_employee(self, employee_data: EmployeeCreate, company_id: int, created_by: int) -> Employee:
        """Создать нового сотрудника"""
        # Преобразуем permissions в JSON строку
        permissions_json = None
        if employee_data.permissions:
            permissions_json = json.dumps(employee_data.permissions)
        
        employee = Employee(
            email=employee_data.email,
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            patronymic=employee_data.patronymic,
            phone=employee_data.phone,
            position=employee_data.position,
            role=EmployeeRole(employee_data.role.value),
            status=EmployeeStatus.PENDING,
            permissions=permissions_json,
            company_id=company_id,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        
        self.session.add(employee)
        await self.session.commit()
        await self.session.refresh(employee)
        
        logger.info(f"Created employee {employee.email} for company {company_id}")
        return employee

    async def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """Получить сотрудника по ID"""
        result = await self.session.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()

    async def get_employee_by_email_and_company(self, email: str, company_id: Optional[int] = None) -> Optional[Employee]:
        """Получить сотрудника по email и компании (company_id может быть None для поиска по всем компаниям)"""
        if company_id:
            result = await self.session.execute(
                select(Employee).where(
                    and_(
                        Employee.email == email,
                        Employee.company_id == company_id
                    )
                )
            )
        else:
            result = await self.session.execute(
                select(Employee).where(Employee.email == email)
            )
        return result.scalar_one_or_none()

    async def get_employees_by_company(self, company_id: int, page: int = 1, per_page: int = 50) -> tuple[List[Employee], int]:
        """Получить список сотрудников компании с пагинацией"""
        # Общее количество
        count_result = await self.session.execute(
            select(Employee).where(Employee.company_id == company_id)
        )
        total = len(count_result.scalars().all())
        
        # Список с пагинацией
        offset = (page - 1) * per_page
        result = await self.session.execute(
            select(Employee)
            .where(Employee.company_id == company_id)
            .order_by(Employee.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        
        employees = result.scalars().all()
        return list(employees), total

    async def update_employee(self, employee_id: int, employee_data: EmployeeUpdate) -> Optional[Employee]:
        """Обновить данные сотрудника"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return None
        
        # Обновляем поля
        for field, value in employee_data.model_dump(exclude_unset=True).items():
            if field == 'permissions' and value is not None:
                setattr(employee, field, json.dumps(value))
            elif field == 'role' and value is not None:
                setattr(employee, field, EmployeeRole(value.value))
            else:
                setattr(employee, field, value)
        
        employee.updated_at = datetime.utcnow()
        self.session.add(employee)
        await self.session.commit()
        await self.session.refresh(employee)
        
        logger.info(f"Updated employee {employee_id}")
        return employee

    async def update_employee_permissions(self, employee_id: int, permissions: Dict[str, bool]) -> bool:
        """Обновить права сотрудника"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return False
        
        employee.permissions = json.dumps(permissions)
        employee.updated_at = datetime.utcnow()
        self.session.add(employee)
        await self.session.commit()
        
        logger.info(f"Updated permissions for employee {employee_id}")
        return True

    async def activate_employee(self, employee_id: int, user_id: int) -> bool:
        """Активировать сотрудника (привязать к пользователю)"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return False
        
        employee.user_id = user_id
        employee.status = EmployeeStatus.ACTIVE
        employee.updated_at = datetime.utcnow()
        self.session.add(employee)
        await self.session.commit()
        
        logger.info(f"Activated employee {employee_id} with user {user_id}")
        return True

    async def deactivate_employee(self, employee_id: int) -> bool:
        """Деактивировать сотрудника"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return False
        
        employee.status = EmployeeStatus.INACTIVE
        employee.updated_at = datetime.utcnow()
        self.session.add(employee)
        await self.session.commit()
        
        logger.info(f"Deactivated employee {employee_id}")
        return True

    async def request_admin_deletion(self, employee_id: int, requested_by: int, reason: Optional[str] = None) -> bool:
        """Запросить удаление администратора"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee or employee.role != EmployeeRole.ADMIN:
            return False
        
        # Проверяем, что это не единственный админ
        admins_count = await self.count_admins_in_company(employee.company_id)
        if admins_count <= 1:
            return False
        
        employee.deletion_requested_at = datetime.utcnow()
        employee.deletion_requested_by = requested_by
        employee.updated_at = datetime.utcnow()
        self.session.add(employee)
        await self.session.commit()
        
        logger.info(f"Requested deletion for admin {employee_id} by {requested_by}")
        return True

    async def reject_admin_deletion(self, employee_id: int) -> bool:
        """Отклонить удаление администратора"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return False
        
        employee.deletion_rejected_at = datetime.utcnow()
        employee.deletion_requested_at = None
        employee.deletion_requested_by = None
        employee.updated_at = datetime.utcnow()
        self.session.add(employee)
        await self.session.commit()
        
        logger.info(f"Rejected deletion for admin {employee_id}")
        return True

    async def execute_admin_deletion(self, employee_id: int) -> bool:
        """Выполнить удаление администратора (через 48 часов)"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee or employee.role != EmployeeRole.ADMIN:
            return False
        
        # Проверяем, что прошло 48 часов
        if not employee.deletion_requested_at:
            return False
        
        time_diff = datetime.utcnow() - employee.deletion_requested_at
        if time_diff < timedelta(hours=48):
            return False
        
        # Проверяем, что удаление не было отклонено
        if employee.deletion_rejected_at:
            return False
        
        employee.status = EmployeeStatus.DELETED
        employee.updated_at = datetime.utcnow()
        self.session.add(employee)
        await self.session.commit()
        
        logger.info(f"Executed deletion for admin {employee_id}")
        return True

    async def count_admins_in_company(self, company_id: int) -> int:
        """Подсчитать количество активных администраторов в компании"""
        result = await self.session.execute(
            select(Employee).where(
                and_(
                    Employee.company_id == company_id,
                    Employee.role == EmployeeRole.ADMIN,
                    Employee.status == EmployeeStatus.ACTIVE
                )
            )
        )
        return len(result.scalars().all())

    async def get_pending_deletions(self) -> List[Employee]:
        """Получить список администраторов, ожидающих удаления"""
        result = await self.session.execute(
            select(Employee).where(
                and_(
                    Employee.role == EmployeeRole.ADMIN,
                    Employee.deletion_requested_at.isnot(None),
                    Employee.deletion_rejected_at.is_(None),
                    Employee.status == EmployeeStatus.ACTIVE
                )
            )
        )
        return list(result.scalars().all())

    async def delete_employee(self, employee_id: int) -> bool:
        """Удалить сотрудника (только для обычных пользователей)"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee or employee.role == EmployeeRole.ADMIN:
            return False
        
        await self.session.delete(employee)
        await self.session.commit()
        
        logger.info(f"Deleted employee {employee_id}")
        return True
