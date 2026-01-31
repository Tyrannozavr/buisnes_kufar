"""
Юнит-тесты репозитория форм документов (DealDocumentForm).
Проверяем: get по пустой БД, save создаёт запись, save обновляет существующую.

Запуск: из backend с запущенной БД (или DATABASE_URL на localhost).
  python -m pytest tests/test_documents_repository.py -v
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal
from app.api.documents.repository import DocumentFormRepository
from app.api.documents.models import DealDocumentForm
from app.api.purchases.models import Order, OrderStatus, OrderType
from app.api.company.models.company import Company
from datetime import datetime


@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def deal_and_companies(db_session: AsyncSession):
    """Создаём две компании и заказ (сделку) для привязки документов."""
    buyer = Company(
        name="Buyer Co",
        slug="buyer-co",
        type="ООО",
        trade_activity="Покупатель",
        business_type="Производство",
        activity_type="Тест",
        description="",
        country="Россия",
        federal_district="ЦФО",
        region="Москва",
        city="Москва",
        full_name="ООО Buyer",
        inn="1111111111",
        ogrn="1111111111111",
        kpp="111111111",
        registration_date=datetime.now(),
        legal_address="",
        production_address="",
        phone="+79001111111",
        email="buyer@test.com",
        website="",
        is_active=True,
    )
    seller = Company(
        name="Seller Co",
        slug="seller-co",
        type="ООО",
        trade_activity="Продавец",
        business_type="Производство",
        activity_type="Тест",
        description="",
        country="Россия",
        federal_district="ЦФО",
        region="Москва",
        city="Москва",
        full_name="ООО Seller",
        inn="2222222222",
        ogrn="2222222222222",
        kpp="222222222",
        registration_date=datetime.now(),
        legal_address="",
        production_address="",
        phone="+79002222222",
        email="seller@test.com",
        website="",
        is_active=True,
    )
    db_session.add(buyer)
    db_session.add(seller)
    await db_session.flush()

    order = Order(
        buyer_order_number="00001",
        seller_order_number="00001",
        deal_type=OrderType.GOODS,
        status=OrderStatus.ACTIVE,
        buyer_company_id=buyer.id,
        seller_company_id=seller.id,
    )
    db_session.add(order)
    await db_session.flush()
    await db_session.refresh(order)
    await db_session.commit()
    return {"deal_id": order.id, "buyer_id": buyer.id, "seller_id": seller.id}


class TestDocumentFormRepository:
    """Тесты DocumentFormRepository: get/save."""

    @pytest.mark.asyncio
    async def test_get_returns_none_when_no_row(self, db_session: AsyncSession, deal_and_companies):
        repo = DocumentFormRepository(db_session)
        deal_id = deal_and_companies["deal_id"]
        row = await repo.get(deal_id, "order")
        assert row is None

    @pytest.mark.asyncio
    async def test_save_creates_new_row(self, db_session: AsyncSession, deal_and_companies):
        repo = DocumentFormRepository(db_session)
        deal_id = deal_and_companies["deal_id"]
        payload = {"items": [{"name": "Товар 1", "qty": 2}]}
        row = await repo.save(deal_id, "order", payload, updated_by_company_id=deal_and_companies["buyer_id"])
        await db_session.commit()
        assert row.id is not None
        assert row.deal_id == deal_id
        assert row.document_type == "order"
        assert row.payload == payload
        assert row.updated_by_company_id == deal_and_companies["buyer_id"]

    @pytest.mark.asyncio
    async def test_get_returns_row_after_save(self, db_session: AsyncSession, deal_and_companies):
        repo = DocumentFormRepository(db_session)
        deal_id = deal_and_companies["deal_id"]
        payload = {"comment": "Заказ от покупателя"}
        await repo.save(deal_id, "bill", payload, updated_by_company_id=deal_and_companies["seller_id"])
        await db_session.commit()

        row = await repo.get(deal_id, "bill")
        assert row is not None
        assert row.payload == payload
        assert row.document_type == "bill"

    @pytest.mark.asyncio
    async def test_save_updates_existing_row(self, db_session: AsyncSession, deal_and_companies):
        repo = DocumentFormRepository(db_session)
        deal_id = deal_and_companies["deal_id"]
        await repo.save(deal_id, "order", {"v": 1}, updated_by_company_id=deal_and_companies["buyer_id"])
        await db_session.commit()

        row2 = await repo.save(deal_id, "order", {"v": 2, "extra": "ok"}, updated_by_company_id=deal_and_companies["seller_id"])
        await db_session.commit()
        assert row2.payload == {"v": 2, "extra": "ok"}
        assert row2.updated_by_company_id == deal_and_companies["seller_id"]

        same = await repo.get(deal_id, "order")
        assert same.id == row2.id
        assert same.payload == {"v": 2, "extra": "ok"}
