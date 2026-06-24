#!/usr/bin/env python3
"""
Тестовые пользователи и сделка для проверки счёта (этап 1).

Запуск (dev Docker):
  docker compose -f docker-compose.dev.yml exec backend poetry run python scripts/ensure_schet_test_users.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.api.authentication.models.roles_positions import UserRole
from app.api.authentication.models.user import User
from app.api.authentication.permissions import PermissionManager
from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.api.company.models.official import CompanyOfficial
from app.api.purchases.models import Order
from app.api.purchases.repositories import DealRepository
from app.api.purchases.schemas import DealCreate, OrderItemCreate
from app.core.security import get_password_hash
from app.db.base import AsyncSessionLocal

TEST_PASSWORD = "123456"

# Канонический email + опечатка из ensure_local_admin.py (dmitriy vs dmitiry)
PRIMARY_EMAILS = (
    "dmitiry40647274@gmail.com",
    "dmitriy40647274@gmail.com",
)

PRIMARY_USER = {
    "email": PRIMARY_EMAILS[0],
    "first_name": "Дмитрий",
    "last_name": "Тестов",
    "patronymic": "Сергеевич",
    "phone": "79001234001",
}

# Контрагент-покупатель
COUNTERPARTY_USER = {
    "email": "seller@gmail.com",
    "first_name": "Иван",
    "last_name": "Покупатель",
    "patronymic": "Иванович",
    "phone": "79001234002",
}

SELLER_COMPANY = {
    "name": "ООО Поставщик Тест",
    "slug": "test-supplier-dmitry",
    "full_name": "Общество с ограниченной ответственностью «Поставщик Тест»",
    "inn": "7707083893",
    "ogrn": "1027700132195",
    "kpp": "770701001",
    "type": "ООО",
    "trade_activity": TradeActivity.SELLER,
    "business_type": BusinessType.GOODS,
    "activity_type": "Производство товаров",
    "description": "Тестовый поставщик для проверки счёта (этап 1)",
    "country": "Россия",
    "federal_district": "Центральный федеральный округ",
    "region": "Москва",
    "city": "Москва",
    "index": "101000",
    "legal_address": "101000, г. Москва, ул. Поставщика, д. 1",
    "production_address": "101000, г. Москва, ул. Складская, д. 2",
    "phone": "+79001234001",
    "email": "dmitiry40647274@gmail.com",
    "current_account_number": "40702810100000001234",
    "bic": "044525225",
    "correspondent_bank_account": "30101810400000000225",
    "bank_name": "ПАО Сбербанк",
    "vat_rate": 20,
}

BUYER_COMPANY = {
    "name": "ООО Покупатель Тест",
    "slug": "test-buyer-counterparty",
    "full_name": "Общество с ограниченной ответственностью «Покупатель Тест»",
    "inn": "7707083894",
    "ogrn": "1027700132196",
    "kpp": "770701002",
    "type": "ООО",
    "trade_activity": TradeActivity.BUYER,
    "business_type": BusinessType.GOODS,
    "activity_type": "Торговля",
    "description": "Тестовый покупатель-контрагент (seller@gmail.com)",
    "country": "Россия",
    "federal_district": "Центральный федеральный округ",
    "region": "Москва",
    "city": "Москва",
    "index": "109012",
    "legal_address": "109012, г. Москва, ул. Покупателя, д. 10",
    "production_address": "109012, г. Москва, ул. Покупателя, д. 10",
    "phone": "+79001234002",
    "email": "seller@gmail.com",
    "vat_rate": 0,
}

SELLER_OFFICIAL = {
    "position": "Генеральный директор",
    "full_name": "Тестов Дмитрий Сергеевич",
    "is_base": True,
    "base_document": "Устав",
    "base_document_name": "Устав",
}


async def upsert_company(session, data: dict) -> Company:
    company = (
        await session.execute(select(Company).where(Company.slug == data["slug"]))
    ).scalar_one_or_none()

    payload = {
        **data,
        "registration_date": datetime.now(timezone.utc).replace(tzinfo=None),
        "is_active": True,
    }

    if company:
        for key, value in payload.items():
            setattr(company, key, value)
        print(f"  company UPDATED: {company.name} (id={company.id})")
    else:
        company = Company(**payload)
        session.add(company)
        await session.flush()
        print(f"  company CREATED: {company.name} (id={company.id})")

    return company


async def upsert_user(session, spec: dict, company_id: int) -> User:
    user = (
        await session.execute(select(User).where(User.email == spec["email"]))
    ).scalar_one_or_none()

    if user:
        user.first_name = spec["first_name"]
        user.last_name = spec["last_name"]
        user.patronymic = spec.get("patronymic")
        user.phone = spec["phone"]
        user.hashed_password = get_password_hash(TEST_PASSWORD)
        user.is_active = True
        user.company_id = company_id
        user.role = UserRole.OWNER
        user.position = "owner"
        user.permissions = PermissionManager.set_permissions_for_role(UserRole.OWNER)
        print(f"  user UPDATED: {user.email} (id={user.id})")
    else:
        user = User(
            email=spec["email"],
            first_name=spec["first_name"],
            last_name=spec["last_name"],
            patronymic=spec.get("patronymic"),
            phone=spec["phone"],
            position="owner",
            hashed_password=get_password_hash(TEST_PASSWORD),
            is_active=True,
            company_id=company_id,
            role=UserRole.OWNER,
            permissions=PermissionManager.set_permissions_for_role(UserRole.OWNER),
        )
        session.add(user)
        await session.flush()
        print(f"  user CREATED: {user.email} (id={user.id})")

    return user


async def link_primary_users(session, seller_company_id: int) -> None:
    """Привязать все варианты email разработчика к компании-поставщику (есть сделка в Продажах)."""
    for email in PRIMARY_EMAILS:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        if not user:
            continue
        user.company_id = seller_company_id
        user.hashed_password = get_password_hash(TEST_PASSWORD)
        user.is_active = True
        if user.role != UserRole.ADMIN:
            user.role = UserRole.OWNER
            user.permissions = PermissionManager.set_permissions_for_role(UserRole.OWNER)
        print(f"  user LINKED: {email} → company_id={seller_company_id} (role={user.role})")


async def ensure_seller_official(session, company_id: int) -> None:
    existing = (
        await session.execute(
            select(CompanyOfficial).where(
                CompanyOfficial.company_id == company_id,
                CompanyOfficial.full_name == SELLER_OFFICIAL["full_name"],
            )
        )
    ).scalar_one_or_none()

    if existing:
        for key, value in SELLER_OFFICIAL.items():
            setattr(existing, key, value)
        print("  official UPDATED")
        return

    session.add(CompanyOfficial(company_id=company_id, **SELLER_OFFICIAL))
    print("  official CREATED")


async def ensure_deal(
    session,
    buyer_company_id: int,
    seller_company_id: int,
    *,
    comments: str,
    items: list[OrderItemCreate],
) -> Order:
    existing = (
        await session.execute(
            select(Order)
            .where(
                Order.buyer_company_id == buyer_company_id,
                Order.seller_company_id == seller_company_id,
                Order.comments == comments,
                Order.status == "Активная",
            )
            .order_by(Order.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    if existing:
        print(
            f"  deal EXISTS: id={existing.id}, "
            f"seller_order={existing.seller_order_number}, "
            f"bill={'да' if existing.bill_date else 'нет'}"
        )
        return existing

    repo = DealRepository(session)
    deal_data = DealCreate(
        seller_company_id=seller_company_id,
        comments=comments,
        items=items,
    )
    order = await repo.create_order(deal_data, buyer_company_id)
    await session.commit()
    await session.refresh(order)
    print(
        f"  deal CREATED: id={order.id}, "
        f"seller_order={order.seller_order_number}, "
        f"buyer_order={order.buyer_order_number}, "
        f"sum={order.total_amount}, "
        f"bill={'да' if order.bill_date else 'нет'}"
    )
    return order


DEAL_MAIN_COMMENTS = "Тестовая сделка для этапа 1 (счёт)"
DEAL_NO_BILL_COMMENTS = "Тест §1.3 — счёт не создан (для createBill)"


async def main() -> None:
    print("=== Тестовые пользователи для счёта (этап 1) ===\n")

    async with AsyncSessionLocal() as session:
        print("Поставщик (основной пользователь):")
        seller_company = await upsert_company(session, SELLER_COMPANY)
        await upsert_user(session, PRIMARY_USER, seller_company.id)
        await link_primary_users(session, seller_company.id)
        await ensure_seller_official(session, seller_company.id)

        print("\nПокупатель (контрагент):")
        buyer_company = await upsert_company(session, BUYER_COMPANY)
        await upsert_user(session, COUNTERPARTY_USER, buyer_company.id)

        await session.commit()

        print("\nСделка 1 (основная, может быть со счётом):")
        order_main = await ensure_deal(
            session,
            buyer_company.id,
            seller_company.id,
            comments=DEAL_MAIN_COMMENTS,
            items=[
                OrderItemCreate(
                    product_name="Болт М8×40",
                    product_article="BOLT-M8-40",
                    quantity=100,
                    unit_of_measurement="шт",
                    price=12.50,
                ),
                OrderItemCreate(
                    product_name="Гайка М8",
                    product_article="NUT-M8",
                    quantity=100,
                    unit_of_measurement="шт",
                    price=5.00,
                ),
            ],
        )

        print("\nСделка 2 (для теста §1.3 — без счёта):")
        order_no_bill = await ensure_deal(
            session,
            buyer_company.id,
            seller_company.id,
            comments=DEAL_NO_BILL_COMMENTS,
            items=[
                OrderItemCreate(
                    product_name="Шайба M8",
                    product_article="WASH-M8",
                    quantity=200,
                    unit_of_measurement="шт",
                    price=2.00,
                ),
                OrderItemCreate(
                    product_name="Винт M6×20",
                    product_article="SCR-M6-20",
                    quantity=50,
                    unit_of_measurement="шт",
                    price=8.00,
                ),
            ],
        )

    print("\n--- Готово ---")
    print(f"Пароль для всех тестовых: {TEST_PASSWORD}")
    print(f"\nВход поставщика (счёт): {PRIMARY_EMAILS[0]}")
    print(f"  (алиас локального admin: {PRIMARY_EMAILS[1]})")
    print(f"Контрагент-покупатель:     {COUNTERPARTY_USER['email']}")
    print(f"\nСделка 1: id={order_main.id}, заказ {order_main.seller_order_number}")
    print(f"Сделка 2: id={order_no_bill.id}, заказ {order_no_bill.seller_order_number} — без счёта")
    print("§1.3: Продажи → сделка 2 → «Создать счет» → на бланке только № и дата → «Заполнить данными»")


if __name__ == "__main__":
    asyncio.run(main())
