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
from app.api.company.models.company import BusinessType, Company, TradeActivity, CompanyRelationType
from app.api.company.models.official import CompanyOfficial
from app.api.company.repositories.company_relations_repository import CompanyRelationsRepository
from app.api.company.schemas.company import CompanyRelationCreate
from app.api.products.models.product import Product, ProductType
from app.api.purchases.models import (
    Order,
    UnitOfMeasurement,
    ContractConditionTemplateType,
)
from app.api.purchases.repositories import DealRepository
from app.api.purchases.repositories.company_contract import CompanyContractRepository
from app.api.purchases.repositories.contract_condition_template import (
    ContractConditionTemplateRepository,
)
from app.api.purchases.schemas import DealCreate, OrderItemCreate, OrderTypeSchema
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
    "trade_activity": TradeActivity.SELLER,
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

BUYER_NO_CONTRACT_COMPANY = {
    "name": "ООО Покупатель Без Договора",
    "slug": "test-buyer-no-contract",
    "full_name": "Общество с ограниченной ответственностью «Покупатель Без Договора»",
    "inn": "7707083895",
    "ogrn": "1027700132197",
    "kpp": "770701003",
    "type": "ООО",
    "trade_activity": TradeActivity.SELLER,
    "business_type": BusinessType.GOODS,
    "activity_type": "Торговля",
    "description": "Покупатель без договоров с поставщиком — этап 3.1",
    "country": "Россия",
    "federal_district": "Центральный федеральный округ",
    "region": "Москва",
    "city": "Москва",
    "index": "109013",
    "legal_address": "109013, г. Москва, ул. Новая, д. 3",
    "production_address": "109013, г. Москва, ул. Новая, д. 3",
    "phone": "+79001234003",
    "email": "buyer-no-contract@gmail.com",
    "vat_rate": 0,
}

# --- ТЗ_15 §5.6: перевозчик / экспедитор ---
CARRIER_USER = {
    "email": "carrier@gmail.com",
    "first_name": "Игорь",
    "last_name": "Перевозчик",
    "patronymic": "Сергеевич",
    "phone": "79001234011",
}

FORWARDER_USER = {
    "email": "forwarder@gmail.com",
    "first_name": "Ольга",
    "last_name": "Экспедитор",
    "patronymic": "Николаевна",
    "phone": "79001234012",
}

CARRIER_COMPANY = {
    "name": "ООО Перевозчик Тест",
    "slug": "test-carrier-tz15",
    "full_name": "Общество с ограниченной ответственностью «Перевозчик Тест»",
    "inn": "7707083911",
    "ogrn": "1027700132211",
    "kpp": "770701011",
    "type": "ООО",
    "trade_activity": TradeActivity.CARRIER,
    "business_type": BusinessType.SERVICES,
    "activity_type": "Автоперевозки",
    "description": "Тестовый перевозчик (carrier@gmail.com) — ТЗ_15 этап 5",
    "country": "Россия",
    "federal_district": "Центральный федеральный округ",
    "region": "Москва",
    "city": "Москва",
    "index": "109020",
    "legal_address": "109020, г. Москва, ул. Транспортная, д. 1",
    "production_address": "109020, г. Москва, ул. Транспортная, д. 1",
    "phone": "+79001234011",
    "email": "carrier@gmail.com",
    "vat_rate": 20,
}

