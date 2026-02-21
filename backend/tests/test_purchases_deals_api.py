"""
Тесты API заказов/сделок: создание, получение списков покупателя/продавца, получение по ID.
Используют аутентификацию через override get_current_user.
"""
import pytest
from datetime import datetime
from uuid import uuid4
from sqlalchemy import delete, select
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.db.base import AsyncSessionLocal
from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.company.models.company import Company, TradeActivity, BusinessType
from app.api.purchases.models import Order


def _company_payload(suffix: str, inn_seed: int) -> dict:
    return {
        "name": f"Test Company {suffix}",
        "slug": f"test-company-{suffix}",
        "type": "ООО",
        "trade_activity": TradeActivity.BOTH,
        "business_type": BusinessType.BOTH,
        "activity_type": "Тест",
        "description": "Тест",
        "country": "Россия",
        "federal_district": "ЦФО",
        "region": "Москва",
        "city": "Москва",
        "full_name": f"ООО Test {suffix}",
        "inn": f"{inn_seed:010d}",
        "ogrn": f"{inn_seed:013d}",
        "kpp": f"{(inn_seed % 10**9):09d}",
        "registration_date": datetime.utcnow(),
        "legal_address": "ул. Тест, 1",
        "production_address": "ул. Тест, 2",
        "phone": "+79000000000",
        "email": f"test-{suffix}@example.com",
        "website": "https://example.com",
        "is_active": True,
    }


@pytest.fixture
async def seeded_context():
    """Покупатель, продавец, пользователь — для тестов с авторизацией."""
    unique = uuid4().hex[:8]
    buyer_data = _company_payload(f"buyer-{unique}", 1000000000 + int(unique[:4], 16) % 899999999)
    seller_data = _company_payload(f"seller-{unique}", 2000000000 + int(unique[4:], 16) % 799999999)

    async with AsyncSessionLocal() as session:
        buyer_company = Company(**buyer_data)
        seller_company = Company(**seller_data)
        session.add_all([buyer_company, seller_company])
        await session.flush()

        user = User(
            email=f"user-{unique}@example.com",
            phone="+79001112233",
            first_name="Test",
            last_name="User",
            hashed_password="test",
            is_active=True,
            company_id=buyer_company.id,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        await session.refresh(buyer_company)
        await session.refresh(seller_company)

        context = {
            "user_id": user.id,
            "buyer_company_id": buyer_company.id,
            "seller_company_id": seller_company.id,
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
            delete(Company).where(
                Company.id.in_([context["buyer_company_id"], context["seller_company_id"]])
            )
        )
        await session.commit()


@pytest.fixture
async def client():
    """Async HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


def _valid_deal_payload(seller_company_id: int, deal_type: str = "Товары"):
    return {
        "seller_company_id": seller_company_id,
        "deal_type": deal_type,
        "items": [
            {
                "article": None,
                "quantity": 2,
                "product_name": "Тестовый товар",
                "unit_of_measurement": "шт",
                "price": 100.0,
            }
        ],
        "comments": "тест",
    }


@pytest.mark.asyncio
async def test_create_deal_success(client: AsyncClient, seeded_context: dict):
    """POST /api/v1/purchases/deals — успешное создание заказа."""
    payload = _valid_deal_payload(seeded_context["seller_company_id"])
    response = await client.post("/api/v1/purchases/deals", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] > 0
    assert data["version"] == 1
    assert data["deal_type"] == "Товары"
    assert data["buyer_company_id"] == seeded_context["buyer_company_id"]
    assert data["seller_company_id"] == seeded_context["seller_company_id"]
    assert data["buyer_order_number"]
    assert data["seller_order_number"]


@pytest.mark.asyncio
async def test_get_buyer_deals_after_create(client: AsyncClient, seeded_context: dict):
    """GET /api/v1/purchases/buyer/deals — покупатель видит свои заказы."""
    payload = _valid_deal_payload(seeded_context["seller_company_id"])
    await client.post("/api/v1/purchases/deals", json=payload)

    response = await client.get("/api/v1/purchases/buyer/deals")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    deal = next((d for d in data if d["seller_company_id"] == seeded_context["seller_company_id"]), None)
    assert deal is not None
    assert deal["buyer_order_number"]
    assert "supplier_name" in deal or "buyer_name" in deal or "id" in deal


@pytest.mark.asyncio
async def test_get_seller_deals_returns_list(client: AsyncClient, seeded_context: dict):
    """GET /api/v1/purchases/seller/deals — возвращает 200 и список (текущий пользователь — покупатель, у продавца заказов может не быть)."""
    response = await client.get("/api/v1/purchases/seller/deals")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_deal_by_id_success(client: AsyncClient, seeded_context: dict):
    """GET /api/v1/purchases/deals/{id} — получение сделки по ID."""
    payload = _valid_deal_payload(seeded_context["seller_company_id"])
    create_resp = await client.post("/api/v1/purchases/deals", json=payload)
    assert create_resp.status_code == 200
    deal_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/purchases/deals/{deal_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == deal_id
    assert "items" in data


@pytest.mark.asyncio
async def test_get_deal_by_id_404(client: AsyncClient, seeded_context: dict):
    """GET /api/v1/purchases/deals/999999 — 404 для несуществующего ID."""
    response = await client.get("/api/v1/purchases/deals/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_deal_validation_missing_required(client: AsyncClient, seeded_context: dict):
    """POST /api/v1/purchases/deals — 422 при отсутствии обязательных полей."""
    payload = {
        "seller_company_id": seeded_context["seller_company_id"],
        "deal_type": "Товары",
        "items": [],
    }
    response = await client.post("/api/v1/purchases/deals", json=payload)
    assert response.status_code == 422, response.text
