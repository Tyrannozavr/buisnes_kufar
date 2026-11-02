"""API §1.2 — реестр документов перевозки / экспедиции."""
from datetime import datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.company.models.company import (
	BusinessType,
	Company,
	CompanyRelation,
	CompanyRelationType,
	TradeActivity,
)
from app.api.purchases.models import Order, OrderStatus, OrderType, TransportDocument
from app.db.base import AsyncSessionLocal
from app.main import app


def _company_payload(suffix: str, inn_seed: int, *, trade: TradeActivity) -> dict:
	return {
		"name": f"TD Co {suffix}",
		"slug": f"td-co-{suffix}",
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
		"full_name": f"ООО TD {suffix}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000001",
		"email": f"td-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.mark.asyncio
async def test_transport_document_create_list_bind_application():
	suffix = uuid4().hex[:8]
	seed = 8100000000 + int(suffix[:4], 16) % 80000000
	async with AsyncSessionLocal() as session:
		seller = Company(**_company_payload(f"s-{suffix}", seed, trade=TradeActivity.SELLER))
		buyer = Company(**_company_payload(f"b-{suffix}", seed + 1, trade=TradeActivity.SELLER))
		carrier = Company(
			**_company_payload(f"c-{suffix}", seed + 2, trade=TradeActivity.CARRIER)
		)
		session.add_all([seller, buyer, carrier])
		await session.flush()
		session.add(
			CompanyRelation(
				company_id=seller.id,
				related_company_id=carrier.id,
				relation_type=CompanyRelationType.CARRIER,
			)
		)
		user = User(
			email=f"td-{suffix}@test.local",
			phone="+79009990111",
			first_name="TD",
			last_name="Test",
			hashed_password="x",
			company_id=seller.id,
			is_active=True,
		)
		deal_id = 910000 + int(suffix[:4], 16) % 90000
		order = Order(
			id=deal_id,
			version=1,
			buyer_order_number="00001",
			seller_order_number="00001",
			deal_type=OrderType.GOODS,
			status=OrderStatus.ACTIVE,
			buyer_company_id=buyer.id,
			seller_company_id=seller.id,
			total_amount=100.0,
			total_amount_word="сто",
			total_amount_excl_vat=100.0,
			amount_vat_rate=0.0,
		)
		session.add_all([user, order])
		await session.commit()
		seller_id = seller.id
		buyer_id = buyer.id
		carrier_id = carrier.id
		user_id = user.id
		order_row_id = order.row_id

	async def _override_user():
		async with AsyncSessionLocal() as session:
			return await session.get(User, user_id)

	app.dependency_overrides[get_current_user] = _override_user
	try:
		transport = ASGITransport(app=app)
		async with AsyncClient(transport=transport, base_url="http://test") as client:
			created = await client.post(
				"/api/v1/purchases/transport-documents",
				json={
					"doc_type": "carriage_contract",
					"carrier_company_id": carrier_id,
					"number": "999",
				},
			)
			assert created.status_code == 200, created.text
			contract = created.json()
			assert contract["doc_type"] == "carriage_contract"
			assert contract["number"] == "999"
			assert contract["carrier_company_id"] == carrier_id

			picker = await client.get(
				"/api/v1/purchases/transport-documents",
				params={
					"carrier_company_id": carrier_id,
					"doc_type": "carriage_contract",
				},
			)
			assert picker.status_code == 200, picker.text
			assert any(d["id"] == contract["id"] for d in picker.json()["documents"])

			next_app = await client.get(
				"/api/v1/purchases/transport-documents/next-number",
				params={
					"doc_type": "carriage_application",
					"carrier_company_id": carrier_id,
					"parent_id": contract["id"],
				},
			)
			assert next_app.status_code == 200, next_app.text
			assert next_app.json()["number"] == "1"

			app_doc = await client.post(
				"/api/v1/purchases/transport-documents",
				json={
					"doc_type": "carriage_application",
					"carrier_company_id": carrier_id,
					"parent_id": contract["id"],
				},
			)
			assert app_doc.status_code == 200, app_doc.text
			assert app_doc.json()["number"] == "1"
			assert app_doc.json()["parent_id"] == contract["id"]

			bind_c = await client.post(
				f"/api/v1/purchases/deals/{deal_id}/transport-documents/bind",
				json={"document_id": contract["id"]},
			)
			assert bind_c.status_code == 200, bind_c.text

			bind_a = await client.post(
				f"/api/v1/purchases/deals/{deal_id}/transport-documents/bind",
				json={"document_id": app_doc.json()["id"]},
			)
			assert bind_a.status_code == 200, bind_a.text

			listed = await client.get(
				f"/api/v1/purchases/deals/{deal_id}/transport-documents"
			)
			assert listed.status_code == 200, listed.text
			types = {d["doc_type"] for d in listed.json()["documents"]}
			assert "carriage_contract" in types
			assert "carriage_application" in types

			deal = await client.get(f"/api/v1/purchases/deals/{deal_id}")
			assert deal.status_code == 200, deal.text
			tc = deal.json().get("transport_contract") or {}
			assert tc.get("number") == "999"
			assert tc.get("type") == "carriage_contract"
			assert len(tc.get("documents") or []) >= 2

			order_doc = await client.post(
				"/api/v1/purchases/transport-documents",
				json={
					"doc_type": "carriage_order",
					"carrier_company_id": carrier_id,
				},
			)
			assert order_doc.status_code == 200, order_doc.text
			assert order_doc.json()["number"] == "000001"

			bad = await client.post(
				"/api/v1/purchases/transport-documents",
				json={
					"doc_type": "carriage_application",
					"carrier_company_id": carrier_id,
				},
			)
			assert bad.status_code == 400

			# §2 — PATCH бланка (номер / payload_json)
			patched = await client.patch(
				f"/api/v1/purchases/transport-documents/{contract['id']}",
				json={
					"number": "999-А",
					"payload_json": {
						"city": "Москва",
						"bodyHtml": "<p>1. Предмет</p>",
						"customer": {"fullName": "ООО Заказчик", "companyType": "ООО"},
						"carrier": {"fullName": "ООО Перевозчик", "companyType": "ООО"},
						"customerDetailsCheck": True,
						"carrierDetailsCheck": True,
					},
				},
			)
			assert patched.status_code == 200, patched.text
			body = patched.json()
			assert body["number"] == "999-А"
			assert body["payload_json"]["city"] == "Москва"
			assert body["payload_json"]["customer"]["fullName"] == "ООО Заказчик"

			got = await client.get(
				f"/api/v1/purchases/transport-documents/{contract['id']}"
			)
			assert got.status_code == 200, got.text
			assert got.json()["payload_json"]["bodyHtml"] == "<p>1. Предмет</p>"
	finally:
		app.dependency_overrides.pop(get_current_user, None)
		async with AsyncSessionLocal() as session:
			await session.execute(
				delete(TransportDocument).where(
					TransportDocument.owner_company_id == seller_id
				)
			)
			await session.execute(delete(Order).where(Order.row_id == order_row_id))
			await session.execute(delete(User).where(User.id == user_id))
			await session.execute(
				delete(CompanyRelation).where(CompanyRelation.company_id == seller_id)
			)
			await session.execute(
				delete(Company).where(Company.id.in_([seller_id, buyer_id, carrier_id]))
			)
			await session.commit()
