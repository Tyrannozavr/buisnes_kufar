from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from app.api.authentication.schemas.user import UserCreate, User, Token, RegistrationToken
from app.api.authentication.repositories.user_repository import UserRepository
from app.core.security import create_access_token
from app.core.config import settings

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_step1(self, user_data: UserCreate) -> Tuple[RegistrationToken, str]:
        # Проверяем, не существует ли уже пользователь с таким email
        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Создаем токен регистрации
        registration_token = await self.user_repository.create_registration_token(user_data.email)
        
        # В реальном приложении здесь будет отправка email
        # Для примера просто выводим токен в консоль
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{registration_token.token}"
        print(f"Verification URL: {verification_url}")

        return registration_token, verification_url

    async def register_step2(self, token: UUID, user_data: UserCreate) -> User:
        # Проверяем токен
        registration_token = await self.user_repository.get_registration_token(token)
        if not registration_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid registration token"
            )

        if registration_token.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration token already used"
            )

        if registration_token.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration token expired"
            )

        if registration_token.email != user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email mismatch"
            )

        # Создаем пользователя
        user = await self.user_repository.create_user(user_data)
        
        # Помечаем токен как использованный
        await self.user_repository.mark_token_as_used(token)

        return User.model_validate(user)

    async def verify_token(self, token: UUID) -> bool:
        registration_token = await self.user_repository.get_registration_token(token)
        if not registration_token:
            return False

        if registration_token.is_used:
            return False

        if registration_token.expires_at < datetime.utcnow():
            return False

        return True

    async def login(self, email: str, password: str) -> Token:
        user = await self.user_repository.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not verified"
            )

        # Создаем JWT токен
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return Token(access_token=access_token)

    async def get_current_user(self, user_id: UUID) -> Optional[User]:
        user = await self.user_repository.get_user_by_id(user_id)
        return User.model_validate(user) if user else None 