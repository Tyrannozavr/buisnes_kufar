from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.services.auth_service import AuthService
from app.db.base import get_db


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> UserRepository:
    return UserRepository(session)

async def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> AuthService:
    return AuthService(user_repository)

# Для удобства использования в роутерах
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)] 