FORWARDER_COMPANY = {
    "name": "ООО Экспедитор Тест",
    "slug": "test-forwarder-tz15",
    "full_name": "Общество с ограниченной ответственностью «Экспедитор Тест»",
    "inn": "7707083912",
    "ogrn": "1027700132212",
    "kpp": "770701012",
    "type": "ООО",
    "trade_activity": TradeActivity.FORWARDER,
    "business_type": BusinessType.SERVICES,
    "activity_type": "Экспедирование грузов",
    "description": "Тестовый экспедитор (forwarder@gmail.com) — ТЗ_15 этап 5",
    "country": "Россия",
    "federal_district": "Центральный федеральный округ",
    "region": "Москва",
    "city": "Москва",
    "index": "109021",
    "legal_address": "109021, г. Москва, ул. Логистическая, д. 2",
    "production_address": "109021, г. Москва, ул. Логистическая, д. 2",
    "phone": "+79001234012",
    "email": "forwarder@gmail.com",
    "vat_rate": 20,
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
DEAL_STAGE31_CONTRACTS_COMMENTS = "Этап 3.1 — без счёта, диалог выбора договора"
DEAL_NO_CONTRACT_COMMENTS = "Этап 3.1 — сделка без счёта, контрагент без договоров"
DEAL_SERVICES_COMMENTS = "Этап 4.6 — услуговая сделка без счёта"

TEMPLATE_NAME_SUPPLIER = "Стандартный, доставка Поставщика"
TEMPLATE_NAME_BUYER = "Стандартный, доставка Покупателя"

# Seed-тексты с плейсхолдерами для редактора шаблонов (§4.4)
_CONTRACT_TERMS_SUPPLIER = """\
Основные условия настоящего договора-счета № {{ НОМЕР_СЧЕТА }} от {{ ДАТА }} г.
1. \tПредметом настоящего Счета-договора является поставка товарно-материальных ценностей (далее - "товар").
2. \tОплата настоящего Счета-договора означает согласие Покупателя с условиями оплаты и поставки товара.\t
3. \tНастоящий Счет-договор действителен в течение {{ СРОК_ОПЛАТЫ }} рабочих дней от даты его составления включительно. При отсутствии оплаты в указанный срок настоящий Счет-договор признается недействительным.
4. \tПоставщик обязан доставить оплаченный товар и передать его Покупателю в течение {{ СРОК_ПОСТАВКИ }} рабочих дней с момента зачисления оплаты на расчетный счет
5. \tОплаченный товар доставляется Покупателю силами ПОСТАВЩИКА
6. \tОплата Счета-договора третьими лицами (сторонами), а также неполная (частичная) оплата Счета-договора не допускается. Покупатель не имеет права производить выборочную оплату позиций счета и требовать поставку товара по выбранным позициям.
7. \tПоставщик вправе не выполнять поставку товара до зачисления оплаты на расчетный счет.
8. \tПокупатель обязан принять оплаченный товар лично или через уполномоченного представителя. Передача товара осуществляется при предъявлении документа, удостоверяющего личность, и/или доверенности оформленной в установленном порядке.
9. \tПодписание Покупателем или его уполномоченным представителем товарной накладной означает согласие Покупателя с комплектностью и надлежащим качеством товара."""

_CONTRACT_TERMS_BUYER = """\
Основные условия настоящего договора-счета № {{ НОМЕР_СЧЕТА }} от {{ ДАТА }} г.
1. \tПредметом настоящего Счета-договора является поставка товарно-материальных ценностей (далее - "товар").
2. \tОплата настоящего Счета-договора означает согласие Покупателя с условиями оплаты и поставки товара.\t
3. \tНастоящий Счет-договор действителен в течение {{ СРОК_ОПЛАТЫ }} рабочих дней от даты его составления включительно. При отсутствии оплаты в указанный срок настоящий Счет-договор признается недействительным.
4. \tПоставщик обязан доставить оплаченный товар и передать его Покупателю в течение {{ СРОК_ПОСТАВКИ }} рабочих дней с момента зачисления оплаты на расчетный счет
5. \tОплаченный товар доставляется Покупателю силами ПОКУПАТЕЛЯ
6. \tОплата Счета-договора третьими лицами (сторонами), а также неполная (частичная) оплата Счета-договора не допускается. Покупатель не имеет права производить выборочную оплату позиций счета и требовать поставку товара по выбранным позициям.
7. \tПоставщик вправе не выполнять поставку товара до зачисления оплаты на расчетный счет.
8. \tПокупатель обязан принять оплаченный товар лично или через уполномоченного представителя. Передача товара осуществляется при предъявлении документа, удостоверяющего личность, и/или доверенности оформленной в установленном порядке.
9. \tПодписание Покупателем или его уполномоченным представителем товарной накладной означает согласие Покупателя с комплектностью и надлежащим качеством товара."""

# Оферта: срок поставки не используется (только {{ СРОК_ОПЛАТЫ }})
_OFFER_TERMS_SUPPLIER = """\
1.\tПредметом настоящего счета-оферты является поставка товара по перечню изделий поставщиком покупателю.
2.\tПодписывая настоящий счет-оферту, Покупатель дает согласие на то, что товар надлежащего качества обмену и возврату не подлежит.
3.\tОсмотр товара Покупателем происходит при получении. Покупатель проводит обследование единиц продукции на предмет отсутствия брака и дефектов, проверяет комплектность партии. При обнаружении недочетов Покупателем составляется акт. При отсутствии акта Поставщик претензии не принимает.
4.\tПокупатель обязуется оплатить товар на условиях 100% предоплаты в сумме, указанной в счете, в течение {{ СРОК_ОПЛАТЫ }} рабочих дней по указанным реквизитам.
5.\tОплаченный товар доставляется Покупателю силами ПОСТАВЩИКА со склада Поставщика, расположенного по адресу: {{ АДРЕС_ПРОИЗВОДСТВА_ПОСТАВЩИКА}}.
6.\tПосле получения товара Покупатель обязан подписать Товарную накладную."""

_OFFER_TERMS_BUYER = """\
1.\tПредметом настоящего счета-оферты является поставка товара по перечню изделий поставщиком покупателю.
2.\tПодписывая настоящий счет-оферту, Покупатель дает согласие на то, что товар надлежащего качества обмену и возврату не подлежит.
3.\tОсмотр товара Покупателем происходит при получении. Покупатель проводит обследование единиц продукции на предмет отсутствия брака и дефектов, проверяет комплектность партии. При обнаружении недочетов Покупателем составляется акт. При отсутствии акта Поставщик претензии не принимает.
4.\tПокупатель обязуется оплатить товар на условиях 100% предоплаты в сумме, указанной в счете, в течение {{ СРОК_ОПЛАТЫ }} рабочих дней по указанным реквизитам.
5.\tОплаченный товар доставляется Покупателю силами ПОКУПАТЕЛЯ со склада Поставщика, расположенного по адресу: {{ АДРЕС_ПРОИЗВОДСТВА_ПОСТАВЩИКА}}.
6.\tПосле получения товара Покупатель обязан подписать Товарную накладную."""

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


async def ensure_contract_condition_templates(session, seller_company_id: int) -> None:
    """Seed шаблонов условий счёт-договора / оферты (§4.4)."""
    repo = ContractConditionTemplateRepository(session)
    specs = [
        (
            ContractConditionTemplateType.BILL_CONTRACT.value,
            TEMPLATE_NAME_SUPPLIER,
            _CONTRACT_TERMS_SUPPLIER,
            True,
        ),
        (
            ContractConditionTemplateType.BILL_CONTRACT.value,
            TEMPLATE_NAME_BUYER,
            _CONTRACT_TERMS_BUYER,
            False,
        ),
        (
            ContractConditionTemplateType.BILL_OFFER.value,
            TEMPLATE_NAME_SUPPLIER,
            _OFFER_TERMS_SUPPLIER,
            True,
        ),
        (
            ContractConditionTemplateType.BILL_OFFER.value,
            TEMPLATE_NAME_BUYER,
            _OFFER_TERMS_BUYER,
            False,
        ),
    ]
    for template_type, name, content_text, is_default in specs:
        await repo.upsert_seed(
            company_id=seller_company_id,
            template_type=template_type,
            name=name,
            content_text=content_text,
            is_default=is_default,
        )
    await session.commit()
    print(
        f"  contract_condition_templates: 4 шт. "
        f"(2×bill_contract + 2×bill_offer) company_id={seller_company_id}"
    )


async def ensure_bill_date_if_missing(session, order: Order) -> Order:
    """Если номер счёта есть, а даты нет — проставить дату (иначе «от — г.» и пустая {{ ДАТА }} в DOC)."""
    if order is None:
        return order
    if order.bill_number and not order.bill_date:
        order.bill_date = order.created_at or datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(order)
        print(
            f"  bill_date FIXED: order id={order.id} "
            f"№{order.bill_number} → {order.bill_date.strftime('%d.%m.%Y')}"
        )
    return order


async def ensure_deal(
    session,
    buyer_company_id: int,
    seller_company_id: int,
    *,
    comments: str,
    items: list[OrderItemCreate],
    deal_type: OrderTypeSchema = OrderTypeSchema.GOODS,
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
            f"type={existing.deal_type}, "
            f"bill={'да' if existing.bill_date else 'нет'}"
        )
        return existing

    repo = DealRepository(session)
    deal_data = DealCreate(
        seller_company_id=seller_company_id,
        deal_type=deal_type,
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
        f"type={order.deal_type}, "
        f"sum={order.total_amount}"
    )
    return order


async def ensure_company_relations(
    session,
    seller_company_id: int,
    buyer_company_id: int,
    buyer_no_contract_id: int,
    carrier_company_id: int | None = None,
) -> None:
    repo = CompanyRelationsRepository(session)
    pairs = [
        (buyer_company_id, CompanyRelationType.BUYER),
        (buyer_company_id, CompanyRelationType.PARTNER),
        (buyer_no_contract_id, CompanyRelationType.BUYER),
        (buyer_no_contract_id, CompanyRelationType.PARTNER),
    ]
    if carrier_company_id:
        pairs.extend(
            [
                (carrier_company_id, CompanyRelationType.CARRIER),
                (carrier_company_id, CompanyRelationType.PARTNER),
            ]
        )
    for related_id, relation_type in pairs:
        await repo.ensure_relation(seller_company_id, related_id, relation_type)
    await session.commit()
    print(
        f"  company relations: seller={seller_company_id} "
        f"buyers=[{buyer_company_id}, {buyer_no_contract_id}]"
        + (f" carrier={carrier_company_id}" if carrier_company_id else "")
    )


async def ensure_company_contracts(
    session,
    seller_company_id: int,
    buyer_company_id: int,
) -> None:
    repo = CompanyContractRepository(session)
    contracts = [
        ("00015", datetime(2025, 3, 1)),
        ("00027", datetime(2025, 6, 15)),
    ]
    for number, date in contracts:
        await repo.upsert_contract(
            seller_company_id=seller_company_id,
            buyer_company_id=buyer_company_id,
            number=number,
            date=date,
        )
    await session.commit()
    print(f"  company contracts: {len(contracts)} шт. seller={seller_company_id} buyer={buyer_company_id}")


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

        print("\nПокупатель без договоров (§3.1):")
        buyer_no_contract = await upsert_company(session, BUYER_NO_CONTRACT_COMPANY)

        print("\nПеревозчик (ТЗ_15 §5.6):")
        carrier_company = await upsert_company(session, CARRIER_COMPANY)
        await upsert_user(session, CARRIER_USER, carrier_company.id)

        print("\nЭкспедитор (ТЗ_15 §5.6):")
        forwarder_company = await upsert_company(session, FORWARDER_COMPANY)
        await upsert_user(session, FORWARDER_USER, forwarder_company.id)

        await session.commit()

        print("\nСвязи ЛК (Контрагенты / Покупатели / Перевозчики) §6:")
        await ensure_company_relations(
            session,
            seller_company.id,
            buyer_company.id,
            buyer_no_contract.id,
            carrier_company.id,
        )

        print("\nДоговоры ЛК (seller ↔ основной покупатель):")
        await ensure_company_contracts(session, seller_company.id, buyer_company.id)

        print("\nШаблоны условий (§4.4):")
        await ensure_contract_condition_templates(session, seller_company.id)

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

        print("\nСделка 2 (без счёта, с договорами — §3.1):")
        order_stage31_contracts = await ensure_deal(
            session,
            buyer_company.id,
            seller_company.id,
            comments=DEAL_STAGE31_CONTRACTS_COMMENTS,
            items=[
                OrderItemCreate(
                    product_name="Шайба M8 (§3.1)",
                    product_article="WASH-M8-31",
                    quantity=100,
                    unit_of_measurement="шт",
                    price=2.00,
                ),
            ],
        )

        print("\nСделка 3 (без счёта, без договоров — §3.1):")
        order_no_contract = await ensure_deal(
            session,
            buyer_no_contract.id,
            seller_company.id,
            comments=DEAL_NO_CONTRACT_COMMENTS,
            items=[
                OrderItemCreate(
                    product_name="Гайка M8",
                    product_article="NUT-M8",
                    quantity=150,
                    unit_of_measurement="шт",
                    price=3.00,
                ),
            ],
        )

        service = next(p for p in catalog if p.type == ProductType.SERVICE)
        print("\nСделка 4 (услуги без счёта — §4.6):")
        order_services = await ensure_deal(
            session,
            buyer_company.id,
            seller_company.id,
            comments=DEAL_SERVICES_COMMENTS,
            deal_type=OrderTypeSchema.SERVICES,
            items=[
                OrderItemCreate(
                    product_name=service.name,
                    product_article=service.article,
                    product_slug=service.slug,
                    quantity=1,
                    unit_of_measurement=service.unit_of_measurement or "усл",
                    price=float(service.price or 5000),
                ),
            ],
        )

    good = next(p for p in catalog if p.type == ProductType.GOOD)
    service = next(p for p in catalog if p.type == ProductType.SERVICE)

    async with AsyncSessionLocal() as session:
        for order_ref in (order_main, order_stage31_contracts, order_no_contract, order_services):
            latest = (
                await session.execute(
                    select(Order)
                    .where(Order.id == order_ref.id)
                    .order_by(Order.version.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()
            await ensure_bill_date_if_missing(session, latest)

    print("\n--- Готово ---")
    print(f"Пароль для всех тестовых: {TEST_PASSWORD}")
    print(f"Поставщик:  {SELLER_USER['email']}  ({SELLER_COMPANY['name']})")
    print(f"Покупатель: {BUYER_USER['email']}  ({BUYER_COMPANY['name']})")
    print(f"Перевозчик: {CARRIER_USER['email']}  ({CARRIER_COMPANY['name']})")
    print(f"Экспедитор: {FORWARDER_USER['email']}  ({FORWARDER_COMPANY['name']})")
    print(f"\nСделка 1: id={order_main.id}, заказ {order_main.seller_order_number}")
    print(f"Сделка 2 (§3.1 договоры): id={order_stage31_contracts.id}, заказ {order_stage31_contracts.seller_order_number}")
    print(f"Сделка 3 (§3.1 без договоров): id={order_no_contract.id}, заказ {order_no_contract.seller_order_number}")
    print(f"Сделка 4 (§4.6 услуги): id={order_services.id}, заказ {order_services.seller_order_number}")
    print("\n§3.1 «Создать счет» — seller@gmail.com → Продажи → Товары")
    print("  A) Сделка 2 → «Создать счет» → список договоров + «Без договора»")
    print("  B) Сделка 3 → «Создать счет» → «Создать без основания?» Да/Нет")
    print("\n§2.1 ОКЕИ — seller@gmail.com → Продажи → сделка 1 → Заказ (ОКЕИ 796, 166)")
    print("\n§2.2 Checkout — buyer@gmail.com:")
    print("  1) http://localhost:8080/auth/login")
    print(f"  2) В корзину: /catalog/items/{good.slug} и /catalog/items/{service.slug}")
    print("  3) Корзина → Оформить заказ → /checkout")
    print("  4) Два блока: товары и услуги → «Подтвердить» в каждом")
    print("  5) Закупки — два новых заказа; seller@gmail.com → Продажи + чат с уведомлением")
    print("\n§4 — seller@gmail.com:")
    print("  1) Продажи → Товары → сделка → счёт → переключение bill / bill-contract / bill-offer")
    print("  2) Шаблоны условий: API GET/POST /contract-condition-templates (seed: 4 шт.)")
    print("  3) Продажи → Услуги → сделка 4 (без счёта) → «Создать счет»")
    print("  4) DOC/PDF bill-contract / bill-offer — условия и галки реквизитов")


if __name__ == "__main__":
    asyncio.run(main())
