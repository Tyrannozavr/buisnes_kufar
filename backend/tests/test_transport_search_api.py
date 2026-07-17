"""Поиск транспорта: /companies/services/search по ИНН / названию / городу."""
from datetime import datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.db.base import AsyncSessionLocal
from app.main import app


def _payload(suffix: str, inn: str, *, trade: TradeActivity, city: str = "Москва") -> dict:
	return {
		"name": f"TS Co {suffix}",
		"slug": f"ts-co-{suffix}",
		"type": "ООО",
		"trade_activity": trade,
		"business_type": BusinessType.SERVICES,
		"activity_type": "Логистика",
		"description": "Тест поиска транспорта",
		"inn": inn,
		"ogrn": f"{inn}00"[:13].ljust(13, "0"),
		"kpp": "770701001",
		"country": "Россия",
		"federal_district": "ЦФО",
		"region": "Москва",
		"city": city,
		"full_name": f"ООО Транспорт {suffix}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000001",
		"email": f"ts-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.mark.asyncio
async def test_services_search_by_inn_partial_and_name():
	suffix = uuid4().hex[:8]
	inn = f"77{int(suffix[:6], 16) % 10**8:08d}"[:10]
	async with AsyncSessionLocal() as session:
		carrier = Company(**_payload(f"car-{suffix}", inn, trade=TradeActivity.CARRIER, city="Казань"))
		seller = Company(
			**_payload(f"sel-{suffix}", f"{(int(inn) + 1) % 10**10:010d}", trade=TradeActivity.SELLER)
		)
		session.add_all([carrier, seller])
		await session.commit()
		carrier_id, seller_id = carrier.id, seller.id

	try:
		transport = ASGITransport(app=app)
		async with AsyncClient(transport=transport, base_url="http://test") as client:
			# полный ИНН
			r_full = await client.post(
				"/api/v1/companies/services/search",
				json={"search": inn, "skip": 0, "limit": 50},
			)
			assert r_full.status_code == 200, r_full.text
			ids_full = {c["id"] for c in r_full.json()["data"]}
			assert carrier_id in ids_full
			assert seller_id not in ids_full

			# частичный ИНН
			r_part = await client.post(
				"/api/v1/companies/services/search",
				json={"search": inn[:6], "skip": 0, "limit": 50},
			)
			assert r_part.status_code == 200, r_part.text
			assert carrier_id in {c["id"] for c in r_part.json()["data"]}

			# название (частичное)
			r_name = await client.post(
				"/api/v1/companies/services/search",
				json={"search": f"car-{suffix}", "skip": 0, "limit": 50},
			)
			assert r_name.status_code == 200, r_name.text
			assert carrier_id in {c["id"] for c in r_name.json()["data"]}

			# город
			r_city = await client.post(
				"/api/v1/companies/services/search",
				json={"search": "Казань", "skip": 0, "limit": 50},
			)
			assert r_city.status_code == 200, r_city.text
			assert carrier_id in {c["id"] for c in r_city.json()["data"]}
	finally:
		async with AsyncSessionLocal() as session:
			await session.execute(delete(Company).where(Company.id.in_([carrier_id, seller_id])))
			await session.commit()
