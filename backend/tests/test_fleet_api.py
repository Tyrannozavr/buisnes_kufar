"""Тесты CRUD транспорта и водителей (ТЗ_15 ЛК)."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.authentication.dependencies import get_token_data
from app.api.authentication.models.user import User
from app.api.authentication.schemas.user import TokenData
from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.api.company.models.fleet import CompanyVehicle, CompanyDriver
from app.db.base import AsyncSessionLocal
from app.main import app


def _company_payload(suffix: str, inn_seed: int) -> dict:
	return {
		"name": f"Fleet Co {suffix}",
		"slug": f"fleet-co-{suffix}",
		"type": "ООО",
		"trade_activity": TradeActivity.CARRIER,
		"business_type": BusinessType.SERVICES,
		"activity_type": "Перевозки",
		"description": "Тест",
		"inn": f"{inn_seed:010d}",
		"ogrn": f"{inn_seed:013d}",
		"kpp": f"{(inn_seed % 10**9):09d}",
		"country": "Россия",
		"federal_district": "ЦФО",
		"region": "Москва",
		"city": "Москва",
		"full_name": f"ООО Fleet {suffix}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000001",
		"email": f"fleet-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.mark.asyncio
async def test_vehicles_and_drivers_crud():
	suffix = uuid4().hex[:8]
	seed = 7700000000 + int(suffix[:4], 16) % 80000000
	async with AsyncSessionLocal() as session:
		company = Company(**_company_payload(suffix, seed))
		session.add(company)
		await session.flush()
		user = User(
			email=f"fleet-{suffix}@test.local",
			phone="+79009991122",
			first_name="Fleet",
			last_name="Test",
			hashed_password="x",
			company_id=company.id,
			is_active=True,
		)
		session.add(user)
		await session.commit()
		user_id, company_id = user.id, company.id

	async def _override_token():
		return TokenData(user_id=user_id, email=f"fleet-{suffix}@test.local")

	app.dependency_overrides[get_token_data] = _override_token
	try:
		transport = ASGITransport(app=app)
		async with AsyncClient(transport=transport, base_url="http://test") as client:
			v = await client.post(
				"/api/v1/company/me/vehicles",
				json={
					"name": "Газель", "plate_number": "A111AA77", "capacity_tons": 1.5,
					"trailer_plate_number": "B222BB77", "body_type": "Тентованный",
					"loading_methods": ["Задняя"], "adr_classes": ["Класс 3 (ADR-3)"],
					"from_locations": [{"type": "city", "name": "Москва"}],
					"to_locations": [{"type": "city", "name": "Тула"}], "partial_load": True,
					"partial_load_weight_kg": 500,
				},
			)
			assert v.status_code == 201, v.text
			vid = v.json()["id"]
			assert v.json()["body_type"] == "Тентованный"
			assert v.json()["partial_load"] is True

			dictionaries = await client.get("/api/v1/company/fleet-dictionaries")
			assert dictionaries.status_code == 200
			assert "Тентованный" in dictionaries.json()["body_types"]

			lst = await client.get("/api/v1/company/me/vehicles")
			assert lst.status_code == 200
			assert any(x["id"] == vid for x in lst.json())

			upd = await client.put(
				f"/api/v1/company/me/vehicles/{vid}",
				json={"is_active": False},
			)
			assert upd.status_code == 200
			assert upd.json()["is_active"] is False

			d = await client.post(
				"/api/v1/company/me/drivers",
				json={"full_name": "Иванов И.И.", "phone": "+79001234567", "inn": "7701234567"},
			)
			assert d.status_code == 201, d.text
			did = d.json()["id"]
			assert d.json()["inn"] == "7701234567"

			dlst = await client.get("/api/v1/company/me/drivers")
			assert dlst.status_code == 200
			assert any(x["id"] == did for x in dlst.json())

			assert (await client.delete(f"/api/v1/company/me/drivers/{did}")).status_code == 200
			assert (await client.delete(f"/api/v1/company/me/vehicles/{vid}")).status_code == 200
	finally:
		app.dependency_overrides.pop(get_token_data, None)
		async with AsyncSessionLocal() as session:
			await session.execute(delete(CompanyDriver).where(CompanyDriver.company_id == company_id))
			await session.execute(delete(CompanyVehicle).where(CompanyVehicle.company_id == company_id))
			await session.execute(delete(User).where(User.id == user_id))
			await session.execute(delete(Company).where(Company.id == company_id))
			await session.commit()
