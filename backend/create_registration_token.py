#!/usr/bin/env python3
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import RegistrationToken as DBRegistrationToken
from sqlalchemy import select

async def create_registration_token(email: str, token_value: str, user_id: int = None):
    async with AsyncSessionLocal() as db:
        try:
            # Удаляем старые токены для этого email
            await db.execute(
                DBRegistrationToken.__table__.delete().where(DBRegistrationToken.email == email)
            )
            await db.commit()

            expires_at = datetime.now(timezone.utc) + timedelta(days=1)
            registration_token = DBRegistrationToken(
                email=email,
                token=token_value,
                user_id=user_id,
                expires_at=expires_at,
                is_used=False,
                created_at=datetime.now(timezone.utc)
            )
            db.add(registration_token)
            await db.commit()
            await db.refresh(registration_token)
            print(f"✅ Создан токен регистрации: {registration_token.token}")
            print(f"Email: {registration_token.email}")
            print(f"Срок действия: {registration_token.expires_at}")
        except Exception as e:
            print(f"Ошибка при создании токена регистрации: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(create_registration_token("owner@testcompany.ru", "test_token_owner"))
