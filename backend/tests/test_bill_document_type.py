"""
Персистентность bill.document_type и галок реквизитов — этап 4.1.
"""
from datetime import datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.api.purchases.models import Order
from app.db.base import AsyncSessionLocal
from app.main import app


def _company_payload(suffix: str, inn_seed: int) -> dict:
	return {
		"name": f"BillType Co {suffix}",
		"slug": f"bill-type-co-{suffix}",
		"type": "ООО",
		"trade_activity": TradeActivity.SELLER,
		"business_type": BusinessType.BOTH,
		"activity_type": "Тест",
		"description": "Тест",
		"country": "Россия",
		"federal_district": "ЦФО",
		"region": "Москва",
		"city": "Москва",
		"full_name": f"ООО BillType {suffix}",
		"inn": f"{inn_seed:010d}",
		"ogrn": f"{inn_seed:013d}",
		"kpp": f"{(inn_seed % 10**9):09d}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000000",
		"email": f"bill-type-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.fixture
async def bill_type_context():
	unique = uuid4().hex[:8]
	buyer_data = _company_payload(
		f"b-{unique}", 1000000000 + int(unique[:4], 16) % 899999999
	)
	seller_data = _company_payload(
		f"s-{unique}", 2000000000 + int(unique[4:], 16) % 799999999
	)

	async with AsyncSessionLocal() as session:
		buyer_company = Company(**buyer_data)
		seller_company = Company(**seller_data)
		session.add_all([buyer_company, seller_company])
		await session.flush()

		buyer_user = User(
			email=f"buyer-bt-{unique}@example.com",
			phone="+79001112235",
			first_name="Buyer",
			last_name="BT",
			hashed_password="test",
			is_active=True,
			company_id=buyer_company.id,
		)
		seller_user = User(
			email=f"seller-bt-{unique}@example.com",
			phone="+79001112236",
			first_name="Seller",
			last_name="BT",
			hashed_password="test",
			is_active=True,
			company_id=seller_company.id,
		)
		session.add_all([buyer_user, seller_user])
		await session.commit()
		await session.refresh(buyer_user)
		await session.refresh(seller_user)

		context = {
			"buyer_user": buyer_user,
			"seller_user": seller_user,
			"buyer_company_id": buyer_company.id,
			"seller_company_id": seller_company.id,
			"current_user": buyer_user,
		}

	async def _override():
		return context["current_user"]

	app.dependency_overrides[get_current_user] = _override
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
	async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
		yield ac


def _set_user(context: dict, user: User) -> None:
	context["current_user"] = user

	async def _override():
		return context["current_user"]

	app.dependency_overrides[get_current_user] = _override


@pytest.mark.asyncio
async def test_bill_document_type_and_details_roundtrip(
	client: AsyncClient, bill_type_context: dict
):
	ctx = bill_type_context
	_set_user(ctx, ctx["buyer_user"])

	create_resp = await client.post(
		"/api/v1/purchases/deals",
		json={
			"seller_company_id": ctx["seller_company_id"],
			"deal_type": "Товары",
			"items": [
				{
					"article": None,
					"quantity": 1,
					"product_name": "Товар",
					"unit_of_measurement": "шт",
					"price": 100.0,
				}
			],
			"comments": "bill document_type test",
		},
	)
	assert create_resp.status_code == 200, create_resp.text
	deal_id = create_resp.json()["id"]
	assert create_resp.json()["bill"]["document_type"] == "bill"

	_set_user(ctx, ctx["seller_user"])
	put_resp = await client.put(
		f"/api/v1/purchases/deals/{deal_id}",
		json={
			"bill": {
				"document_type": "bill-contract",
				"supplier_details_check": False,
				"buyer_details_check": True,
				"contract_terms_text_contract": "Условия с {{ СРОК_ОПЛАТЫ }}",
			},
			"bill_date": "2026-07-14T00:00:00",
		},
	)
	assert put_resp.status_code == 200, put_resp.text
	updated = put_resp.json()
	assert updated["bill"]["document_type"] == "bill-contract"
	assert updated["bill"]["supplier_details_check"] is False
	assert updated["bill"]["buyer_details_check"] is True
	assert "{{ СРОК_ОПЛАТЫ }}" in updated["bill"]["contract_terms_text_contract"]

	get_resp = await client.get(f"/api/v1/purchases/deals/{deal_id}")
	assert get_resp.status_code == 200, get_resp.text
	bill = get_resp.json()["bill"]
	assert bill["document_type"] == "bill-contract"
	assert bill["supplier_details_check"] is False
	assert bill["buyer_details_check"] is True
	assert "{{ СРОК_ОПЛАТЫ }}" in bill["contract_terms_text_contract"]

	# Версия с другим типом
	version_resp = await client.post(
		f"/api/v1/purchases/deals/{deal_id}/versions",
		json={
			"bill": {
				"document_type": "bill-offer",
				"supplier_details_check": True,
				"buyer_details_check": False,
			},
		},
	)
	assert version_resp.status_code == 200, version_resp.text
	v2 = version_resp.json()
	assert v2["version"] == 2
	assert v2["bill"]["document_type"] == "bill-offer"
	assert v2["bill"]["supplier_details_check"] is True
	assert v2["bill"]["buyer_details_check"] is False
