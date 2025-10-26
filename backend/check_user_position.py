#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import User
from sqlalchemy import select

async def check_user_position():
    async with AsyncSessionLocal() as db:
        try:
            user = await db.scalar(select(User).where(User.email == "owner@testcompany.ru"))
            if user:
                print(f"Пользователь: {user.email}")
                print(f"ID: {user.id}")
                print(f"Должность: {user.position}")
                print(f"Роль: {user.role}")
                print(f"Компания ID: {user.company_id}")
            else:
                print("Пользователь не найден")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_user_position())
