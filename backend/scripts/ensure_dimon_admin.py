#!/usr/bin/env python3
"""
Создать или обновить пользователя-администратора компании (UserRole.ADMIN).
Запуск из каталога backend: python scripts/ensure_dimon_admin.py
Docker: docker compose -f docker-compose.dev.yml run --rm --entrypoint "" backend poetry run python scripts/ensure_dimon_admin.py
"""
import asyncio
import os
import random
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import User
from app.api.authentication.models.roles_positions import UserRole
from app.api.authentication.permissions import PermissionManager
from app.api.company.models.company import Company, TradeActivity, BusinessType
from app.core.security import get_password_hash

ADMIN_EMAIL = "dimon@gmail.com"
ADMIN_PASSWORD = "12345678"
ADMIN_PHONE = "79000000001"
COMPANY_NAME = "Компания администратора (dimon)"


async def _unique_slug(session, base: str) -> str:
    slug = base
    for _ in range(20):
        r = await session.execute(select(Company.id).where(Company.slug == slug))
        if r.scalar_one_or_none() is None:
            return slug
        slug = f"{base}-{random.randint(1000, 99999)}"
    return f"{base}-{random.randint(100000, 999999)}"


async def _unique_inn(session) -> str:
    for _ in range(50):
        inn = f"{random.randint(1000000000, 9999999999)}"
        r = await session.execute(select(Company.id).where(Company.inn == inn))
        if r.scalar_one_or_none() is None:
            return inn
    return f"{random.randint(1000000000, 9999999999)}"


async def main() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
        user = result.scalar_one_or_none()

        if user:
            user.hashed_password = get_password_hash(ADMIN_PASSWORD)
            user.role = UserRole.ADMIN
            user.permissions = PermissionManager.set_permissions_for_role(UserRole.ADMIN)
            user.is_active = True
            await session.commit()
            print(f"Обновлён пользователь {ADMIN_EMAIL}: роль admin, пароль установлен.")
            print(f"  user_id={user.id}, company_id={user.company_id}")
            return

        slug = await _unique_slug(session, "dimon-admin-company")
        inn = await _unique_inn(session)

        company = Company(
            name=COMPANY_NAME,
            slug=slug,
            type="ООО",
            trade_activity=TradeActivity.BOTH,
            business_type=BusinessType.BOTH,
            activity_type="Администрирование",
            country="Российская Федерация",
            federal_district="Центральный",
            region="Москва",
            city="Москва",
            full_name=f'ООО "{COMPANY_NAME}"',
            inn=inn,
            kpp="770001001",
            registration_date=datetime.now(timezone.utc).replace(tzinfo=None),
            legal_address="г. Москва",
            phone=ADMIN_PHONE,
            email=ADMIN_EMAIL,
            is_active=True,
        )
        session.add(company)
        await session.flush()

        user = User(
            email=ADMIN_EMAIL,
            first_name="Димон",
            last_name="Админ",
            phone=ADMIN_PHONE,
            position="admin",
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            is_active=True,
            company_id=company.id,
            role=UserRole.ADMIN,
            permissions=PermissionManager.set_permissions_for_role(UserRole.ADMIN),
        )
        session.add(user)
        await session.commit()
        print(f"Создан администратор: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"  user_id={user.id}, company_id={company.id}, slug={slug}")


if __name__ == "__main__":
    asyncio.run(main())
