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
async def seller_user_context():
    unique = uuid4().hex[:8]
    buyer_data = _build_company_payload(
        f"buyer-cr-{unique}", 1000000000 + int(unique[:4], 16) % 899999999
    )
    seller_data = _build_company_payload(
        f"seller-cr-{unique}", 2000000000 + int(unique[4:], 16) % 799999999
    )

    async with AsyncSessionLocal() as session:
        buyer_company = Company(**buyer_data)
        seller_company = Company(**seller_data)
        session.add_all([buyer_company, seller_company])
        await session.flush()

        buyer_user = User(
            email=f"buyer-{unique}@example.com",
            phone="+79001112233",
            first_name="Buyer",
            last_name="Tester",
            hashed_password="test",
            is_active=True,
            company_id=buyer_company.id,
        )
        seller_user = User(
            email=f"seller-{unique}@example.com",
            phone="+79001112234",
            first_name="Seller",
            last_name="Tester",
            hashed_password="test",
            is_active=True,
            company_id=seller_company.id,
        )
        session.add_all([buyer_user, seller_user])
        await session.commit()
        await session.refresh(buyer_user)
        await session.refresh(seller_user)
        await session.refresh(buyer_company)
        await session.refresh(seller_company)

        context = {
            "buyer_user": buyer_user,
            "seller_user": seller_user,
            "buyer_company_id": buyer_company.id,
            "seller_company_id": seller_company.id,
            "current_user": seller_user,
        }

    async def _override_current_user():
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
        await session.execute(
            delete(User).where(
                User.id.in_([context["buyer_user"].id, context["seller_user"].id])
            )
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
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


def _set_current_user(context: dict, user: User) -> None:
    context["current_user"] = user

    async def _override_current_user():
        return context["current_user"]

    app.dependency_overrides[get_current_user] = _override_current_user


async def _create_deal(client: AsyncClient, seller_company_id: int) -> dict:
    payload = {
        "seller_company_id": seller_company_id,
        "deal_type": "Товары",
        "items": [
            {
                "article": None,
                "quantity": 1,
                "product_name": "Тестовая позиция",
                "unit_of_measurement": "шт",
                "price": 100.0,
            }
        ],
        "comments": "initial",
    }
    response = await client.post("/api/v1/purchases/deals", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.asyncio
async def test_change_review_only_counterparty_can_respond(
    client: AsyncClient, seller_user_context: dict
):
    context = seller_user_context
    _set_current_user(context, context["buyer_user"])

    created = await _create_deal(client, context["seller_company_id"])
    deal_id = created["id"]

    _set_current_user(context, context["seller_user"])
    create_v2 = await client.post(
        f"/api/v1/purchases/deals/{deal_id}/versions",
        json={"comments": "seller proposal"},
    )
    assert create_v2.status_code == 200, create_v2.text

    seller_review = await client.get(f"/api/v1/purchases/deals/{deal_id}/change-review")
    assert seller_review.status_code == 200, seller_review.text
    seller_data = seller_review.json()
    assert seller_data["has_pending_changes"] is True
    assert seller_data["can_respond"] is False
    assert seller_data["is_proposer"] is True

    _set_current_user(context, context["buyer_user"])
    buyer_review = await client.get(f"/api/v1/purchases/deals/{deal_id}/change-review")
    assert buyer_review.status_code == 200, buyer_review.text
    buyer_data = buyer_review.json()
    assert buyer_data["has_pending_changes"] is True
    assert buyer_data["can_respond"] is True
    assert buyer_data["is_proposer"] is False
    assert buyer_data.get("diff") is not None
    assert any(item["status"] == "modified" for item in buyer_data["diff"]["items"]) or buyer_data["diff"]["comments_changed"]

    _set_current_user(context, context["seller_user"])
    proposer_accept = await client.post(f"/api/v1/purchases/deals/{deal_id}/changes/accept")
    assert proposer_accept.status_code == 403

    proposer_reject = await client.post(f"/api/v1/purchases/deals/{deal_id}/changes/reject")
    assert proposer_reject.status_code == 403

    _set_current_user(context, context["buyer_user"])
    buyer_accept = await client.post(f"/api/v1/purchases/deals/{deal_id}/changes/accept")
    assert buyer_accept.status_code == 200, buyer_accept.text

    after_accept = await client.get(f"/api/v1/purchases/deals/{deal_id}/change-review")
    assert after_accept.json()["has_pending_changes"] is False

    async with AsyncSessionLocal() as session:
        latest = (
            await session.execute(
                select(Order).where(Order.id == deal_id).order_by(Order.version.desc()).limit(1)
            )
        ).scalar_one()
        assert latest.proposed_by_company_id is None
        assert latest.buyer_accepted_at is not None


@pytest.mark.asyncio
async def test_change_review_buyer_can_reject_seller_proposal(
    client: AsyncClient, seller_user_context: dict
):
    context = seller_user_context
    _set_current_user(context, context["buyer_user"])

    created = await _create_deal(client, context["seller_company_id"])
    deal_id = created["id"]

    _set_current_user(context, context["seller_user"])
    create_v2 = await client.post(
        f"/api/v1/purchases/deals/{deal_id}/versions",
        json={"comments": "seller proposal v2"},
    )
    assert create_v2.status_code == 200, create_v2.text

    _set_current_user(context, context["buyer_user"])
    reject_response = await client.post(f"/api/v1/purchases/deals/{deal_id}/changes/reject")
    assert reject_response.status_code == 200, reject_response.text
    assert reject_response.json()["deleted_version"] == 2

    get_deal = await client.get(f"/api/v1/purchases/deals/{deal_id}")
    assert get_deal.status_code == 200
    assert get_deal.json()["version"] == 1
    assert get_deal.json()["comments"] == "initial"


@pytest.mark.asyncio
async def test_buyer_can_create_order_version(client: AsyncClient, seller_user_context: dict):
    """§3.3: покупатель может создать новую версию заказа (не документов)."""
    context = seller_user_context
    _set_current_user(context, context["buyer_user"])

    created = await _create_deal(client, context["seller_company_id"])
    deal_id = created["id"]

    create_v2 = await client.post(
        f"/api/v1/purchases/deals/{deal_id}/versions",
        json={"comments": "buyer proposal"},
    )
    assert create_v2.status_code == 200, create_v2.text
    assert create_v2.json()["comments"] == "buyer proposal"
    assert create_v2.json()["version"] == 2

    forbidden = await client.post(
        f"/api/v1/purchases/deals/{deal_id}/versions",
        json={
            "comments": "buyer bill hack",
            "bill": {"number": "HACK-001"},
        },
    )
    assert forbidden.status_code == 403
