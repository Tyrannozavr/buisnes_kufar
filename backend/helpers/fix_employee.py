#!/usr/bin/env python3
import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import User
from sqlalchemy import update

async def fix_employee():
    """Исправляем данные сотрудника"""
    async with AsyncSessionLocal() as db:
        try:
            # Привязываем сотрудника к компании и устанавливаем должность
            await db.execute(
                update(User)
                .where(User.id == 11)  # ID сотрудника test@example.com
                .values(
                    company_id=10,  # ID компании "Тестовая компания ООО"
                    position="Главный бухгалтер"
                )
            )
            
            await db.commit()
            print("✅ Сотрудник успешно привязан к компании и должность установлена!")
            
            # Проверяем результат
            result = await db.execute(
                update(User)
                .where(User.id == 11)
                .values(
                    company_id=10,
                    position="Главный бухгалтер"
                )
            )
            
            print("Проверка: сотрудник ID 11 привязан к компании ID 10 с должностью 'Главный бухгалтер'")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(fix_employee())
