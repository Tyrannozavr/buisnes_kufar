#!/usr/bin/env python3
"""
Тестовые пользователи и сделки для проверки счёта (этапы 1–2).

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
from app.api.products.models.product import Product, ProductType
from app.api.purchases.models import Order, UnitOfMeasurement
from app.api.purchases.repositories import DealRepository
from app.api.purchases.schemas import DealCreate, OrderItemCreate
from app.core.security import get_password_hash
from app.db.base import AsyncSessionLocal

TEST_PASSWORD = "123456"

# Канонические тестовые аккаунты этапа 2
SELLER_USER = {
    "email": "seller@gmail.com",
    "first_name": "Сергей",
    "last_name": "Поставщик",
    "patronymic": "Петрович",
    "phone": "79001234001",
}

BUYER_USER = {
    "email": "buyer@gmail.com",
    "first_name": "Анна",
    "last_name": "Покупатель",
    "patronymic": "Ивановна",
    "phone": "79001234002",
}

# Алиас разработчика (привязывается к компании поставщика)
PRIMARY_EMAILS = (
    "dmitiry40647274@gmail.com",
    "dmitriy40647274@gmail.com",
)

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
    "description": "Тестовый поставщик (seller@gmail.com) — этап 2",
    "country": "Россия",
    "federal_district": "Центральный федеральный округ",
    "region": "Москва",
    "city": "Москва",
    "index": "101000",
    "legal_address": "101000, г. Москва, ул. Поставщика, д. 1",
    "production_address": "101000, г. Москва, ул. Складская, д. 2",
    "phone": "+79001234001",
    "email": "seller@gmail.com",
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
    "description": "Тестовый покупатель (buyer@gmail.com) — этап 2",
    "country": "Россия",
    "federal_district": "Центральный федеральный округ",
    "region": "Москва",
    "city": "Москва",
    "index": "109012",
    "legal_address": "109012, г. Москва, ул. Покупателя, д. 10",
    "production_address": "109012, г. Москва, ул. Покупателя, д. 10",
    "phone": "+79001234002",
    "email": "buyer@gmail.com",
    "vat_rate": 0,
}

SELLER_OFFICIAL = {
    "position": "Генеральный директор",
    "full_name": "Поставщик Сергей Петрович",
    "is_base": True,
    "base_document": "Устав",
    "base_document_name": "Устав",
}

UNITS_DATA = [
    ("Штука", "шт", "796"),
    ("Бобина", "боб", "616"),
    ("Лист", "л.", "625"),
    ("Набор", "набор", "704"),
    ("Пара", "пар", "715"),
    ("Рулон", "рул", "736"),
    ("Миллиметр", "мм", "003"),
    ("Сантиметр", "см", "004"),
    ("Метр", "м", "006"),
    ("Километр", "км", "008"),
    ("Погонный метр", "пог. м", "018"),
    ("Квадратный миллиметр", "мм²", "050"),
    ("Квадратный сантиметр", "см²", "051"),
    ("Квадратный метр", "м²", "055"),
    ("Квадратный километр", "км²", "061"),
    ("Гектар", "га", "059"),
    ("Миллилитр", "мл", "111"),
    ("Литр", "л", "112"),
    ("Кубический миллиметр", "мм³", "110"),
    ("Кубический сантиметр", "см³", "111"),
    ("Кубический метр", "м³", "113"),
    ("Миллиграмм", "мг", "161"),
    ("Грамм", "г", "163"),
    ("Килограмм", "кг", "166"),
    ("Тонна", "т", "168"),
]

DEAL_MAIN_COMMENTS = "Этап 2 — тест ОКЕИ (заказ + счёт)"
DEAL_NO_BILL_COMMENTS = "Этап 2 — сделка без счёта (createBill)"

# Каталог поставщика для §2.2 checkout (товар + услуга → два заказа)
CHECKOUT_CATALOG = [
    {
        "slug": "test-checkout-bolt-m8",
        "name": "Болт М8 (checkout)",
        "article": "CHK-BOLT-M8",
        "type": ProductType.GOOD,
        "price": 15.00,
        "unit_of_measurement": "шт",
        "description": "Тестовый товар для checkout §2.2",
    },
    {
        "slug": "test-checkout-montazh",
        "name": "Монтаж оборудования (checkout)",
        "article": "CHK-SVC-MONT",
        "type": ProductType.SERVICE,
        "price": 5000.00,
        "unit_of_measurement": "усл",
        "description": "Тестовая услуга для checkout §2.2",
    },
]


async def ensure_units(session) -> None:
    count = (
        await session.execute(select(UnitOfMeasurement))
    ).scalars().all()
    if count:
        print(f"  units EXISTS: {len(count)} записей")
        return

    for name, symbol, code in UNITS_DATA:
        session.add(UnitOfMeasurement(name=name, symbol=symbol, code=code))
    await session.flush()
    print(f"  units CREATED: {len(UNITS_DATA)} записей ОКЕИ")


async def upsert_company(session, data: dict) -> Company:
    company = (
        await session.execute(select(Company).where(Company.slug == data["slug"]))
    ).scalar_one_or_none()

    if not company and data.get("inn"):
        company = (
            await session.execute(select(Company).where(Company.inn == data["inn"]))
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
        print(f"  user LINKED: {email} → company_id={seller_company_id}")


async def ensure_catalog_products(session, company_id: int) -> list[Product]:
    """Товар и услуга поставщика для проверки checkout (§2.2)."""
    products: list[Product] = []
    for spec in CHECKOUT_CATALOG:
        product = (
            await session.execute(select(Product).where(Product.slug == spec["slug"]))
        ).scalar_one_or_none()

        payload = {
            **spec,
            "images": [],
            "characteristics": [],
            "is_hidden": False,
            "is_deleted": False,
            "company_id": company_id,
        }

        if product:
            for key, value in payload.items():
                setattr(product, key, value)
            print(f"  catalog UPDATED: {product.name} ({product.slug})")
        else:
            product = Product(**payload)
            session.add(product)
            await session.flush()
            print(f"  catalog CREATED: {product.name} ({product.slug})")

        products.append(product)

    return products


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
        f"sum={order.total_amount}"
    )
    return order


async def main() -> None:
    print("=== Тестовые данные: этап 2 (ОКЕИ, seller/buyer) ===\n")

    async with AsyncSessionLocal() as session:
        print("Справочник ОКЕИ:")
        await ensure_units(session)

        print("\nПоставщик:")
        seller_company = await upsert_company(session, SELLER_COMPANY)
        await upsert_user(session, SELLER_USER, seller_company.id)
        await link_primary_users(session, seller_company.id)
        await ensure_seller_official(session, seller_company.id)

        print("\nКаталог для checkout §2.2:")
        catalog = await ensure_catalog_products(session, seller_company.id)

        print("\nПокупатель:")
        buyer_company = await upsert_company(session, BUYER_COMPANY)
        await upsert_user(session, BUYER_USER, buyer_company.id)

        await session.commit()

        print("\nСделка 1 (ОКЕИ: шт→796, кг→166):")
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
                    product_name="Профиль алюминиевый",
                    product_article="ALU-PROF-01",
                    quantity=25,
                    unit_of_measurement="кг",
                    price=180.00,
                ),
            ],
        )

        print("\nСделка 2 (без счёта):")
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
            ],
        )

    good = next(p for p in catalog if p.type == ProductType.GOOD)
    service = next(p for p in catalog if p.type == ProductType.SERVICE)

    print("\n--- Готово ---")
    print(f"Пароль для всех тестовых: {TEST_PASSWORD}")
    print(f"Поставщик:  {SELLER_USER['email']}  ({SELLER_COMPANY['name']})")
    print(f"Покупатель: {BUYER_USER['email']}  ({BUYER_COMPANY['name']})")
    print(f"\nСделка 1: id={order_main.id}, заказ {order_main.seller_order_number}")
    print(f"Сделка 2: id={order_no_bill.id}, заказ {order_no_bill.seller_order_number}")
    print("\n§2.1 ОКЕИ — seller@gmail.com → Продажи → сделка 1 → Заказ (ОКЕИ 796, 166)")
    print("\n§2.2 Checkout — buyer@gmail.com:")
    print("  1) http://localhost:8080/auth/login")
    print(f"  2) В корзину: /catalog/items/{good.slug} и /catalog/items/{service.slug}")
    print("  3) Корзина → Оформить заказ → /checkout")
    print("  4) Два блока: товары и услуги → «Подтвердить» в каждом")
    print("  5) Закупки — два новых заказа; seller@gmail.com → Продажи + чат с уведомлением")


if __name__ == "__main__":
    asyncio.run(main())
