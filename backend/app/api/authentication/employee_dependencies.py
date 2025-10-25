from typing import Annotated

from fastapi import Depends

from app.api.authentication.repositories.employee_repository import EmployeeRepository
from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.services.employee_service import EmployeeService
from app.db.dependencies import async_db_dep


async def get_employee_service(db: async_db_dep) -> EmployeeService:
    """Dependency для получения сервиса сотрудников"""
    employee_repository = EmployeeRepository(session=db)
    user_repository = UserRepository(session=db)
    return EmployeeService(
        employee_repository=employee_repository, 
        user_repository=user_repository
    )


employee_service_dep = Annotated[EmployeeService, Depends(get_employee_service)]
