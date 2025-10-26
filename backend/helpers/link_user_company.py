#!/usr/bin/env python3
import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import User
from app.api.company.models.company import Company
from sqlalchemy import update

async def link_user_to_company():
    """Привязываем пользователя к компании"""
    async with AsyncSessionLocal() as db:
        try:
            # Привязываем пользователя ID 7 к компании ID 9
            await db.execute(
                update(User)
                .where(User.id == 7)
                .values(company_id=9)
            )
            
            await db.commit()
            print("✅ Пользователь успешно привязан к компании!")
            
            # Проверяем результат
            result = await db.execute(
                update(User)
                .where(User.id == 7)
                .values(company_id=9)
            )
            
            print("Проверка: пользователь ID 7 привязан к компании ID 9")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(link_user_to_company())
