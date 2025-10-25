from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, ConfigDict, constr

from app.api.company.schemas.company import CompanyLogoUrlMixin


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    phone: constr(min_length=10, max_length=15)
    inn: Optional[str] = None
    position: Optional[str] = None


class UserCreateStep1(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    phone: constr(min_length=10, max_length=15)
    recaptcha_token: Optional[str] = None  # Токен reCAPTCHA v3 (опциональный для localhost)


class UserCreateStep2(BaseModel):
    token: str
    inn: constr(min_length=10, max_length=12)
    password: constr(min_length=8)


class UserUpdate(BaseModel):
    """Схема для обновления профиля пользователя"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    phone: Optional[constr(min_length=10, max_length=15)] = None
    inn: Optional[str] = None
    position: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    id: int
    is_active: bool
    hashed_password: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegistrationTokenCreate(BaseModel):
    email: EmailStr


class RegistrationTokenVerify(BaseModel):
    token: str


class RegistrationTokenResponse(BaseModel):
    is_valid: bool
    message: Optional[str] = None


class RegistrationToken(BaseModel):
    token: str
    email: EmailStr
    created_at: datetime
    expires_at: datetime
    is_used: bool = False
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class RegistrationStep2(BaseModel):
    token: uuid4
    password: str


class TokenData(BaseModel):
    user_id: int


class VerifyTokenResponse(CompanyLogoUrlMixin):
    is_valid: bool
    company_name: str | None = None
    company_slug: str | None = None
    company_id: int | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: constr(min_length=8)


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr
    password: str


class ChangeEmailConfirmRequest(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: constr(min_length=8)


# Новые схемы для восстановления пароля с кодами
class PasswordRecoveryRequest(BaseModel):
    email: EmailStr


class PasswordRecoveryVerifyRequest(BaseModel):
    email: EmailStr
    code: str


class PasswordRecoveryResetRequest(BaseModel):
    email: EmailStr
    code: str
    newPassword: constr(min_length=8)
