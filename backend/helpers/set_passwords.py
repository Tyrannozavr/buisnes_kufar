#!/usr/bin/env python3
import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import User
from sqlalchemy import select, update
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def set_passwords():
    """Устанавливаем пароли для тестовых пользователей"""
    async with AsyncSessionLocal() as db:
        try:
            # Устанавливаем пароль для владельца
            owner_password = pwd_context.hash("1")
            await db.execute(
                update(User)
                .where(User.id == 5)
                .values(hashed_password=owner_password)
            )
            print("Установлен пароль для владельца (ID: 5)")
            
            # Устанавливаем пароль для сотрудника
            employee_password = pwd_context.hash("1")
            await db.execute(
                update(User)
                .where(User.id == 6)
                .values(hashed_password=employee_password)
            )
            print("Установлен пароль для сотрудника (ID: 6)")
            
            await db.commit()
            print("Пароли установлены успешно!")
            print("Пароль для всех пользователей: 1")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(set_passwords())
