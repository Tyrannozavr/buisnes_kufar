from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.authentication.models import User
from app.api.authentication.repositories.employee_repository import EmployeeRepository
from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.schemas.user import TokenData
from app.api.authentication.services.auth_service import AuthService
from app.api.authentication.services.employee_service import EmployeeService
from app.api.company.repositories.company_repository import CompanyRepository
from app.core.config import settings
from app.core.security import decode_token
from app.db.dependencies import async_db_dep, get_async_db

# Create OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    auto_error=True,  # Возвращаем обратно для продакшена
    scheme_name="Bearer",
    scopes=None,
    description="OAuth2 password bearer token",
)


async def get_user_repository(
        session: async_db_dep
) -> UserRepository:
    return UserRepository(session)


user_repository_dep = Annotated[UserRepository, Depends(get_user_repository)]


async def get_auth_service(
        user_repository: user_repository_dep,
        db: async_db_dep
) -> AuthService:
    return AuthService(user_repository=user_repository, db=db)


# Для удобства использования в роутерах
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db = Depends(get_async_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    from app.core.ttl_cache import cache_get, cache_set, user_cache_key

    uid = int(user_id)
    cache_key = user_cache_key(uid)
    cached = await cache_get(cache_key)
    if isinstance(cached, dict) and cached.get("id") == uid and cached.get("is_active", True):
        from app.api.authentication.models.roles_positions import UserRole

        role_raw = cached.get("role") or UserRole.USER
        try:
            role = UserRole(role_raw) if not isinstance(role_raw, UserRole) else role_raw
        except Exception:
            role = UserRole.USER
        return User(
            id=cached["id"],
            email=cached.get("email") or f"user{uid}@cache.local",
            company_id=cached.get("company_id"),
            is_active=bool(cached.get("is_active", True)),
            hashed_password="",
            phone=cached.get("phone") or "",
            first_name=cached.get("first_name"),
            last_name=cached.get("last_name"),
            role=role,
        )

    user = await db.get(User, uid)
    if user is None or not user.is_active:
        raise credentials_exception
    await cache_set(
        cache_key,
        {
            "id": user.id,
            "email": user.email,
            "company_id": user.company_id,
            "is_active": user.is_active,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": getattr(user.role, "value", user.role),
        },
    )
    return user


async def get_token_data(
        token: Annotated[str, Depends(oauth2_scheme)],
) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    return TokenData(user_id=int(user_id))


current_user_dep = Annotated[User, Depends(get_current_user)]
token_data_dep = Annotated[TokenData, Depends(get_token_data)]


# Дополнительные зависимости для сотрудников
async def get_current_user_id(
        token: Annotated[str, Depends(oauth2_scheme)]
) -> int:
    """Получить ID текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token is None:
        raise credentials_exception
        
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    return int(user_id)


async def get_employee_repository(
        session: async_db_dep
) -> EmployeeRepository:
    return EmployeeRepository(session)


async def get_company_repository(
        session: async_db_dep
) -> CompanyRepository:
    return CompanyRepository(session)


async def get_employee_service(
        employee_repository: Annotated[EmployeeRepository, Depends(get_employee_repository)],
        user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> EmployeeService:
    return EmployeeService(
        employee_repository=employee_repository,
        user_repository=user_repository
    )


# Для удобства использования в роутерах
get_current_user_id_dep = Annotated[int, Depends(get_current_user_id)]
EmployeeRepositoryDep = Annotated[EmployeeRepository, Depends(get_employee_repository)]
CompanyRepositoryDep = Annotated[CompanyRepository, Depends(get_company_repository)]
EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
