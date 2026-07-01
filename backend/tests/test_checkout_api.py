"""
Тесты checkout: группировка товаров и услуг в отдельные заказы.
"""
import pytest
from datetime import datetime
from uuid import uuid4
from sqlalchemy import delete, select
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.db.base import AsyncSessionLocal
from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.roles_positions import UserRole
from app.api.authentication.models.user import User
from app.api.company.models.company import Company, TradeActivity, BusinessType
from app.api.messages.models.message import Message
from app.api.products.models.product import Product, ProductType
from app.api.purchases.models import Order, OrderType


def _company_payload(suffix: str, inn_seed: int) -> dict:
    return {
        "name": f"Checkout Company {suffix}",
        "slug": f"checkout-company-{suffix}",
        "type": "ООО",
        "trade_activity": TradeActivity.BOTH,
        "business_type": BusinessType.BOTH,
        "activity_type": "Тест",
        "description": "Тест",
        "country": "Россия",
        "federal_district": "ЦФО",
        "region": "Москва",
        "city": "Москва",
        "full_name": f"ООО Checkout {suffix}",
        "inn": f"{inn_seed:010d}",
        "ogrn": f"{inn_seed:013d}",
        "kpp": f"{(inn_seed % 10**9):09d}",
        "registration_date": datetime.utcnow(),
        "legal_address": "ул. Тест, 1",
        "production_address": "ул. Тест, 2",
        "phone": "+79000000000",
        "email": f"checkout-{suffix}@example.com",
        "website": "https://example.com",
        "is_active": True,
    }


def _checkout_item_slug_only(
    *,
    product_name: str,
    product_type: str,
    slug: str,
) -> dict:
    """Позиция корзины без companyId — продавец определяется на бэкенде по slug."""
    return {
        "slug": slug,
        "description": "Описание",
        "logoUrl": None,
        "productName": product_name,
        "article": "",
        "productType": product_type,
        "quantity": 1,
        "units": "шт",
        "price": 100.0,
        "amount": 100.0,
    }

def _checkout_item(
    *,
    company_id: int,
    company_name: str,
    company_slug: str,
    product_name: str,
    product_type: str,
    slug: str,
) -> dict:
    return {
        "slug": slug,
        "description": "Описание",
        "logoUrl": None,
        "productName": product_name,
        "article": "",
        "productType": product_type,
        "quantity": 1,
        "units": "шт",
        "price": 100.0,
        "amount": 100.0,
        "companyId": company_id,
        "companyName": company_name,
        "companySlug": company_slug,
    }


@pytest.fixture
async def checkout_context():
    unique = uuid4().hex[:8]
    buyer_data = _company_payload(f"buyer-{unique}", 3000000000 + int(unique[:4], 16) % 699999999)
    seller_data = _company_payload(f"seller-{unique}", 4000000000 + int(unique[4:], 16) % 599999999)

    async with AsyncSessionLocal() as session:
        buyer_company = Company(**buyer_data)
        seller_company = Company(**seller_data)
        session.add_all([buyer_company, seller_company])
        await session.flush()

        user = User(
            email=f"checkout-user-{unique}@example.com",
            phone="+79003334455",
            first_name="Checkout",
            last_name="Buyer",
            hashed_password="test",
            is_active=True,
            company_id=buyer_company.id,
            role=UserRole.OWNER,
        )
        seller_user = User(
            email=f"checkout-seller-{unique}@example.com",
            phone="+79003334456",
            first_name="Checkout",
            last_name="Seller",
            hashed_password="test",
            is_active=True,
            company_id=seller_company.id,
            role=UserRole.OWNER,
        )
        session.add_all([user, seller_user])
        await session.commit()
        await session.refresh(user)
        await session.refresh(buyer_company)
        await session.refresh(seller_company)

        context = {
            "user_id": user.id,
            "buyer_company_id": buyer_company.id,
            "seller_company_id": seller_company.id,
            "seller_slug": seller_company.slug,
            "seller_name": seller_company.name,
            "current_user": user,
        }

    def _override_current_user():
        return context["current_user"]

    app.dependency_overrides[get_current_user] = _override_current_user
    yield context
    app.dependency_overrides.pop(get_current_user, None)

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(Order).where(
                (Order.buyer_company_id == context["buyer_company_id"])
                | (Order.seller_company_id == context["seller_company_id"])
            )
        )
        await session.execute(delete(User).where(User.id == context["user_id"]))
        await session.execute(
            delete(User).where(User.company_id == context["seller_company_id"])
        )
        await session.execute(
            delete(Company).where(
                Company.id.in_([context["buyer_company_id"], context["seller_company_id"]])
            )
        )
        await session.commit()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.asyncio
