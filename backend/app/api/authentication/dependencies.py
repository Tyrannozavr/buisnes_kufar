from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.models import User
from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.schemas.user import TokenData
from app.api.authentication.services.auth_service import AuthService
from app.core.config import settings
from app.core.security import decode_token
from app.db.dependencies import async_db_dep, get_async_db

# Create OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    auto_error=True,
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
    db: AsyncSession = Depends(get_async_db)
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
        
    user_repository = UserRepository(session=db)
    user = await user_repository.get_user_by_id(int(user_id))
    if user is None:
        raise credentials_exception
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