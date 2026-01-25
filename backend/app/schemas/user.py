from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    inn: constr(min_length=9, max_length=12, pattern=r'^\d+$')
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: constr(min_length=8)


class UserLogin(BaseModel):
    login: str  # Может быть email или телефон
    # Для dev-тестов допускаем короткий пароль (см. ТЗ с 123456).
    # Регистрация/смена пароля всё ещё требуют min_length=8 в authentication схемах.
    password: constr(min_length=6)


# class UserDocsLogin(BaseModel):
#     username: str = Form(...),
#     password: str = Form(...),
#     grant_type: Optional[str] = Form(None),


class UserResponse(UserBase):
    id: UUID
    is_active: bool = True

    class Config:
        from_attributes = True