async def test_checkout_splits_goods_and_services(client: AsyncClient, checkout_context: dict):
    """POST /checkout — товары и услуги одного продавца создают два заказа."""
    seller_id = checkout_context["seller_company_id"]
    payload = {
        "items": [
            _checkout_item(
                company_id=seller_id,
                company_name=checkout_context["seller_name"],
                company_slug=checkout_context["seller_slug"],
                product_name="Товар А",
                product_type="Товар",
                slug="good-a",
            ),
            _checkout_item(
                company_id=seller_id,
                company_name=checkout_context["seller_name"],
                company_slug=checkout_context["seller_slug"],
                product_name="Услуга Б",
                product_type="Услуга",
                slug="service-b",
            ),
        ],
        "comments": "checkout test",
    }

    response = await client.post("/api/v1/purchases/checkout", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "deals" in data
    assert len(data["deals"]) == 2

    deal_types = {deal["deal_type"] for deal in data["deals"]}
    assert deal_types == {"Товары", "Услуги"}

    async with AsyncSessionLocal() as session:
        orders = (
            await session.execute(
                select(Order).where(Order.buyer_company_id == checkout_context["buyer_company_id"])
            )
        ).scalars().all()
        assert len(orders) == 2
        db_types = {order.deal_type for order in orders}
        assert db_types == {OrderType.GOODS, OrderType.SERVICES}


@pytest.mark.asyncio
async def test_checkout_single_type_returns_one_deal(client: AsyncClient, checkout_context: dict):
    seller_id = checkout_context["seller_company_id"]
    payload = {
        "items": [
            _checkout_item(
                company_id=seller_id,
                company_name=checkout_context["seller_name"],
                company_slug=checkout_context["seller_slug"],
                product_name="Товар В",
                product_type="Товар",
                slug="good-c",
            ),
        ],
    }

    response = await client.post("/api/v1/purchases/checkout", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["deals"]) == 1
    assert data["deals"][0]["deal_type"] == "Товары"


@pytest.mark.asyncio
async def test_checkout_sends_chat_notification(client: AsyncClient, checkout_context: dict):
    """Checkout создаёт сделку и уведомление продавцу в чате (без отдельного вызова /chats)."""
    seller_id = checkout_context["seller_company_id"]
    payload = {
        "items": [
            _checkout_item(
                company_id=seller_id,
                company_name=checkout_context["seller_name"],
                company_slug=checkout_context["seller_slug"],
                product_name="Товар для чата",
                product_type="Товар",
                slug="good-chat-notify",
            ),
        ],
    }

    response = await client.post("/api/v1/purchases/checkout", json=payload)
    assert response.status_code == 200, response.text
    deal = response.json()["deals"][0]
    order_number = deal["seller_order_number"]

    async with AsyncSessionLocal() as session:
        msgs = (
            await session.execute(
                select(Message).where(Message.content.contains("Поступил новый заказ"))
            )
        ).scalars().all()
        matching = [m for m in msgs if order_number in m.content and "Товар для чата" in m.content]
        assert len(matching) >= 1
        assert matching[-1].sender_user_id == checkout_context["user_id"]


@pytest.mark.asyncio
async def test_checkout_resolves_seller_from_product_slug(
    client: AsyncClient, checkout_context: dict
):
    """POST /checkout без companyId — продавец берётся из каталога по slug товара."""
    unique = uuid4().hex[:8]
    good_slug = f"checkout-good-{unique}"
    service_slug = f"checkout-service-{unique}"
    seller_id = checkout_context["seller_company_id"]

    async with AsyncSessionLocal() as session:
        session.add_all([
            Product(
                name="Товар по slug",
                slug=good_slug,
                article=f"ART-G-{unique}",
                type=ProductType.GOOD,
                price=100.0,
                unit_of_measurement="шт",
                company_id=seller_id,
            ),
            Product(
                name="Услуга по slug",
                slug=service_slug,
                article=f"ART-S-{unique}",
                type=ProductType.SERVICE,
                price=200.0,
                unit_of_measurement="усл",
                company_id=seller_id,
            ),
        ])
        await session.commit()

    payload = {
        "items": [
            _checkout_item_slug_only(
                product_name="Товар по slug",
                product_type="Товар",
                slug=good_slug,
            ),
            _checkout_item_slug_only(
                product_name="Услуга по slug",
                product_type="Услуга",
                slug=service_slug,
            ),
        ],
    }

    response = await client.post("/api/v1/purchases/checkout", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["deals"]) == 2
    assert {d["deal_type"] for d in data["deals"]} == {"Товары", "Услуги"}
