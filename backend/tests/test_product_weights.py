"""Веса товара и тип по умолчанию — этап 7.3 (ТЗ_15)."""
from datetime import datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.api.products.models.product import Product
from app.db.base import AsyncSessionLocal
from app.main import app


def _company_payload(suffix: str, inn_seed: int) -> dict:
	return {
		"name": f"Prod Co {suffix}",
		"slug": f"prod-co-{suffix}",
		"type": "ООО",
		"trade_activity": TradeActivity.SELLER,
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
		"full_name": f"ООО Prod {suffix}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000001",
		"email": f"prod-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.mark.asyncio
async def test_create_and_update_product_weights():
	suffix = uuid4().hex[:8]
	seed = 7900000000 + int(suffix[:4], 16) % 80000000
	async with AsyncSessionLocal() as session:
		company = Company(**_company_payload(suffix, seed))
		session.add(company)
		await session.flush()
		user = User(
			email=f"prod-{suffix}@test.local",
			phone="+79009990033",
			first_name="Prod",
			last_name="Test",
			hashed_password="x",
			company_id=company.id,
			is_active=True,
		)
		session.add(user)
		await session.commit()
		company_id, user_id = company.id, user.id

	async def _override():
		async with AsyncSessionLocal() as session:
			return await session.get(User, user_id)

	app.dependency_overrides[get_current_user] = _override
	product_id = None
	try:
		transport = ASGITransport(app=app)
		async with AsyncClient(transport=transport, base_url="http://test") as client:
			created = await client.post(
				"/api/v1/me/products",
				json={
					"name": f"Товар вес {suffix}",
					"article": f"ART-{suffix[:6]}",
					"price": 100.0,
					"unit_of_measurement": "кг",
					"net_weight": 1.5,
					"gross_weight": 1.8,
					"characteristics": [],
				},
			)
			assert created.status_code in (200, 201), created.text
			body = created.json()
			product_id = body["id"]
			assert body["type"] == "Товар"
			assert body["net_weight"] == 1.5
			assert body["gross_weight"] == 1.8

			updated = await client.put(
				f"/api/v1/me/products/{product_id}",
				json={
					"name": body["name"],
					"article": body["article"],
					"type": "Товар",
					"price": 100.0,
					"unit_of_measurement": "кг",
					"net_weight": 2.0,
					"gross_weight": None,
					"characteristics": [],
				},
			)
			assert updated.status_code == 200, updated.text
			assert updated.json()["net_weight"] == 2.0
			assert updated.json()["gross_weight"] is None
	finally:
		app.dependency_overrides.pop(get_current_user, None)
		async with AsyncSessionLocal() as session:
			if product_id:
				await session.execute(delete(Product).where(Product.id == product_id))
			await session.execute(delete(User).where(User.id == user_id))
			await session.execute(delete(Company).where(Company.id == company_id))
			await session.commit()
