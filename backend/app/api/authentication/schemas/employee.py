from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum


class EmployeeRoleEnum(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"


class EmployeeStatusEnum(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class EmployeeBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    role: EmployeeRoleEnum = EmployeeRoleEnum.USER
    permissions: Optional[Dict[str, bool]] = None


class EmployeeCreate(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    role: EmployeeRoleEnum = EmployeeRoleEnum.USER
    permissions: Optional[Dict[str, bool]] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    role: Optional[EmployeeRoleEnum] = None
    permissions: Optional[Dict[str, bool]] = None


class EmployeeResponse(EmployeeBase):
    id: int
    user_id: Optional[int] = None
    company_id: int
    status: EmployeeStatusEnum
    deletion_requested_at: Optional[datetime] = None
    deletion_requested_by: Optional[int] = None
    deletion_rejected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeListResponse(BaseModel):
    employees: List[EmployeeResponse]
    total: int
    page: int
    per_page: int


class PermissionUpdateRequest(BaseModel):
    permissions: Dict[str, bool]


class AdminDeletionRequest(BaseModel):
    reason: Optional[str] = None


class AdminDeletionRejectRequest(BaseModel):
    reason: Optional[str] = None


# Список всех доступных прав в системе
AVAILABLE_PERMISSIONS = {
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
