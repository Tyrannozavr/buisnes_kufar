"""API контрагентов / перевозчиков — этап 6 (ТЗ_15)."""
from datetime import datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.api.company.models.company import CompanyRelation
from app.db.base import AsyncSessionLocal
from app.main import app


def _company_payload(suffix: str, inn_seed: int, *, trade: TradeActivity) -> dict:
	return {
		"name": f"CP Co {suffix}",
		"slug": f"cp-co-{suffix}",
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
		"full_name": f"ООО CP {suffix}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000001",
		"email": f"cp-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.mark.asyncio
async def test_add_counterparty_and_list_carriers_and_counterparties():
	suffix = uuid4().hex[:8]
	seed = 7700000000 + int(suffix[:4], 16) % 80000000
	async with AsyncSessionLocal() as session:
		owner = Company(**_company_payload(f"own-{suffix}", seed, trade=TradeActivity.SELLER))
		buyer = Company(**_company_payload(f"buy-{suffix}", seed + 1, trade=TradeActivity.SELLER))
		carrier = Company(**_company_payload(f"car-{suffix}", seed + 2, trade=TradeActivity.CARRIER))
		session.add_all([owner, buyer, carrier])
		await session.flush()
		user = User(
			email=f"cp-{suffix}@test.local",
			phone="+79009990011",
			first_name="Cp",
			last_name="Test",
			hashed_password="x",
			company_id=owner.id,
			is_active=True,
		)
		session.add(user)
		await session.commit()
		owner_id, buyer_id, carrier_id, user_id = owner.id, buyer.id, carrier.id, user.id

	async def _override():
		async with AsyncSessionLocal() as session:
			return await session.get(User, user_id)

	app.dependency_overrides[get_current_user] = _override
	try:
		transport = ASGITransport(app=app)
		async with AsyncClient(transport=transport, base_url="http://test") as client:
			r1 = await client.post(
				"/api/v1/company/me/counterparties/add",
				params={"related_company_id": buyer_id, "as_buyer": True},
			)
			assert r1.status_code == 200, r1.text

			r2 = await client.post(
				"/api/v1/company/me/counterparties/add",
				params={"related_company_id": carrier_id, "as_carrier": True},
			)
			assert r2.status_code == 200, r2.text

			cp = await client.get("/api/v1/company/me/counterparties", params={"per_page": 50})
			assert cp.status_code == 200
			ids = {c["id"] for c in cp.json()["data"]}
			assert buyer_id in ids
			assert carrier_id in ids

			carriers = await client.get("/api/v1/company/me/carriers", params={"per_page": 50})
			assert carriers.status_code == 200
			carrier_ids = {c["id"] for c in carriers.json()["data"]}
			assert carrier_id in carrier_ids
			assert buyer_id not in carrier_ids

			rm = await client.delete(f"/api/v1/company/me/counterparties/{carrier_id}")
			assert rm.status_code == 200
			carriers2 = await client.get("/api/v1/company/me/carriers")
			assert carrier_id not in {c["id"] for c in carriers2.json()["data"]}
	finally:
		app.dependency_overrides.pop(get_current_user, None)
		async with AsyncSessionLocal() as session:
			await session.execute(delete(CompanyRelation).where(CompanyRelation.company_id == owner_id))
			await session.execute(delete(User).where(User.id == user_id))
			await session.execute(delete(Company).where(Company.id.in_([owner_id, buyer_id, carrier_id])))
			await session.commit()
