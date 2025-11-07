#!/usr/bin/env python3
import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import AsyncSessionLocal
from sqlalchemy import text

async def set_passwords_sql():
    """Устанавливаем пароли через SQL"""
    async with AsyncSessionLocal() as db:
        try:
            # Устанавливаем пароль "password123" (хеш bcrypt)
            # Это хеш для пароля "password123"
            password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4VZJjKzKq2"
            
            # Обновляем пароль для владельца
            await db.execute(
                text("UPDATE users SET hashed_password = :password WHERE id = :user_id"),
                {"password": password_hash, "user_id": 5}
            )
            print("Установлен пароль для владельца (ID: 5)")
            
            # Обновляем пароль для сотрудника
            await db.execute(
                text("UPDATE users SET hashed_password = :password WHERE id = :user_id"),
                {"password": password_hash, "user_id": 6}
            )
            print("Установлен пароль для сотрудника (ID: 6)")
            
            await db.commit()
            print("Пароли установлены успешно!")
            print("Пароль для всех пользователей: password123")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(set_passwords_sql())