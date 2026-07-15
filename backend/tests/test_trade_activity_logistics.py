"""ТЗ_15 §5.2–§5.3: trade_activity и 403 для Перевозчик/Экспедитор."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.db.base import AsyncSessionLocal
from app.main import app


def _payload(suffix: str, inn_seed: int, trade: TradeActivity) -> dict:
	return {
		"name": f"Logistics Co {suffix}",
		"slug": f"logistics-co-{suffix}",
		"type": "ООО",
		"trade_activity": trade,
		"business_type": BusinessType.SERVICES,
		"activity_type": "Логистика",
		"description": "Тест",
		"country": "Россия",
		"federal_district": "ЦФО",
		"region": "Москва",
		"city": "Москва",
		"full_name": f"ООО Logistics {suffix}",
		"inn": f"{inn_seed:010d}",
		"ogrn": f"{inn_seed:013d}",
		"kpp": f"{(inn_seed % 10**9):09d}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000099",
		"email": f"logistics-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.fixture
async def carrier_context():
	unique = uuid4().hex[:8]
	data = _payload(unique, 7700000000 + int(unique[:4], 16) % 89999999, TradeActivity.CARRIER)

	async with AsyncSessionLocal() as session:
		company = Company(**data)
		session.add(company)
		await session.flush()
		user = User(
			email=f"carrier-{unique}@example.com",
			phone="+79009991122",
			first_name="Carrier",
			last_name="Test",
			hashed_password="test",
			is_active=True,
			company_id=company.id,
		)
		session.add(user)
		await session.commit()
		await session.refresh(company)
		await session.refresh(user)
		company_id = company.id
		user_id = user.id
		user_email = user.email

	async def override():
		async with AsyncSessionLocal() as session:
			return await session.get(User, user_id)

	app.dependency_overrides[get_current_user] = override
	try:
		yield {"user_id": user_id, "company_id": company_id, "email": user_email}
	finally:
		app.dependency_overrides.pop(get_current_user, None)
		async with AsyncSessionLocal() as session:
			await session.execute(delete(User).where(User.id == user_id))
			await session.execute(delete(Company).where(Company.id == company_id))
			await session.commit()


@pytest.mark.asyncio
async def test_trade_activity_enum_values():
	assert TradeActivity.PRODUCER.value == "Производитель"
	assert TradeActivity.SELLER.value == "Продавец"
	assert TradeActivity.CARRIER.value == "Перевозчик"
	assert TradeActivity.FORWARDER.value == "Экспедитор"
	assert TradeActivity.CARRIER.is_logistics_only
	assert TradeActivity.FORWARDER.is_logistics_only
	assert not TradeActivity.SELLER.is_logistics_only
	assert not TradeActivity.PRODUCER.is_logistics_only


@pytest.mark.asyncio
async def test_carrier_products_forbidden(carrier_context):
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://test") as client:
		resp = await client.get("/api/v1/me/products")
	assert resp.status_code == 403
	assert "Перевозчик" in resp.json()["detail"] or "Экспедитор" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_carrier_seller_deals_forbidden(carrier_context):
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://test") as client:
		resp = await client.get("/api/v1/purchases/seller/deals")
	assert resp.status_code == 403


@pytest.mark.asyncio
async def test_carrier_buyers_list_forbidden(carrier_context):
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://test") as client:
		resp = await client.get("/api/v1/company/me/buyers")
	assert resp.status_code == 403
