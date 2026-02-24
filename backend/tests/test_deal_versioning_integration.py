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


def _build_company_payload(suffix: str, inn_seed: int) -> dict:
    return {
        "name": f"Test Company {suffix}",
        "slug": f"test-company-{suffix}",
        "type": "ООО",
        "trade_activity": TradeActivity.BOTH,
        "business_type": BusinessType.BOTH,
        "activity_type": "Тестовая деятельность",
        "description": "Интеграционный тест",
        "country": "Россия",
        "federal_district": "ЦФО",
        "region": "Москва",
        "city": "Москва",
        "full_name": f"ООО Test Company {suffix}",
        "inn": f"{inn_seed:010d}",
        "ogrn": f"{inn_seed:013d}",
        "kpp": f"{(inn_seed % 10**9):09d}",
        "registration_date": datetime.utcnow(),
        "legal_address": "ул. Тестовая, 1",
        "production_address": "ул. Тестовая, 2",
        "phone": "+79000000000",
        "email": f"test-{suffix}@example.com",
        "website": "https://example.com",
        "is_active": True,
    }


@pytest.fixture
async def seeded_context():
    unique = uuid4().hex[:8]
    buyer_data = _build_company_payload(f"buyer-{unique}", inn_seed=1000000000 + int(unique[:4], 16) % 899999999)
    seller_data = _build_company_payload(f"seller-{unique}", inn_seed=2000000000 + int(unique[4:], 16) % 799999999)

    async with AsyncSessionLocal() as session:
        buyer_company = Company(**buyer_data)
        seller_company = Company(**seller_data)
        session.add_all([buyer_company, seller_company])
        await session.flush()

        user = User(
            email=f"user-{unique}@example.com",
            phone="+79001112233",
            first_name="Version",
            last_name="Tester",
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

    async def _override_current_user():
        return context["current_user"]

    app.dependency_overrides[get_current_user] = _override_current_user

    yield context

    app.dependency_overrides.pop(get_current_user, None)

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(Order).where(
                (Order.buyer_company_id == context["buyer_company_id"]) |
                (Order.seller_company_id == context["seller_company_id"])
            )
        )
        await session.execute(delete(User).where(User.id == context["user_id"]))
        await session.execute(delete(Company).where(Company.id.in_([context["buyer_company_id"], context["seller_company_id"]])))
        await session.commit()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


async def _create_deal(client: AsyncClient, seller_company_id: int) -> dict:
    payload = {
        "seller_company_id": seller_company_id,
        "deal_type": "Товары",
        "items": [
            {
                "article": None,
                "quantity": 2,
                "product_name": "Тестовая позиция",
                "unit_of_measurement": "шт",
                "price": 123.45,
            }
        ],
        "comments": "initial",
    }
    response = await client.post("/api/v1/purchases/deals", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.asyncio
async def test_deal_versioning_scenarios(client: AsyncClient, seeded_context: dict):
    # 1) Create deal -> version=1
    created = await _create_deal(client, seeded_context["seller_company_id"])
    deal_id = created["id"]
    assert created["version"] == 1

    # 2) CREATE_NEW_VERSION_DEAL -> version=2, same id
    create_v2_response = await client.post(
        f"/api/v1/purchases/deals/{deal_id}/versions",
        json={"comments": "created-from-version-endpoint"},
    )
    assert create_v2_response.status_code == 200, create_v2_response.text
    version2 = create_v2_response.json()
    assert version2["id"] == deal_id
    assert version2["version"] == 2
    assert version2["comments"] == "created-from-version-endpoint"

    # 3) GET by id returns active version by default (v1); v2 доступна по ?version=2
    get_active_response = await client.get(f"/api/v1/purchases/deals/{deal_id}")
    assert get_active_response.status_code == 200, get_active_response.text
    active = get_active_response.json()
    assert active["id"] == deal_id
    assert active["version"] == 1

    get_v2_response = await client.get(f"/api/v1/purchases/deals/{deal_id}?version=2")
    assert get_v2_response.status_code == 200, get_v2_response.text
    latest = get_v2_response.json()
    assert latest["version"] == 2
    assert latest.get("comments") == "created-from-version-endpoint"

    # 4) PUT updates latest version in-place (v2 remains, comments updated)
    update_payload = {"comments": "updated-latest"}
    put_response = await client.put(f"/api/v1/purchases/deals/{deal_id}", json=update_payload)
    assert put_response.status_code == 200, put_response.text
    updated_latest = put_response.json()
    assert updated_latest["version"] == 2
    assert updated_latest["comments"] == "updated-latest"

    # Ensure v1 is still unchanged in DB
    async with AsyncSessionLocal() as session:
        version1_order = (
            await session.execute(
                select(Order).where(Order.id == deal_id, Order.version == 1)
            )
        ).scalar_one()
        version2_order = (
            await session.execute(
                select(Order).where(Order.id == deal_id, Order.version == 2)
            )
        ).scalar_one()
        assert version1_order.comments == "initial"
        assert version2_order.comments == "updated-latest"

    # 5) DELETE_LAST_VERSION_DEAL removes only latest (v2)
    delete_last_response = await client.delete(f"/api/v1/purchases/deals/{deal_id}/versions/last")
    assert delete_last_response.status_code == 200, delete_last_response.text
    delete_last_data = delete_last_response.json()
    assert delete_last_data["deal_id"] == deal_id
    assert delete_last_data["deleted_version"] == 2

    after_delete_last = await client.get(f"/api/v1/purchases/deals/{deal_id}")
    assert after_delete_last.status_code == 200, after_delete_last.text
    reverted_active = after_delete_last.json()
    assert reverted_active["version"] == 1
    assert reverted_active["comments"] == "initial"

    # 6) DELETE /deals/{id} removes all versions
    delete_all_response = await client.delete(f"/api/v1/purchases/deals/{deal_id}")
    assert delete_all_response.status_code == 200, delete_all_response.text
    delete_all_data = delete_all_response.json()
    assert delete_all_data["deal_id"] == deal_id

    get_after_delete_all = await client.get(f"/api/v1/purchases/deals/{deal_id}")
    assert get_after_delete_all.status_code == 404
