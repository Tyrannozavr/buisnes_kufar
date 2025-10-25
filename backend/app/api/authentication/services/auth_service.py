from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.schemas.user import UserCreateStep1, UserCreateStep2, User, ChangePasswordRequest, \
    ChangeEmailRequest
from app.api.company.repositories.company_repository import CompanyRepository
from app.core.config import settings
from app.core.email_utils import send_verification_email, send_password_reset_email, send_email_change_code, \
    send_password_recovery_code
from app.core.security import create_access_token, decode_token
from app.core.security import verify_password
from app_logging.logger import logger


class AuthService:
    def __init__(self, user_repository: UserRepository, db: AsyncSession):
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
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
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
            # Если не удалось отправить email, выводим ссылку в консоль для разработки
            logger.error(f"EMAIL SERVICE ERROR: Failed to send verification email to {user_data.email}")
            logger.error(f"VERIFICATION LINK FOR DEVELOPMENT: {verification_url}")
            logger.error("This is likely due to incorrect SMTP credentials or email service configuration.")
            logger.error("For development purposes, you can use the verification link above.")
            
            # Возвращаем дружелюбное сообщение пользователю
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Временные технические трудности с отправкой email. Пожалуйста, попробуйте позже.",
                    "error_type": "email_service_unavailable",
                    "verbose_error": "Email service configuration issue - check SMTP credentials"
                }
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
        if registration_token.expires_at < datetime.now(timezone.utc):
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

        # Проверяем, является ли пользователь сотрудником компании
        from app.api.authentication.repositories.employee_repository import EmployeeRepository
        employee_repository = EmployeeRepository(session=self.db)
        
        # Ищем сотрудника по email и ИНН
        employee = await employee_repository.get_employee_by_email_and_company(
            updated_user.email, 
            None  # Пока что ищем по email, потом найдем компанию
        )
        
        if employee:
            # Если найден сотрудник, привязываем пользователя к сотруднику
            await employee_repository.activate_employee(employee.id, updated_user.id)
            logger.info(f"Activated employee {employee.id} for user {updated_user.id}")
        else:
            # Если не найден сотрудник, создаем компанию по умолчанию (владелец)
            try:
                from app.api.company.repositories.company_repository import CompanyRepository
                company_repository = CompanyRepository(session=self.db)
                await company_repository.create_by_default(updated_user, user_data.inn)
                logger.info(f"Created default company for user {updated_user.id}")
            except Exception as e:
                logger.error(f"Failed to create default company for user {updated_user.id}: {str(e)}")
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
        if registration_token.expires_at < datetime.now(timezone.utc):
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

    async def authenticate_user_by_login(self, login: str, password: str) -> Optional[User]:
        """Authenticate user by email/phone and password"""
        logger.info(f"Attempting authentication for login: {login}")

        user = await self.user_repository.get_user_by_email_or_phone(login)
        if not user:
            logger.error(f"User not found for login: {login}")
            return None

        logger.info(f"User found: ID={user.id}, email={user.email}, phone={user.phone}")

        if not user.hashed_password:
            logger.error(f"User {user.id} has no password hash")
            return None

        if not verify_password(password, user.hashed_password):
            logger.error(f"Password verification failed for user {user.id}")
            return None

        logger.info(f"Authentication successful for user {user.id}")
        return User.model_validate(user)

    async def change_password(self, user_id: int, password_data: ChangePasswordRequest) -> bool:
        """Change user password"""
        # Get current user
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        success = await self.user_repository.update_user_password(user_id, password_data.new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )

        logger.info(f"Password changed for user {user_id}")
        return True

    async def request_password_reset(self, email: str) -> bool:
        """Request password reset"""
        # Check if user exists
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            # Don't reveal if user exists or not for security
            return True

        # Generate reset token
        import secrets
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        # Create reset token
        success = await self.user_repository.create_password_reset_token(email, token, expires_at)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create password reset token"
            )

        # Send reset email
        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        email_sent = await send_password_reset_email(email, reset_url)
        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email"
            )

        logger.info(f"Password reset requested for {email}")
        return True

    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """Confirm password reset"""
        # Get reset token
        reset_token = await self.user_repository.get_password_reset_token(token)
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        if reset_token.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token already used"
            )

        if reset_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token expired"
            )

        # Get user by email
        user = await self.user_repository.get_user_by_email(reset_token.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update password
        success = await self.user_repository.update_user_password(user.id, new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )

        # Mark token as used
        await self.user_repository.mark_password_reset_token_as_used(token)

        logger.info(f"Password reset completed for user {user.id}")
        return True

    async def request_email_change(self, user_id: int, email_data: ChangeEmailRequest) -> bool:
        """Request email change"""
        # Get current user
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify current password
        if not verify_password(email_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect"
            )

        # Check if new email already exists
        email_exists = await self.user_repository.check_email_exists(email_data.new_email)
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        # Generate confirmation code (6 digits)
        import random
        code = str(random.randint(100000, 999999))
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        # Create change token with code
        success = await self.user_repository.create_email_change_token(
            user_id, email_data.new_email, code, expires_at
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create email change token"
            )

        # Send confirmation code
        email_sent = await send_email_change_code(email_data.new_email, code)
        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email change confirmation"
            )

        logger.info(f"Email change code sent for user {user_id} to {email_data.new_email}")
        return True

    async def confirm_email_change(self, token: str) -> bool:
        """Confirm email change"""
        # Get change token
        change_token = await self.user_repository.get_email_change_token(token)
        if not change_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid change token"
            )

        if change_token.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Change token already used"
            )

        if change_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Change token expired"
            )

        # Get user
        user = await self.user_repository.get_user_by_id(change_token.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update email
        success = await self.user_repository.update_user_email(user.id, change_token.new_email)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update email"
            )

        # Mark token as used
        await self.user_repository.mark_email_change_token_as_used(token)

        logger.info(f"Email changed for user {user.id}")
        return True

    # Новые методы для восстановления пароля с кодами
    async def request_password_recovery(self, email: str) -> bool:
        """Request password recovery with code"""
        # Check if user exists
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            # Don't reveal if user exists or not for security
            return True

        # Generate 6-digit code
        import random
        code = str(random.randint(100000, 999999))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        # Create recovery code
        success = await self.user_repository.create_password_recovery_code(email, code, expires_at)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create password recovery code"
            )

        # Send recovery code email
        email_sent = await send_password_recovery_code(email, code)
        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password recovery code"
            )

        logger.info(f"Password recovery code sent to {email}")
        return True

    async def verify_password_recovery_code(self, email: str, code: str) -> bool:
        """Verify password recovery code"""
        # Get recovery code
        recovery_code = await self.user_repository.get_password_recovery_code(email, code)
        if not recovery_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recovery code"
            )

        if recovery_code.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recovery code expired"
            )

        logger.info(f"Password recovery code verified for {email}")
        return True

    async def reset_password_with_code(self, email: str, code: str, new_password: str) -> bool:
        """Reset password using recovery code"""
        logger.info(f"Starting password reset process for email: {email}")

        # Get recovery code
        recovery_code = await self.user_repository.get_password_recovery_code(email, code)
        if not recovery_code:
            logger.error(f"Invalid recovery code for email: {email}, code: {code}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recovery code"
            )

        logger.info(f"Recovery code found for email: {email}, expires at: {recovery_code.expires_at}")

        if recovery_code.expires_at < datetime.now(timezone.utc):
            logger.error(f"Recovery code expired for email: {email}, expires at: {recovery_code.expires_at}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recovery code expired"
            )

        # Get user by email
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            logger.error(f"User not found for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"User found: ID={user.id}, email={user.email}")

        # Update password
        success = await self.user_repository.update_user_password(user.id, new_password)
        if not success:
            logger.error(f"Failed to update password for user ID: {user.id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )

        logger.info(f"Password successfully updated for user ID: {user.id}")

        # Mark code as used
        mark_success = await self.user_repository.mark_password_recovery_code_as_used(email, code)
        if not mark_success:
            logger.warning(f"Failed to mark recovery code as used for email: {email}")
        else:
            logger.info(f"Recovery code marked as used for email: {email}")

        logger.info(f"Password reset completed successfully for user {user.id}")
        return True
