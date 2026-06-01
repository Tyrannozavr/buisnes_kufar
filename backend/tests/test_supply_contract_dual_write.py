"""Тесты dual-write и read-switch supply contract ↔ order."""
import pytest
from uuid import uuid4
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.api.authentication.dependencies import get_current_user
from app.api.company.models.company import Company
from tests.test_purchases_deals_api import _company_payload, _valid_deal_payload


@pytest.fixture
async def dual_write_context():
	unique = uuid4().hex[:8]
	buyer_data = _company_payload(f"buyer-dw-{unique}", 3100000000 + int(unique[:4], 16) % 699999999)
	seller_data = _company_payload(f"seller-dw-{unique}", 4100000000 + int(unique[4:], 16) % 599999999)

	from app.db.base import AsyncSessionLocal

	async with AsyncSessionLocal() as session:
		buyer = Company(**buyer_data)
		seller = Company(**seller_data)
		session.add_all([buyer, seller])
		await session.flush()

		from app.api.authentication.models.user import User

		user = User(
			email=f"dw-{unique}@example.com",
			phone="+79001112233",
			first_name="DW",
			last_name="User",
			hashed_password="test",
			is_active=True,
			company_id=buyer.id,
		)
		session.add(user)
		await session.commit()
		await session.refresh(user)
		await session.refresh(buyer)
		await session.refresh(seller)

		yield {
			"user": user,
			"buyer_id": buyer.id,
			"seller_id": seller.id,
		}


@pytest.fixture
async def client(dual_write_context):
	user = dual_write_context["user"]

	async def override_get_current_user():
		return user

	app.dependency_overrides[get_current_user] = override_get_current_user
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://test") as async_client:
		yield async_client
	app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_assign_supply_contract_creates_entity_and_read_switch(client, dual_write_context):
	seller_id = dual_write_context["seller_id"]

	create_deal = await client.post(
		"/api/v1/purchases/deals",
		json=_valid_deal_payload(seller_id),
	)
	assert create_deal.status_code == 200
	deal = create_deal.json()
	deal_id = deal["id"]

	assign = await client.post(f"/api/v1/purchases/deals/{deal_id}/supply-contract")
	assert assign.status_code == 200
	number = assign.json()["supply_contract_number"]

	get_deal = await client.get(f"/api/v1/purchases/deals/{deal_id}")
	assert get_deal.status_code == 200
	payload = get_deal.json()
	assert payload["supply_contract"]["number"] == number
	assert payload["supply_contract"]["entity_id"] is not None

	exists = await client.get(
		"/api/v1/purchases/supply-contracts/exists",
		params={
			"buyer_company_id": dual_write_context["buyer_id"],
			"seller_company_id": seller_id,
		},
	)
	assert exists.status_code == 200
	assert exists.json()["is_exist"] is True


@pytest.mark.asyncio
async def test_supply_contract_get_not_found(client, dual_write_context):
	resp = await client.get("/api/v1/purchases/supply-contracts/999999")
	assert resp.status_code == 404


@pytest.mark.asyncio
async def test_bind_deal_to_supply_contract(client, dual_write_context):
	buyer_id = dual_write_context["buyer_id"]
	seller_id = dual_write_context["seller_id"]

	create_deal = await client.post(
		"/api/v1/purchases/deals",
		json=_valid_deal_payload(seller_id),
	)
	deal_id = create_deal.json()["id"]

	contract = await client.post(
		"/api/v1/purchases/supply-contracts",
		json={"buyer_company_id": buyer_id, "seller_company_id": seller_id},
	)
	assert contract.status_code == 200
	contract_id = contract.json()["id"]

	bind = await client.post(
		f"/api/v1/purchases/deals/{deal_id}/supply-contract-entity/bind",
		json={"contract_id": contract_id},
	)
	assert bind.status_code == 200
	assert bind.json()["bound"] is True

	get_deal = await client.get(f"/api/v1/purchases/deals/{deal_id}")
	assert get_deal.json()["supply_contract"]["entity_id"] == contract_id
