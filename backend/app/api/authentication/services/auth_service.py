from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.schemas.user import UserCreateStep1, UserCreateStep2, User
from app.api.company.repositories.company_repository import CompanyRepository
from app.api.company.services.company_service import CompanyService
from app.core.config import settings
from app.core.email_utils import send_verification_email
from app.core.security import create_access_token, decode_token
from app.core.security import verify_password
from app_logging.logger import logger


class AuthService:
    def __init__(self, user_repository: UserRepository, db: Session):
        self.user_repository = user_repository
        self.db = db

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
        
        # Создаем неактивную компанию для пользователя
        try:
            company_repository = CompanyRepository(session=self.db)
            company_service = CompanyService(company_repository=company_repository, db=self.db)
            await company_service.create_inactive_company(updated_user)
            logger.info(f"Created inactive company for user {updated_user.id}")
        except Exception as e:
            logger.error(f"Failed to create inactive company for user {updated_user.id}: {str(e)}")
            # Не прерываем регистрацию, если не удалось создать компанию
        
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

    async def login(self, email: str, password: str) -> User:
        """Login user and return user data. Token will be set in cookie by the router."""
        user = await self.user_repository.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        return User.model_validate(user)

    async def get_current_user(self, request: Request) -> Optional[User]:
        """Get current user from Bearer token in Authorization header"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        token = auth_header.split(" ")[1]
        try:
            payload = decode_token(token)
            user_id = int(payload.get("sub"))
            if user_id is None:
                return None
        except Exception as e:
            logger.error(f"Error decoding token: {str(e)}")
            return None
            
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            return None
            
        return User.model_validate(user)

    async def create_access_token_cookie(self, user_id: int) -> str:
        """Create access token for cookie"""
        return create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    async def authenticate_user_by_inn(self, inn: str, password: str) -> Optional[User]:
        """Authenticate user by INN and password"""
        user = await self.user_repository.get_user_by_inn(inn)
        if not user:
            return None
        if not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return User.model_validate(user) 