from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.models.user import User, RegistrationToken as DBRegistrationToken
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