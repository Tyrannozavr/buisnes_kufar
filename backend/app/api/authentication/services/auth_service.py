from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, status
from app.api.authentication.schemas.user import UserCreateStep1, UserCreateStep2, User, Token, RegistrationToken
from app.api.authentication.repositories.user_repository import UserRepository
from app.core.security import create_access_token
from app.core.config import settings
from app.core.email_utils import send_verification_email
from app_logging.logger import logger


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_step1(self, user_data: UserCreateStep1) -> None:
        # Проверяем, не существует ли уже пользователь с таким email
        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        # Создаем пользователя (без пароля)
        user = await self.user_repository.create_user_step1(user_data)
        # Создаем токен регистрации
        import secrets
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        await self.user_repository.create_registration_token(
            email=user_data.email,
            token=token,
            expires_at=expires_at
        )
        logger.info(f"Created registration token for {user_data.email}")
        # Формируем URL для верификации
        verification_url = f"{settings.FRONTEND_URL}/auth/register/complete?token={token}"
        # Отправляем email с ссылкой для верификации
        email_sent = await send_verification_email(user_data.email, verification_url)
        if not email_sent:
            # Если не удалось отправить email, можно удалить токен (опционально)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email"
            )

    async def register_step2(self, user_data: UserCreateStep2) -> User:
        # Проверяем токен
        registration_token = await self.user_repository.get_registration_token(user_data.token)
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
        # Получаем пользователя по email из токена
        db_user = await self.user_repository.get_user_by_email(registration_token.email)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        # Обновляем пользователя (ИНН, должность, пароль)
        updated_user = await self.user_repository.update_user_step2(db_user, user_data)
        # Помечаем токен как использованный
        await self.user_repository.mark_token_as_used(user_data.token)
        return User.model_validate(updated_user)

    async def verify_token(self, token: str) -> bool:
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
        # Создаем JWT токен
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return Token(access_token=access_token)

    async def get_current_user(self, user_id: int) -> Optional[User]:
        db_user = await self.user_repository.get_user_by_id(user_id)
        return User.model_validate(db_user) if db_user else None

    async def create_access_token_cookie(self, user_id: int) -> str:
        """Create access token for cookie"""
        return create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        ) 