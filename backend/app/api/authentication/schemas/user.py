from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    phone: str
    inn: str
    position: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: UUID
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

class User(UserBase):
    id: uuid4
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RegistrationToken(BaseModel):
    token: uuid4
    email: EmailStr
    registration_data: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    is_used: bool = False

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str

class RegistrationStep2(BaseModel):
    token: uuid4
    password: str 