"""
Юнит-тесты сервиса документов: доступ только buyer/seller, валидация document_type, GET/PUT логика.

Запуск: из backend с запущенной БД (или DATABASE_URL на localhost).
  python -m pytest tests/test_documents_service.py -v
"""
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal
from app.api.documents.service import DocumentFormService, get_order_and_company_role
from app.api.documents.schemas import DocumentResponse
from app.api.purchases.models import Order, OrderStatus, OrderType
from app.api.company.models.company import Company
from datetime import datetime


@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def deal_buyer_seller(db_session: AsyncSession):
    """Две компании и заказ; возвращаем deal_id, buyer_company_id, seller_company_id."""
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


class TestGetOrderAndCompanyRole:
    """Вспомогательная функция доступа к сделке."""

    @pytest.mark.asyncio
    async def test_returns_buyer_for_buyer_company(self, db_session: AsyncSession, deal_buyer_seller):
        order, role = await get_order_and_company_role(
            db_session, deal_buyer_seller["deal_id"], deal_buyer_seller["buyer_id"]
        )
        assert order is not None
        assert role == "buyer"

    @pytest.mark.asyncio
    async def test_returns_seller_for_seller_company(self, db_session: AsyncSession, deal_buyer_seller):
        order, role = await get_order_and_company_role(
            db_session, deal_buyer_seller["deal_id"], deal_buyer_seller["seller_id"]
        )
        assert order is not None
        assert role == "seller"

    @pytest.mark.asyncio
    async def test_returns_none_for_unknown_deal(self, db_session: AsyncSession):
        order, role = await get_order_and_company_role(db_session, 999999, 1)
        assert order is None
        assert role is None

    @pytest.mark.asyncio
    async def test_returns_none_for_third_party_company(self, db_session: AsyncSession, deal_buyer_seller):
        other = Company(
            name="Other",
            slug="other-co",
            type="ООО",
            trade_activity="Покупатель",
            business_type="Производство",
            activity_type="Тест",
            description="",
            country="Россия",
            federal_district="ЦФО",
            region="Москва",
            city="Москва",
            full_name="ООО Other",
            inn="3333333333",
            ogrn="3333333333333",
            kpp="333333333",
            registration_date=datetime.now(),
            legal_address="",
            production_address="",
            phone="+79003333333",
            email="other@test.com",
            website="",
            is_active=True,
        )
        db_session.add(other)
        await db_session.flush()
        await db_session.commit()
        order, role = await get_order_and_company_role(
            db_session, deal_buyer_seller["deal_id"], other.id
        )
        assert order is not None  # заказ есть
        assert role is None  # но компания не участник


class TestDocumentFormService:
    """Тесты DocumentFormService: get_document, save_document."""

    @pytest.mark.asyncio
    async def test_get_document_404_deal_not_found(self, db_session: AsyncSession, deal_buyer_seller):
        service = DocumentFormService(db_session)
        with pytest.raises(HTTPException) as exc:
            await service.get_document(999999, "order", deal_buyer_seller["buyer_id"])
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_document_404_access_denied(self, db_session: AsyncSession, deal_buyer_seller):
        # компания, не участвующая в сделке (не buyer и не seller)
        other = Company(
            name="Other",
            slug="other-co",
            type="ООО",
            trade_activity="Покупатель",
            business_type="Производство",
            activity_type="Тест",
            description="",
            country="Россия",
            federal_district="ЦФО",
            region="Москва",
            city="Москва",
            full_name="ООО Other",
            inn="3333333333",
            ogrn="3333333333333",
            kpp="333333333",
            registration_date=datetime.now(),
            legal_address="",
            production_address="",
            phone="+79003333333",
            email="other@test.com",
            website="",
            is_active=True,
        )
        db_session.add(other)
        await db_session.flush()
        await db_session.commit()
        service = DocumentFormService(db_session)
        with pytest.raises(HTTPException) as exc:
            await service.get_document(deal_buyer_seller["deal_id"], "order", other.id)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_document_400_invalid_type(self, db_session: AsyncSession, deal_buyer_seller):
        service = DocumentFormService(db_session)
        with pytest.raises(HTTPException) as exc:
            await service.get_document(deal_buyer_seller["deal_id"], "invalid_type", deal_buyer_seller["buyer_id"])
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_get_document_empty_payload_when_no_form(self, db_session: AsyncSession, deal_buyer_seller):
        service = DocumentFormService(db_session)
        resp = await service.get_document(
            deal_buyer_seller["deal_id"], "order", deal_buyer_seller["buyer_id"]
        )
        assert isinstance(resp, DocumentResponse)
        assert resp.deal_id == deal_buyer_seller["deal_id"]
        assert resp.document_type == "order"
        assert resp.payload == {}
        assert resp.updated_by_company_id is None

    @pytest.mark.asyncio
    async def test_save_and_get_document(self, db_session: AsyncSession, deal_buyer_seller):
        service = DocumentFormService(db_session)
        payload = {"items": [{"name": "Товар", "qty": 1}], "comment": "Тест"}
        saved = await service.save_document(
            deal_buyer_seller["deal_id"], "order", payload, deal_buyer_seller["buyer_id"]
        )
        await db_session.commit()
        assert saved.payload == payload
        assert saved.updated_by_company_id == deal_buyer_seller["buyer_id"]

        got = await service.get_document(
            deal_buyer_seller["deal_id"], "order", deal_buyer_seller["seller_id"]
        )
        assert got.payload == payload
        assert got.updated_by_company_id == deal_buyer_seller["buyer_id"]

    @pytest.mark.asyncio
    async def test_save_document_404_deal_not_found(self, db_session: AsyncSession, deal_buyer_seller):
        service = DocumentFormService(db_session)
        with pytest.raises(HTTPException) as exc:
            await service.save_document(999999, "order", {}, deal_buyer_seller["buyer_id"])
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_save_document_400_invalid_type(self, db_session: AsyncSession, deal_buyer_seller):
        service = DocumentFormService(db_session)
        with pytest.raises(HTTPException) as exc:
            await service.save_document(
                deal_buyer_seller["deal_id"], "unknown_kind", {"a": 1}, deal_buyer_seller["buyer_id"]
            )
        assert exc.value.status_code == 400
