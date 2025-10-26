#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import User
from app.api.authentication.models.roles_positions import Position
from sqlalchemy import update

async def update_user_position():
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(
                update(User)
                .where(User.email == "owner@testcompany.ru")
                .values(position=Position.OWNER.value)
            )
            await db.commit()
            print("✅ Должность пользователя обновлена на 'owner'")
        except Exception as e:
            print(f"Ошибка: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(update_user_position())
