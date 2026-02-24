#!/usr/bin/env python3
"""
Создание тестового пользователя и компании в локальной БД.
Запуск из корня backend: python scripts/create_test_user.py
Или из корня проекта: docker compose -f docker-compose.dev.yml run --rm backend python scripts/create_test_user.py
"""
import asyncio
import os
import sys
from datetime import datetime, timezone

# Добавляем корень backend в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import User
from app.api.authentication.models.roles_positions import UserRole
from app.api.company.models.company import Company, TradeActivity, BusinessType
from app.core.security import get_password_hash


TEST_EMAIL = "test@localhost.dev"
TEST_PASSWORD = "test123456"
TEST_PHONE = "79001234567"
TEST_COMPANY_NAME = "Тестовая компания (локально)"
TEST_SLUG = "test-company-local"
TEST_INN = "770000000099"
TEST_KPP = "770001001"


async def main():
    async with AsyncSessionLocal() as session:
        # Проверяем, нет ли уже такого пользователя
        result = await session.execute(select(User).where(User.email == TEST_EMAIL))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Пользователь {TEST_EMAIL} уже существует (id={existing.id}, company_id={existing.company_id}).")
            return

        # Создаём компанию
        company = Company(
            name=TEST_COMPANY_NAME,
            slug=TEST_SLUG,
            type="ООО",
            trade_activity=TradeActivity.BOTH,
            business_type=BusinessType.BOTH,
            activity_type="Деятельность не указана",
            country="RU",
            federal_district="Центральный",
            region="Москва",
            city="Москва",
            full_name="ООО Тестовая компания",
            inn=TEST_INN,
            kpp=TEST_KPP,
            registration_date=datetime.now(timezone.utc).replace(tzinfo=None),
            legal_address="г. Москва, ул. Тестовая, д. 1",
            phone=TEST_PHONE,
            email=TEST_EMAIL,
            is_active=True,
        )
        session.add(company)
        await session.flush()

        # Создаём пользователя
        user = User(
            email=TEST_EMAIL,
            first_name="Тест",
            last_name="Тестов",
            patronymic="Тестович",
            phone=TEST_PHONE,
            position="owner",
            hashed_password=get_password_hash(TEST_PASSWORD),
            is_active=True,
            company_id=company.id,
            role=UserRole.OWNER,
            permissions='["view_statistics", "user_management", "chat", "company_edit", "products", "announcements", "purchases", "sales", "documents"]',
        )
        session.add(user)
        await session.commit()
        print(f"Создан тестовый пользователь: {TEST_EMAIL} / {TEST_PASSWORD}")
        print(f"  user_id={user.id}, company_id={company.id} ({company.name})")
        print("  Вход на localhost: http://localhost:8080/auth/login")


if __name__ == "__main__":
    asyncio.run(main())
