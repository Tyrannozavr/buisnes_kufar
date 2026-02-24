"""
Тесты API форм документов: GET/PUT /deals/{deal_id}/documents/form.
Проверяют сохранение и чтение JSON payload для типов bill, supply_contract с версионированием.
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
from app.api.purchases.models import Order, OrderDocument


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
            first_name="Form",
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

    def _override_current_user():
        return context["current_user"]

    app.dependency_overrides[get_current_user] = _override_current_user
    yield context
    app.dependency_overrides.pop(get_current_user, None)

    async with AsyncSessionLocal() as session:
        # Удаляем заказы (каскадно удалятся order_documents), затем пользователя и компании
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
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


def _valid_deal_payload(seller_company_id: int):
    return {
        "seller_company_id": seller_company_id,
        "deal_type": "Товары",
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
async def test_get_document_form_empty(client: AsyncClient, seeded_context: dict):
    """GET формы без сохранённых данных возвращает пустой payload и v1."""
    payload = _valid_deal_payload(seeded_context["seller_company_id"])
    create_resp = await client.post("/api/v1/purchases/deals", json=payload)
    assert create_resp.status_code == 200
    deal_id = create_resp.json()["id"]

    response = await client.get(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        params={"document_type": "bill"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["payload"] == {}
    assert data["document_version"] == "v1"
    assert data.get("updated_at") is None
    assert data.get("updated_by_company_id") is None


@pytest.mark.asyncio
async def test_save_and_get_document_form_bill(client: AsyncClient, seeded_context: dict):
    """PUT сохраняет форму счета, GET возвращает те же данные."""
    deal_payload = _valid_deal_payload(seeded_context["seller_company_id"])
    create_resp = await client.post("/api/v1/purchases/deals", json=deal_payload)
    assert create_resp.status_code == 200
    deal_id = create_resp.json()["id"]

    form_payload = {
        "invoice_number": "СЧ-001",
        "invoice_date": "2026-02-24",
        "seller_inn": "1234567890",
        "seller_name": "ООО Поставщик",
        "buyer_name": "ООО Покупатель",
        "items": [{"name": "Услуга 1", "quantity": 1, "price": 1000, "amount": 1000}],
        "total": 1000,
    }

    put_resp = await client.put(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        json={"document_type": "bill", "payload": form_payload},
    )
    assert put_resp.status_code == 200, put_resp.text
    put_data = put_resp.json()
    assert put_data["payload"] == form_payload
    assert put_data["document_version"] == "v1"
    assert put_data.get("updated_at") is not None
    assert put_data.get("updated_by_company_id") == seeded_context["buyer_company_id"]

    get_resp = await client.get(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        params={"document_type": "bill"},
    )
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["payload"] == form_payload
    assert get_data["document_version"] == "v1"


@pytest.mark.asyncio
async def test_save_and_get_document_form_supply_contract(client: AsyncClient, seeded_context: dict):
    """PUT сохраняет форму договора поставки, GET возвращает те же данные."""
    deal_payload = _valid_deal_payload(seeded_context["seller_company_id"])
    create_resp = await client.post("/api/v1/purchases/deals", json=deal_payload)
    assert create_resp.status_code == 200
    deal_id = create_resp.json()["id"]

    form_payload = {
        "contract_number": "ДП-001",
        "contract_date": "2026-02-24",
        "supplier": "ООО Поставщик",
        "customer": "ООО Покупатель",
        "subject": "Поставка товаров",
        "delivery_terms": "До 10 дней",
    }

    put_resp = await client.put(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        json={"document_type": "supply_contract", "payload": form_payload},
    )
    assert put_resp.status_code == 200, put_resp.text
    assert put_resp.json()["payload"] == form_payload

    get_resp = await client.get(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        params={"document_type": "supply_contract"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["payload"] == form_payload


@pytest.mark.asyncio
async def test_document_form_update_overwrites(client: AsyncClient, seeded_context: dict):
    """Повторный PUT с тем же document_type обновляет payload (версия остаётся v1)."""
    deal_payload = _valid_deal_payload(seeded_context["seller_company_id"])
    create_resp = await client.post("/api/v1/purchases/deals", json=deal_payload)
    assert create_resp.status_code == 200
    deal_id = create_resp.json()["id"]

    await client.put(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        json={"document_type": "bill", "payload": {"old": "data"}},
    )
    updated = {"invoice_number": "СЧ-002", "total": 2000}
    put_resp = await client.put(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        json={"document_type": "bill", "payload": updated},
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["payload"] == updated

    get_resp = await client.get(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        params={"document_type": "bill"},
    )
    assert get_resp.json()["payload"] == updated


@pytest.mark.asyncio
async def test_document_form_wrong_deal(client: AsyncClient, seeded_context: dict):
    """GET для несуществующей сделки — 200 и пустой payload; PUT — 404."""
    get_resp = await client.get(
        "/api/v1/purchases/deals/999999/documents/form",
        params={"document_type": "bill"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["payload"] == {}

    put_resp = await client.put(
        "/api/v1/purchases/deals/999999/documents/form",
        json={"document_type": "bill", "payload": {"x": 1}},
    )
    assert put_resp.status_code == 404


@pytest.mark.asyncio
async def test_document_form_invalid_document_type(client: AsyncClient, seeded_context: dict):
    """Неверный document_type — 400."""
    deal_payload = _valid_deal_payload(seeded_context["seller_company_id"])
    create_resp = await client.post("/api/v1/purchases/deals", json=deal_payload)
    assert create_resp.status_code == 200
    deal_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        params={"document_type": "invalid_type"},
    )
    assert resp.status_code == 400

    resp = await client.put(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        json={"document_type": "invalid_type", "payload": {}},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_document_form_persisted_in_db(client: AsyncClient, seeded_context: dict):
    """После PUT запись формы есть в БД (order_documents с document_number='-')."""
    deal_payload = _valid_deal_payload(seeded_context["seller_company_id"])
    create_resp = await client.post("/api/v1/purchases/deals", json=deal_payload)
    assert create_resp.status_code == 200
    deal_id = create_resp.json()["id"]
    payload_saved = {"key": "value", "nested": {"a": 1}}

    await client.put(
        f"/api/v1/purchases/deals/{deal_id}/documents/form",
        json={"document_type": "bill", "payload": payload_saved},
    )

    async with AsyncSessionLocal() as session:
        from sqlalchemy import and_
        # Найти заказ по deal_id (id), затем форму документа по order_row_id
        order_result = await session.execute(
            select(Order).where(Order.id == deal_id).order_by(Order.version.desc()).limit(1)
        )
        order = order_result.scalar_one_or_none()
        assert order is not None
        result = await session.execute(
            select(OrderDocument).where(
                and_(
                    OrderDocument.order_row_id == order.row_id,
                    OrderDocument.document_type == "bill",
                    OrderDocument.document_number == "-",
                    OrderDocument.document_file_path.is_(None),
                )
            )
        )
        docs = list(result.scalars().all())
    assert len(docs) == 1
    form_doc = docs[0]
    assert form_doc.document_content == payload_saved
    assert getattr(form_doc, "document_version", "v1") == "v1"
    assert form_doc.updated_by_company_id == seeded_context["buyer_company_id"]
