from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.authentication.models.user import User, RegistrationToken as DBRegistrationToken
from app.api.authentication.schemas.user import UserCreate, UserInDB, RegistrationToken
from app.core.security import get_password_hash, verify_password
from app_logging.logger import logger


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> UserInDB:
        hashed_password = get_password_hash(user_data.password)
        user = User(
            id=uuid4(),
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **user_data.model_dump(exclude={'password'})
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserInDB.model_validate(user)

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        return UserInDB.model_validate(user) if user else None

    async def get_user_by_id(self, user_id: UUID) -> Optional[UserInDB]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return UserInDB.model_validate(user) if user else None

    async def verify_user(self, user_id: UUID) -> bool:
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_verified=True, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount > 0

    async def create_registration_token(self, email: str, registration_data: Dict[str, Any]) -> RegistrationToken:
        token = DBRegistrationToken(
            email=email,
            registration_data=registration_data,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        self.session.add(token)
        try:
            await self.session.commit()
            await self.session.refresh(token)
            return RegistrationToken.model_validate(token)
        except Exception as e:
            logger.error(f"Error creating token for {email}: {str(e)}")
            await self.session.rollback()
            raise

    async def get_registration_token(self, token: UUID) -> Optional[RegistrationToken]:
        result = await self.session.execute(
            select(DBRegistrationToken).where(DBRegistrationToken.token == token)
        )
        db_token = result.scalar_one_or_none()
        return RegistrationToken.model_validate(db_token) if db_token else None

    async def mark_token_as_used(self, token: UUID) -> bool:
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
        if not verify_password(password, user.hashed_password):
            return None
        return user 