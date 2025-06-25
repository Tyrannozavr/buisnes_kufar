from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.models.user import User, RegistrationToken as DBRegistrationToken, PasswordResetToken, EmailChangeToken, PasswordRecoveryCode
from app.api.authentication.schemas.user import UserCreateStep1, UserCreateStep2, UserInDB, RegistrationToken
from app.core.security import get_password_hash, verify_password
from app_logging.logger import logger


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user_step1(self, user_data: UserCreateStep1) -> UserInDB:
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            patronymic=user_data.patronymic,
            phone=user_data.phone,
            is_active=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserInDB.model_validate(user)

    async def update_user_step2(self, user: User, user_data: UserCreateStep2) -> UserInDB:
        user.inn = user_data.inn
        user.position = user_data.position
        user.is_active = True
        user.hashed_password = get_password_hash(user_data.password)
        user.updated_at = datetime.utcnow()
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserInDB.model_validate(user)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_inn(self, inn: str) -> Optional[User]:
        """Get user by INN"""
        result = await self.session.execute(
            select(User).where(User.inn == inn)
        )
        return result.scalar_one_or_none()

    async def create_registration_token(self, email: str, token: str, expires_at: datetime) -> RegistrationToken:
        db_token = DBRegistrationToken(
            email=email,
            token=token,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_used=False
        )
        self.session.add(db_token)
        try:
            await self.session.commit()
            await self.session.refresh(db_token)
            return RegistrationToken.model_validate(db_token)
        except Exception as e:
            logger.error(f"Error creating token for {email}: {str(e)}")
            await self.session.rollback()
            raise

    async def get_registration_token(self, token: str) -> Optional[RegistrationToken]:
        result = await self.session.execute(
            select(DBRegistrationToken).where(DBRegistrationToken.token == token)
        )
        db_token = result.scalar_one_or_none()
        return RegistrationToken.model_validate(db_token) if db_token else None

    async def mark_token_as_used(self, token: str) -> bool:
        result = await self.session.execute(
            update(DBRegistrationToken)
            .where(DBRegistrationToken.token == token)
            .values(is_used=True)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_user_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        hashed_password = get_password_hash(new_password)
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(hashed_password=hashed_password, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount > 0

    async def update_user_email(self, user_id: int, new_email: str) -> bool:
        """Update user email"""
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(email=new_email, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount > 0

    async def create_password_reset_token(self, email: str, token: str, expires_at: datetime) -> bool:
        """Create password reset token"""
        db_token = PasswordResetToken(
            email=email,
            token=token,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_used=False
        )
        self.session.add(db_token)
        try:
            await self.session.commit()
            await self.session.refresh(db_token)
            return True
        except Exception as e:
            logger.error(f"Error creating password reset token for {email}: {str(e)}")
            await self.session.rollback()
            return False

    async def get_password_reset_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get password reset token"""
        result = await self.session.execute(
            select(PasswordResetToken).where(PasswordResetToken.token == token)
        )
        return result.scalar_one_or_none()

    async def mark_password_reset_token_as_used(self, token: str) -> bool:
        """Mark password reset token as used"""
        result = await self.session.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.token == token)
            .values(is_used=True)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def create_email_change_token(self, user_id: int, new_email: str, token: str, expires_at: datetime) -> bool:
        """Create email change token"""
        db_token = EmailChangeToken(
            user_id=user_id,
            new_email=new_email,
            token=token,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_used=False
        )
        self.session.add(db_token)
        try:
            await self.session.commit()
            await self.session.refresh(db_token)
            return True
        except Exception as e:
            logger.error(f"Error creating email change token for user {user_id}: {str(e)}")
            await self.session.rollback()
            return False

    async def get_email_change_token(self, token: str) -> Optional[EmailChangeToken]:
        """Get email change token"""
        result = await self.session.execute(
            select(EmailChangeToken).where(EmailChangeToken.token == token)
        )
        return result.scalar_one_or_none()

    async def mark_email_change_token_as_used(self, token: str) -> bool:
        """Mark email change token as used"""
        result = await self.session.execute(
            update(EmailChangeToken)
            .where(EmailChangeToken.token == token)
            .values(is_used=True)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def check_email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None

    # Методы для работы с кодами восстановления пароля
    async def create_password_recovery_code(self, email: str, code: str, expires_at: datetime) -> bool:
        """Create password recovery code"""
        # Удаляем старые коды для этого email
        await self.session.execute(
            update(PasswordRecoveryCode)
            .where(PasswordRecoveryCode.email == email)
            .values(is_used=True)
        )
        
        db_code = PasswordRecoveryCode(
            email=email,
            code=code,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_used=False
        )
        self.session.add(db_code)
        try:
            await self.session.commit()
            await self.session.refresh(db_code)
            return True
        except Exception as e:
            logger.error(f"Error creating password recovery code for {email}: {str(e)}")
            await self.session.rollback()
            return False

    async def get_password_recovery_code(self, email: str, code: str) -> Optional[PasswordRecoveryCode]:
        """Get password recovery code"""
        result = await self.session.execute(
            select(PasswordRecoveryCode)
            .where(
                PasswordRecoveryCode.email == email,
                PasswordRecoveryCode.code == code,
                PasswordRecoveryCode.is_used == False
            )
        )
        return result.scalar_one_or_none()

    async def mark_password_recovery_code_as_used(self, email: str, code: str) -> bool:
        """Mark password recovery code as used"""
        result = await self.session.execute(
            update(PasswordRecoveryCode)
            .where(
                PasswordRecoveryCode.email == email,
                PasswordRecoveryCode.code == code
            )
            .values(is_used=True)
        )
        await self.session.commit()
        return result.rowcount > 0 