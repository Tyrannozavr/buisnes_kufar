#!/usr/bin/env python3
import asyncio
import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import User, RegistrationToken, PasswordRecoveryCode
from app.api.authentication.models.employee import Employee, EmployeePermission
from app.api.company.models.company import Company
from app.api.company.models.official import CompanyOfficial

async def delete_all_data():
    """Удаляем все данные из базы"""
    async with AsyncSessionLocal() as db:
        try:
            print("🗑️ Удаляем все данные...")
            
            # Удаляем в правильном порядке (сначала зависимые таблицы)
            await db.execute(EmployeePermission.__table__.delete())
            await db.execute(Employee.__table__.delete())
            await db.execute(CompanyOfficial.__table__.delete())
            await db.execute(RegistrationToken.__table__.delete())
            await db.execute(PasswordRecoveryCode.__table__.delete())
            await db.execute(User.__table__.delete())
            await db.execute(Company.__table__.delete())
            
            await db.commit()
            print("✅ Все данные удалены успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка при удалении данных: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(delete_all_data())
