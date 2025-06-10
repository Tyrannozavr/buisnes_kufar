from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field, ConfigDict, constr


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

class UserCreateStep2(BaseModel):
    token: str
    inn: constr(min_length=10, max_length=12)
    position: str
    password: constr(min_length=8)

class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

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