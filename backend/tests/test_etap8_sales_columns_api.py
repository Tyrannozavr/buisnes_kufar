"""API этапа 8 — счёт replace, перевозка, закрывающие (ТЗ_15)."""
from datetime import datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.api.purchases.models import Order, OrderItem, OrderStatus, OrderType
from app.db.base import AsyncSessionLocal
from app.main import app


def _company_payload(suffix: str, inn_seed: int, *, trade: TradeActivity) -> dict:
	return {
		"name": f"E8 Co {suffix}",
		"slug": f"e8-co-{suffix}",
		"type": "ООО",
		"trade_activity": trade,
		"business_type": BusinessType.GOODS,
		"activity_type": "Торговля",
		"description": "Тест",
		"inn": f"{inn_seed:010d}",
		"ogrn": f"{inn_seed:013d}",
		"kpp": f"{(inn_seed % 10**9):09d}",
		"country": "Россия",
		"federal_district": "ЦФО",
		"region": "Москва",
		"city": "Москва",
		"full_name": f"ООО E8 {suffix}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000001",
		"email": f"e8-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.mark.asyncio
async def test_etap8_bill_replace_transport_closing():
	suffix = uuid4().hex[:8]
	seed = 7600000000 + int(suffix[:4], 16) % 80000000
	async with AsyncSessionLocal() as session:
		seller = Company(**_company_payload(f"s-{suffix}", seed, trade=TradeActivity.SELLER))
		buyer = Company(**_company_payload(f"b-{suffix}", seed + 1, trade=TradeActivity.SELLER))
		session.add_all([seller, buyer])
		await session.flush()
		user = User(
			email=f"e8-{suffix}@test.local",
			phone="+79009990044",
			first_name="E8",
			last_name="Test",
			hashed_password="x",
			company_id=seller.id,
			is_active=True,
		)
		order = Order(
			id=900000 + int(suffix[:4], 16) % 90000,
			version=1,
			buyer_order_number="00001",
			seller_order_number="00001",
			deal_type=OrderType.GOODS,
			status=OrderStatus.ACTIVE,
			buyer_company_id=buyer.id,
			seller_company_id=seller.id,
			bill_number="00001",
			bill_date=datetime.utcnow(),
			bill_reason="Старый счёт",
			total_amount=100.0,
			total_amount_word="сто",
			total_amount_excl_vat=100.0,
			amount_vat_rate=0.0,
		)
		session.add_all([user, order])
		await session.flush()
		session.add(
			OrderItem(
				order_row_id=order.row_id,
				product_name="Товар",
				product_slug="t",
				quantity=1,
				unit_of_measurement="шт",
				price=100.0,
				amount=100.0,
				position=1,
			)
		)
		await session.commit()
		seller_id, buyer_id, user_id, order_id, order_row_id = seller.id, buyer.id, user.id, order.id, order.row_id

	async def _override():
		async with AsyncSessionLocal() as session:
			return await session.get(User, user_id)

	app.dependency_overrides[get_current_user] = _override
	try:
		transport = ASGITransport(app=app)
		async with AsyncClient(transport=transport, base_url="http://test") as client:
			# replace bill
			rb = await client.post(
				f"/api/v1/purchases/deals/{order_id}/bill",
				json={"replace": True},
			)
			assert rb.status_code == 200, rb.text
			assert rb.json()["bill_number"] == "00001"

			get_deal = await client.get(f"/api/v1/purchases/deals/{order_id}")
			assert get_deal.status_code == 200
			deal = get_deal.json()
			assert deal["bill"]["reason"] == ""

			# transport contract
			rt = await client.post(
				f"/api/v1/purchases/deals/{order_id}/transport-contract",
				json={"number": "TE-100"},
			)
			assert rt.status_code == 200, rt.text
			assert rt.json()["number"] == "TE-100"

			get_deal2 = await client.get(f"/api/v1/purchases/deals/{order_id}")
			assert get_deal2.json().get("transport_contract", {}).get("number") == "TE-100"

			# closing document
			rc = await client.post(
				f"/api/v1/purchases/deals/{order_id}/closing-document",
				json={"doc_type": "UPD", "number": "12345"},
			)
			assert rc.status_code == 200, rc.text
			assert "УПД" in rc.json()["name"]

			get_deal3 = await client.get(f"/api/v1/purchases/deals/{order_id}")
			closing = get_deal3.json().get("closing_documents") or []
			assert len(closing) == 1
	finally:
		app.dependency_overrides.pop(get_current_user, None)
		async with AsyncSessionLocal() as session:
			await session.execute(delete(OrderItem).where(OrderItem.order_row_id == order_row_id))
			await session.execute(delete(Order).where(Order.row_id == order_row_id))
			await session.execute(delete(User).where(User.id == user_id))
			await session.execute(delete(Company).where(Company.id.in_([seller_id, buyer_id])))
			await session.commit()
