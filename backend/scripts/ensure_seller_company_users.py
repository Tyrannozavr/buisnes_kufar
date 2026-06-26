#!/usr/bin/env python3
"""Владельцы для компаний-поставщиков без пользователей (нужно для чатов)."""
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
from app.api.purchases.models import Order
from app.core.security import get_password_hash

DEFAULT_PASSWORD = "Demo2026!"


async def main() -> None:
    async with AsyncSessionLocal() as session:
        seller_ids_subq = select(Order.seller_company_id).distinct()
        result = await session.execute(
            select(Company)
            .where(Company.id.in_(seller_ids_subq))
            .where(
                ~Company.id.in_(
                    select(User.company_id).where(User.company_id.is_not(None))
                )
            )
        )
        companies = result.scalars().all()

        if not companies:
            print("Все компании-поставщики уже имеют пользователей.")
            return

        for company in companies:
            email = (company.email or f"owner-company-{company.id}@tradesynergy.ru").strip().lower()
            existing = (
                await session.execute(select(User).where(User.email == email))
            ).scalar_one_or_none()
            if existing:
                existing.company_id = company.id
                existing.role = UserRole.OWNER
                existing.is_active = True
                existing.permissions = PermissionManager.set_permissions_for_role(UserRole.OWNER)
                print(f"LINKED {email} -> {company.name} (id={company.id})")
                continue

            user = User(
                email=email,
                first_name="Владелец",
                last_name=company.name[:50] if company.name else "Компания",
                phone=company.phone or f"7900{company.id:07d}"[-10:],
                position="owner",
                hashed_password=get_password_hash(DEFAULT_PASSWORD),
                is_active=True,
                company_id=company.id,
                role=UserRole.OWNER,
                permissions=PermissionManager.set_permissions_for_role(UserRole.OWNER),
            )
            session.add(user)
            print(f"CREATED {email} -> {company.name} (id={company.id})")

        await session.commit()

    print(f"\nПароль для новых владельцев: {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
