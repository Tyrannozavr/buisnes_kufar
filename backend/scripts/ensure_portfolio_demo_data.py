#!/usr/bin/env python3
"""
Демо-данные для скриншотов портфолио (реалистичные компании, каталог, сделки, счета).

Запуск:
  docker compose -f docker-compose.dev.yml exec backend poetry run python scripts/ensure_portfolio_demo_data.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.api.authentication.models.roles_positions import UserRole
from app.api.authentication.models.user import User
from app.api.authentication.permissions import PermissionManager
from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.api.company.models.official import CompanyOfficial
from app.api.products.models.product import Product, ProductType
from app.api.purchases.deal_bill_defaults import DEFAULT_BILL_DELIVERY_TERMS_DAYS, DEFAULT_BILL_PAYMENT_TERMS_DAYS
from app.api.purchases.models import Order, OrderType, UnitOfMeasurement
from app.api.purchases.repositories import DealRepository
from app.api.purchases.schemas import (
    BillUpdateInDeal,
    CompanyOfficialInDealResponse,
    DealCreate,
    DealUpdate,
    OrderItemCreate,
    OrderTypeSchema,
)
from app.core.security import get_password_hash
from app.db.base import AsyncSessionLocal

PASSWORD = "123456"
PORTFOLIO_TAG = "portfolio-demo"

ADDITIONAL_INFO_BILL = (
    "Внимание!\n"
    "Оплата данного счета означает согласие с условиями поставки товара.\n"
    "Уведомление об оплате обязательно, в противном случае не гарантируется наличие товара на складе.\n"
    "Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом, при наличии доверенности и паспорта."
)

SELLER = {
    "email": "seller@gmail.com",
    "first_name": "Алексей",
    "last_name": "Королёв",
    "patronymic": "Сергеевич",
    "phone": "74951234567",
    "company": {
        "name": "ООО «СтройМеталл Плюс»",
        "slug": "stroymetall-plus",
        "full_name": "Общество с ограниченной ответственностью «СтройМеталл Плюс»",
        "inn": "7708123456",
        "ogrn": "1177746123456",
        "kpp": "770801001",
        "type": "ООО",
        "trade_activity": TradeActivity.SELLER,
        "business_type": BusinessType.GOODS,
        "activity_type": "Оптовая торговля металлопрокатом и крепежом",
        "description": "Поставка металлопроката, крепежа и комплектующих для строительства и промышленности.",
        "country": "Россия",
        "federal_district": "Центральный федеральный округ",
        "region": "Москва",
        "city": "Москва",
        "index": "115432",
        "legal_address": "115432, г. Москва, ул. Электролитный проезд, д. 3, стр. 2",
        "production_address": "142718, Московская обл., г. Видное, промзона «Южная», д. 12",
        "phone": "+7 (495) 123-45-67",
        "email": "zakaz@stroymetall-plus.ru",
        "current_account_number": "40702810938000123456",
        "bic": "044525225",
        "correspondent_bank_account": "30101810400000000225",
        "bank_name": "ПАО Сбербанк",
        "vat_rate": 20,
    },
    "official": {
        "position": "Генеральный директор",
        "full_name": "Королёв Алексей Сергеевич",
        "is_base": True,
        "base_document": "Устав",
        "base_document_name": "Устав",
    },
}

BUYERS = [
    {
        "email": "buyer@gmail.com",
        "first_name": "Елена",
        "last_name": "Волкова",
        "patronymic": "Андреевна",
        "phone": "74959876543",
        "company": {
            "name": "ООО «ТехноСнаб»",
            "slug": "tehnosnab-moscow",
            "full_name": "Общество с ограниченной ответственностью «ТехноСнаб»",
            "inn": "7709234567",
            "ogrn": "1187746234567",
            "kpp": "770901001",
            "type": "ООО",
            "trade_activity": TradeActivity.SELLER,
            "business_type": BusinessType.GOODS,
            "activity_type": "Снабжение строительных объектов",
            "description": "Комплексное снабжение строительных и монтажных организаций.",
            "country": "Россия",
            "federal_district": "Центральный федеральный округ",
            "region": "Москва",
            "city": "Москва",
            "index": "109012",
            "legal_address": "109012, г. Москва, ул. Никольская, д. 10, оф. 305",
            "production_address": "109012, г. Москва, ул. Никольская, д. 10, оф. 305",
            "phone": "+7 (495) 987-65-43",
            "email": "snab@tehnosnab.ru",
            "current_account_number": "40702810500000987654",
            "bic": "044525974",
            "correspondent_bank_account": "30101810145250000974",
            "bank_name": "АО «Тинькофф Банк»",
            "vat_rate": 20,
        },
    },
    {
        "email": "portfolio-buyer2@demo.ru",
        "first_name": "Дмитрий",
        "last_name": "Орлов",
        "patronymic": "Игоревич",
        "phone": "78125551234",
        "company": {
            "name": "ООО «СевЗапМонтаж»",
            "slug": "sevzap-montazh",
            "full_name": "Общество с ограниченной ответственностью «СевЗапМонтаж»",
            "inn": "7801345678",
            "ogrn": "1197846345678",
            "kpp": "780101001",
            "type": "ООО",
            "trade_activity": TradeActivity.SELLER,
            "business_type": BusinessType.GOODS,
            "activity_type": "Монтаж металлоконструкций",
            "description": "Монтаж и поставка металлоконструкций для промышленных объектов.",
            "country": "Россия",
            "federal_district": "Северо-Западный федеральный округ",
            "region": "Санкт-Петербург",
            "city": "Санкт-Петербург",
            "index": "196006",
            "legal_address": "196006, г. Санкт-Петербург, Московский пр., д. 97, лит. А",
            "production_address": "196006, г. Санкт-Петербург, Московский пр., д. 97, лит. А",
            "phone": "+7 (812) 555-12-34",
            "email": "zakaz@sevzap-montazh.ru",
            "current_account_number": "40702810900000111222",
            "bic": "044030653",
            "correspondent_bank_account": "30101810000000000653",
            "bank_name": "Банк «Санкт-Петербург»",
            "vat_rate": 20,
        },
    },
]

CATALOG = [
    {
        "slug": "bolt-din933-m12x50",
        "name": "Болт DIN 933 М12×50, класс прочности 8.8",
        "article": "SM-BOLT-M12-50",
        "type": ProductType.GOOD,
        "price": 18.50,
        "unit_of_measurement": "шт",
        "description": "Высокопрочный болт с полной резьбой, оцинкованный.",
    },
    {
        "slug": "nut-hex-m12-8",
        "name": "Гайка шестигранная М12, класс 8",
        "article": "SM-NUT-M12-8",
        "type": ProductType.GOOD,
        "price": 6.20,
        "unit_of_measurement": "шт",
        "description": "Гайка DIN 934, оцинкованная.",
    },
    {
        "slug": "profile-alu-40x40",
        "name": "Профиль алюминиевый 40×40 мм, 6 м",
        "article": "SM-ALU-40X40",
        "type": ProductType.GOOD,
        "price": 2450.00,
        "unit_of_measurement": "шт",
        "description": "Алюминиевый профиль для каркасных конструкций.",
    },
    {
        "slug": "sheet-steel-3mm",
        "name": "Лист стальной горячекатаный 3 мм, 1500×6000",
        "article": "SM-SHEET-3MM",
        "type": ProductType.GOOD,
        "price": 48500.00,
        "unit_of_measurement": "л.",
        "description": "Ст3сп, толщина 3 мм.",
    },
    {
        "slug": "angle-50x50x5",
        "name": "Уголок стальной 50×50×5 мм, 6 м",
        "article": "SM-ANGLE-50",
        "type": ProductType.GOOD,
        "price": 4200.00,
        "unit_of_measurement": "шт",
        "description": "Горячекатаный уголок, ГОСТ 8509-93.",
    },
    {
        "slug": "channel-10p",
        "name": "Швеллер 10П, 12 м",
        "article": "SM-CH-10P",
        "type": ProductType.GOOD,
        "price": 18700.00,
        "unit_of_measurement": "шт",
        "description": "Стальной швеллер для металлоконструкций.",
    },
    {
        "slug": "rebar-a500s-12",
        "name": "Арматура А500С Ø12 мм",
        "article": "SM-ARM-12",
        "type": ProductType.GOOD,
        "price": 62.00,
        "unit_of_measurement": "кг",
        "description": "Арматурная сталь для железобетонных конструкций.",
    },
    {
        "slug": "montazh-metall",
        "name": "Монтаж металлоконструкций",
        "article": "SM-SVC-MONT",
        "type": ProductType.SERVICE,
        "price": 85000.00,
        "unit_of_measurement": "усл",
        "description": "Монтаж и сборка металлоконструкций на объекте заказчика.",
    },
    {
        "slug": "delivery-moscow",
        "name": "Доставка по Москве и МО",
        "article": "SM-SVC-DEL",
        "type": ProductType.SERVICE,
        "price": 12000.00,
        "unit_of_measurement": "усл",
        "description": "Доставка товара собственным транспортом.",
    },
]

DEALS = [
    {
        "key": "001",
        "buyer_slug": "tehnosnab-moscow",
        "deal_type": OrderType.GOODS,
        "days_ago": 45,
        "with_bill": True,
        "items": [
            ("SM-BOLT-M12-50", 500),
            ("SM-NUT-M12-8", 500),
        ],
    },
    {
        "key": "002",
        "buyer_slug": "tehnosnab-moscow",
        "deal_type": OrderType.GOODS,
        "days_ago": 38,
        "with_bill": True,
        "items": [
            ("SM-SHEET-3MM", 4),
            ("SM-ANGLE-50", 20),
        ],
    },
    {
        "key": "003",
        "buyer_slug": "tehnosnab-moscow",
        "deal_type": OrderType.GOODS,
        "days_ago": 30,
        "with_bill": True,
        "items": [
            ("SM-CH-10P", 6),
            ("SM-ARM-12", 1200),
        ],
    },
    {
        "key": "004",
        "buyer_slug": "tehnosnab-moscow",
        "deal_type": OrderType.GOODS,
        "days_ago": 22,
        "with_bill": True,
        "items": [
            ("SM-ALU-40X40", 15),
        ],
    },
    {
        "key": "005",
        "buyer_slug": "tehnosnab-moscow",
        "deal_type": OrderType.GOODS,
        "days_ago": 14,
        "with_bill": False,
        "items": [
            ("SM-BOLT-M12-50", 200),
            ("SM-NUT-M12-8", 200),
        ],
    },
    {
        "key": "006",
        "buyer_slug": "tehnosnab-moscow",
        "deal_type": OrderType.SERVICES,
        "days_ago": 10,
        "with_bill": True,
        "items": [
            ("SM-SVC-MONT", 1),
        ],
    },
    {
        "key": "007",
        "buyer_slug": "sevzap-montazh",
        "deal_type": OrderType.GOODS,
        "days_ago": 28,
        "with_bill": True,
        "items": [
            ("SM-CH-10P", 10),
            ("SM-ANGLE-50", 30),
        ],
    },
    {
        "key": "008",
        "buyer_slug": "sevzap-montazh",
        "deal_type": OrderType.GOODS,
        "days_ago": 18,
        "with_bill": True,
        "items": [
            ("SM-SHEET-3MM", 8),
            ("SM-ARM-12", 2500),
        ],
    },
    {
        "key": "009",
        "buyer_slug": "sevzap-montazh",
        "deal_type": OrderType.SERVICES,
        "days_ago": 7,
        "with_bill": True,
        "items": [
            ("SM-SVC-MONT", 2),
            ("SM-SVC-DEL", 1),
        ],
    },
    {
        "key": "010",
        "buyer_slug": "tehnosnab-moscow",
        "deal_type": OrderType.GOODS,
        "days_ago": 5,
        "with_bill": True,
        "items": [
            ("SM-BOLT-M12-50", 1000),
            ("SM-NUT-M12-8", 1000),
            ("SM-ALU-40X40", 8),
        ],
    },
    {
        "key": "011",
        "buyer_slug": "sevzap-montazh",
        "deal_type": OrderType.GOODS,
        "days_ago": 3,
        "with_bill": True,
        "items": [
            ("SM-BOLT-M12-50", 300),
            ("SM-CH-10P", 4),
        ],
    },
    {
        "key": "012",
        "buyer_slug": "tehnosnab-moscow",
        "deal_type": OrderType.SERVICES,
        "days_ago": 1,
        "with_bill": True,
        "items": [
            ("SM-SVC-DEL", 2),
        ],
    },
]


async def ensure_units(session) -> None:
    existing = (await session.execute(select(UnitOfMeasurement))).scalars().all()
    if existing:
        return
    defaults = [
        ("Штука", "шт", "796"),
        ("Килограмм", "кг", "166"),
        ("Лист", "л.", "625"),
        ("Услуга", "усл", "876"),
    ]
    for name, symbol, code in defaults:
        session.add(UnitOfMeasurement(name=name, symbol=symbol, code=code))
    await session.flush()


async def upsert_company(session, data: dict) -> Company:
    company = (
        await session.execute(select(Company).where(Company.slug == data["slug"]))
    ).scalar_one_or_none()
    payload = {**data, "registration_date": datetime.now(timezone.utc).replace(tzinfo=None), "is_active": True}
    if company:
        for key, value in payload.items():
            setattr(company, key, value)
    else:
        company = Company(**payload)
        session.add(company)
        await session.flush()
    return company


async def upsert_user(session, spec: dict, company_id: int) -> User:
    user = (await session.execute(select(User).where(User.email == spec["email"]))).scalar_one_or_none()
    if user:
        user.first_name = spec["first_name"]
        user.last_name = spec["last_name"]
        user.patronymic = spec.get("patronymic")
        user.phone = spec["phone"]
        user.hashed_password = get_password_hash(PASSWORD)
        user.is_active = True
        user.company_id = company_id
        user.role = UserRole.OWNER
        user.position = "owner"
        user.permissions = PermissionManager.set_permissions_for_role(UserRole.OWNER)
    else:
        user = User(
            email=spec["email"],
            first_name=spec["first_name"],
            last_name=spec["last_name"],
            patronymic=spec.get("patronymic"),
            phone=spec["phone"],
            position="owner",
            hashed_password=get_password_hash(PASSWORD),
            is_active=True,
            company_id=company_id,
            role=UserRole.OWNER,
            permissions=PermissionManager.set_permissions_for_role(UserRole.OWNER),
        )
        session.add(user)
        await session.flush()
    return user


async def ensure_official(session, company_id: int, data: dict) -> CompanyOfficial:
    official = (
        await session.execute(
            select(CompanyOfficial).where(
                CompanyOfficial.company_id == company_id,
                CompanyOfficial.full_name == data["full_name"],
            )
        )
    ).scalar_one_or_none()
    if official:
        for key, value in data.items():
            setattr(official, key, value)
    else:
        official = CompanyOfficial(company_id=company_id, **data)
        session.add(official)
        await session.flush()
    return official


async def ensure_catalog(session, company_id: int) -> dict[str, Product]:
    by_article: dict[str, Product] = {}
    for spec in CATALOG:
        product = (
            await session.execute(select(Product).where(Product.slug == spec["slug"]))
        ).scalar_one_or_none()
        payload = {**spec, "images": [], "characteristics": [], "is_hidden": False, "is_deleted": False, "company_id": company_id}
        if product:
            for key, value in payload.items():
                setattr(product, key, value)
        else:
            product = Product(**payload)
            session.add(product)
            await session.flush()
        by_article[spec["article"]] = product
    return by_article


async def ensure_deal(
    session,
    *,
    buyer_id: int,
    seller_id: int,
    spec: dict,
    articles: dict[str, Product],
) -> Order:
    comment = f"{PORTFOLIO_TAG}:{spec['key']}"
    existing = (
        await session.execute(
            select(Order)
            .where(
                Order.buyer_company_id == buyer_id,
                Order.seller_company_id == seller_id,
                Order.comments == comment,
            )
            .order_by(Order.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    items = [OrderItemCreate(article=article, quantity=qty) for article, qty in spec["items"]]
    repo = DealRepository(session)
    order = await repo.create_order(
        DealCreate(
            seller_company_id=seller_id,
            deal_type=OrderTypeSchema(spec["deal_type"].value),
            comments=comment,
            items=items,
        ),
        buyer_id,
    )

    created = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=spec["days_ago"])
    order.created_at = created
    order.updated_at = created
    await session.commit()
    await session.refresh(order)
    return order


async def fill_bill(session, order: Order, seller_id: int, official: CompanyOfficial) -> None:
    repo = DealRepository(session)
    bill_date = order.created_at + timedelta(days=1)
    await repo.assign_bill(order.id, seller_id, bill_date)

    bill_update = BillUpdateInDeal(
        number=order.seller_order_number,
        reason=f"Оплата по счёту № {order.seller_order_number} от {bill_date.strftime('%d.%m.%Y')} г.",
        payment_terms=DEFAULT_BILL_PAYMENT_TERMS_DAYS,
        payment_terms_contract=DEFAULT_BILL_PAYMENT_TERMS_DAYS,
        delivery_terms_contract=DEFAULT_BILL_DELIVERY_TERMS_DAYS,
        additional_info=ADDITIONAL_INFO_BILL,
        officials=[
            CompanyOfficialInDealResponse(
                id=official.id,
                company_id=seller_id,
                full_name=official.full_name,
                position=official.position,
                is_base=official.is_base,
                base_document=official.base_document or "",
                base_document_name=official.base_document_name or "",
            )
        ],
    )
    await repo.update_order(
        order.id,
        DealUpdate(bill=bill_update, amount_with_vat_rate=True),
        seller_id,
        apply_date_fields=True,
    )


async def main() -> None:
    print("=== Портфолио: реалистичные демо-данные ===\n")

    async with AsyncSessionLocal() as session:
        await ensure_units(session)

        seller_company = await upsert_company(session, SELLER["company"])
        seller_user = await upsert_user(session, SELLER, seller_company.id)
        seller_official = await ensure_official(session, seller_company.id, SELLER["official"])
        articles = await ensure_catalog(session, seller_company.id)

        buyers_by_slug: dict[str, Company] = {}
        for buyer_spec in BUYERS:
            company = await upsert_company(session, buyer_spec["company"])
            await upsert_user(session, buyer_spec, company.id)
            buyers_by_slug[buyer_spec["company"]["slug"]] = company

        await session.commit()

        print(f"Поставщик: {seller_company.name} (id={seller_company.id})")
        for slug, company in buyers_by_slug.items():
            print(f"Покупатель: {company.name} (slug={slug})")
        print(f"Каталог: {len(articles)} позиций\n")

        created_deals: list[Order] = []
        for spec in DEALS:
            buyer = buyers_by_slug[spec["buyer_slug"]]
            order = await ensure_deal(
                session,
                buyer_id=buyer.id,
                seller_id=seller_company.id,
                spec=spec,
                articles=articles,
            )
            if spec["with_bill"] and not order.bill_date:
                await fill_bill(session, order, seller_company.id, seller_official)
            created_deals.append(order)
            bill_label = "счёт" if order.bill_date else "без счёта"
            print(f"  сделка {spec['key']}: №{order.seller_order_number}, {bill_label}, {order.total_amount:,.2f} ₽")

    print("\n--- Готово для скриншотов ---")
    print(f"URL: http://localhost:8080")
    print(f"Пароль для всех аккаунтов: {PASSWORD}")
    print(f"\nПоставщик (Продажи, счета, каталог):")
    print(f"  {SELLER['email']} — {SELLER['company']['name']}")
    print(f"\nПокупатель 1 (Закупки):")
    print(f"  {BUYERS[0]['email']} — {BUYERS[0]['company']['name']}")
    print(f"\nПокупатель 2 (второй контрагент в таблице):")
    print(f"  {BUYERS[1]['email']} — {BUYERS[1]['company']['name']}")
    print("\nСтраницы для скриншотов:")
    print("  /auth/login")
    print("  /catalog")
    print("  /profile/sales — вкладка «Товары»")
    print("  /profile/editor?dealId=<id>&role=seller#bill — счёт на оплату")
    print("  /profile/editor?dealId=<id>&role=seller#order — заказ")
    if created_deals:
        sample = next((d for d in created_deals if d.bill_date), created_deals[0])
        print(f"\nПример сделки со счётом: dealId={sample.id}, заказ №{sample.seller_order_number}")


if __name__ == "__main__":
    asyncio.run(main())
