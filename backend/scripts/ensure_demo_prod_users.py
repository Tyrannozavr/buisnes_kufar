#!/usr/bin/env python3
"""Демо-пользователи для проверки на продакшене."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import User
from app.api.authentication.models.roles_positions import UserRole
from app.api.authentication.permissions import PermissionManager
from app.api.company.models.company import Company
from app.core.security import get_password_hash

DEMO_PASSWORD = "Demo2026!"

DEMO_USERS = [
    {
        "email": "demo-buyer@tradesynergy.ru",
        "first_name": "Демо",
        "last_name": "Покупатель",
        "phone": "79001111101",
        "company_slug": "shveianeia",
    },
    {
        "email": "demo-seller@tradesynergy.ru",
        "first_name": "Демо",
        "last_name": "Поставщик",
        "phone": "79001111102",
        "company_slug": "tkani",
    },
    {
        "email": "demo-owner@tradesynergy.ru",
        "first_name": "Демо",
        "last_name": "Владелец",
        "phone": "79001111103",
        "company_slug": "novaia-kompaniia",
    },
]


async def main() -> None:
    async with AsyncSessionLocal() as session:
        for spec in DEMO_USERS:
            company = (
                await session.execute(
                    select(Company).where(Company.slug == spec["company_slug"])
                )
            ).scalar_one_or_none()
            if not company:
                print(f"SKIP {spec['email']}: company {spec['company_slug']} not found")
                continue

            user = (
                await session.execute(select(User).where(User.email == spec["email"]))
            ).scalar_one_or_none()

            if user:
                user.hashed_password = get_password_hash(DEMO_PASSWORD)
                user.is_active = True
                user.role = UserRole.OWNER
                user.company_id = company.id
                user.permissions = PermissionManager.set_permissions_for_role(UserRole.OWNER)
                print(f"UPDATED {spec['email']} -> company {company.name} (id={company.id})")
            else:
                user = User(
                    email=spec["email"],
                    first_name=spec["first_name"],
                    last_name=spec["last_name"],
                    phone=spec["phone"],
                    position="owner",
                    hashed_password=get_password_hash(DEMO_PASSWORD),
                    is_active=True,
                    company_id=company.id,
                    role=UserRole.OWNER,
                    permissions=PermissionManager.set_permissions_for_role(UserRole.OWNER),
                )
                session.add(user)
                print(f"CREATED {spec['email']} -> company {company.name} (id={company.id})")

        await session.commit()

    print(f"\nПароль для всех: {DEMO_PASSWORD}")
    print("Вход: https://tradesynergy.ru/auth/login")


if __name__ == "__main__":
    asyncio.run(main())
