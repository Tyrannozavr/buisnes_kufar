"""
Тесты API договоров компании (ЛК «Договоры») — этап 3.1.
"""
from datetime import datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.roles_positions import UserRole
from app.api.authentication.models.user import User
from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.api.purchases.models import CompanyContract
from app.db.base import AsyncSessionLocal
from app.main import app


def _company_payload(suffix: str, inn_seed: int, *, trade: TradeActivity) -> dict:
	return {
		"name": f"Contract Co {suffix}",
		"slug": f"contract-co-{suffix}",
		"type": "ООО",
		"trade_activity": trade,
		"business_type": BusinessType.GOODS,
		"activity_type": "Тест",
		"description": "Тест",
		"country": "Россия",
		"federal_district": "ЦФО",
		"region": "Москва",
		"city": "Москва",
		"full_name": f"ООО Contract {suffix}",
		"inn": f"{inn_seed:010d}",
		"ogrn": f"{inn_seed:013d}",
		"kpp": f"{(inn_seed % 10**9):09d}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000000",
		"email": f"contract-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.fixture
async def contract_pair():
	suffix = uuid4().hex[:8]
	seller_inn = int(uuid4().int % 9_000_000_000) + 1_000_000_000
	buyer_inn = seller_inn + 1
	seller_id: int | None = None
	buyer_id: int | None = None
	user_id: int | None = None

	async with AsyncSessionLocal() as session:
		seller = Company(**_company_payload(f"s-{suffix}", seller_inn, trade=TradeActivity.SELLER))
		buyer = Company(**_company_payload(f"b-{suffix}", buyer_inn, trade=TradeActivity.BUYER))
		session.add_all([seller, buyer])
		await session.flush()
		seller_id = seller.id
		buyer_id = buyer.id

		seller_user = User(
			email=f"seller-contract-{suffix}@example.com",
			phone="+79003334457",
			first_name="Contract",
			last_name="Seller",
			hashed_password="x",
			is_active=True,
			role=UserRole.OWNER,
			company_id=seller.id,
		)
		session.add(seller_user)
		await session.flush()
		user_id = seller_user.id

		session.add(
			CompanyContract(
				seller_company_id=seller.id,
				buyer_company_id=buyer.id,
				number="00042",
				date=datetime(2025, 4, 8),
			)
		)
		await session.commit()

		yield {
			"seller_user": seller_user,
			"seller_company_id": seller_id,
			"buyer_company_id": buyer_id,
		}

	async with AsyncSessionLocal() as cleanup:
		if seller_id is not None:
			await cleanup.execute(
				delete(CompanyContract).where(CompanyContract.seller_company_id == seller_id)
			)
		if user_id is not None:
			await cleanup.execute(delete(User).where(User.id == user_id))
		if seller_id is not None and buyer_id is not None:
			await cleanup.execute(delete(Company).where(Company.id.in_([seller_id, buyer_id])))
		await cleanup.commit()


@pytest.mark.asyncio
async def test_list_company_contracts_returns_counterparty_contracts(contract_pair):
	pair = contract_pair
	app.dependency_overrides[get_current_user] = lambda: pair["seller_user"]

	try:
		async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
			response = await client.get(
				"/api/v1/purchases/company-contracts",
				params={"counterparty_company_id": pair["buyer_company_id"]},
			)
	finally:
		app.dependency_overrides.pop(get_current_user, None)

	assert response.status_code == 200
	body = response.json()
	assert len(body["contracts"]) == 1
	assert body["contracts"][0]["number"] == "00042"
	assert body["contracts"][0]["buyer_company_id"] == pair["buyer_company_id"]
	assert body["contracts"][0]["counterparty_company_id"] == pair["buyer_company_id"]


@pytest.mark.asyncio
async def test_list_all_company_contracts(contract_pair):
	pair = contract_pair
	app.dependency_overrides[get_current_user] = lambda: pair["seller_user"]

	try:
		async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
			response = await client.get("/api/v1/purchases/company-contracts")
	finally:
		app.dependency_overrides.pop(get_current_user, None)

	assert response.status_code == 200
	assert len(response.json()["contracts"]) == 1


@pytest.mark.asyncio
async def test_create_update_delete_company_contract(contract_pair):
	pair = contract_pair
	app.dependency_overrides[get_current_user] = lambda: pair["seller_user"]

	try:
		async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
			create_resp = await client.post(
				"/api/v1/purchases/company-contracts",
				json={
					"counterparty_company_id": pair["buyer_company_id"],
					"number": "00099",
					"date": "2026-01-15T00:00:00",
					"relation": "as_seller",
				},
			)
			assert create_resp.status_code == 201
			created = create_resp.json()
			assert created["number"] == "00099"
			contract_id = created["id"]

			dup_resp = await client.post(
				"/api/v1/purchases/company-contracts",
				json={
					"counterparty_company_id": pair["buyer_company_id"],
					"number": "00099",
					"date": "2026-01-16T00:00:00",
					"relation": "as_seller",
				},
			)
			assert dup_resp.status_code == 409

			patch_resp = await client.patch(
				f"/api/v1/purchases/company-contracts/{contract_id}",
				json={"number": "00100"},
			)
			assert patch_resp.status_code == 200
			assert patch_resp.json()["number"] == "00100"

			delete_resp = await client.delete(
				f"/api/v1/purchases/company-contracts/{contract_id}",
			)
			assert delete_resp.status_code == 204
	finally:
		app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_list_company_contracts_empty_for_unknown_counterparty(contract_pair):
	pair = contract_pair
	app.dependency_overrides[get_current_user] = lambda: pair["seller_user"]

	try:
		async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
			response = await client.get(
				"/api/v1/purchases/company-contracts",
				params={"counterparty_company_id": 9_999_999},
			)
	finally:
		app.dependency_overrides.pop(get_current_user, None)

	assert response.status_code == 200
	assert response.json()["contracts"] == []


@pytest.mark.asyncio
async def test_get_next_company_contract_number_as_seller(contract_pair):
	pair = contract_pair
	app.dependency_overrides[get_current_user] = lambda: pair["seller_user"]

	try:
		async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
			response = await client.get(
				"/api/v1/purchases/company-contracts/next-number",
				params={"relation": "as_seller"},
			)
	finally:
		app.dependency_overrides.pop(get_current_user, None)

	assert response.status_code == 200
	body = response.json()
	assert body["number"] == "00001"
	assert "date" in body


@pytest.mark.asyncio
async def test_get_next_company_contract_number_as_buyer_requires_counterparty(contract_pair):
	pair = contract_pair
	app.dependency_overrides[get_current_user] = lambda: pair["seller_user"]

	try:
		async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
			response = await client.get(
				"/api/v1/purchases/company-contracts/next-number",
				params={"relation": "as_buyer"},
			)
	finally:
		app.dependency_overrides.pop(get_current_user, None)

	assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_company_contract_without_number_auto_generates(contract_pair):
	pair = contract_pair
	app.dependency_overrides[get_current_user] = lambda: pair["seller_user"]

	try:
		async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
			create_resp = await client.post(
				"/api/v1/purchases/company-contracts",
				json={
					"counterparty_company_id": pair["buyer_company_id"],
					"relation": "as_seller",
				},
			)
	finally:
		app.dependency_overrides.pop(get_current_user, None)

	assert create_resp.status_code == 201
	created = create_resp.json()
	assert created["number"] == "00001"
	assert created["buyer_company_id"] == pair["buyer_company_id"]
