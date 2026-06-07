"""
Тесты API договоров поставки и спецификаций.
"""
import pytest
from uuid import uuid4
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.api.authentication.dependencies import get_current_user
from app.api.company.models.company import Company, TradeActivity, BusinessType
from tests.test_purchases_deals_api import _company_payload


@pytest.fixture
async def supply_contract_context():
	unique = uuid4().hex[:8]
	buyer_data = _company_payload(f"buyer-sc-{unique}", 3000000000 + int(unique[:4], 16) % 699999999)
	seller_data = _company_payload(f"seller-sc-{unique}", 4000000000 + int(unique[4:], 16) % 599999999)

	from app.db.base import AsyncSessionLocal

	async with AsyncSessionLocal() as session:
		buyer_company = Company(**buyer_data)
		seller_company = Company(**seller_data)
		session.add_all([buyer_company, seller_company])
		await session.flush()

		from app.api.authentication.models.user import User

		user = User(
			email=f"sc-user-{unique}@example.com",
			phone="+79003334455",
			first_name="SC",
			last_name="User",
			hashed_password="test",
			is_active=True,
			company_id=buyer_company.id,
		)
		session.add(user)
		await session.commit()
		await session.refresh(user)
		await session.refresh(buyer_company)
		await session.refresh(seller_company)

		yield {
			"user": user,
			"buyer_company_id": buyer_company.id,
			"seller_company_id": seller_company.id,
		}


@pytest.fixture
async def client(supply_contract_context):
	user = supply_contract_context["user"]

	async def override_get_current_user():
		return user

	app.dependency_overrides[get_current_user] = override_get_current_user
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://test") as async_client:
		yield async_client
	app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_supply_contract_create_get_exists_and_spec(client, supply_contract_context):
	buyer_id = supply_contract_context["buyer_company_id"]
	seller_id = supply_contract_context["seller_company_id"]

	exists_before = await client.get(
		"/api/v1/purchases/supply-contracts/exists",
		params={"buyer_company_id": buyer_id, "seller_company_id": seller_id},
	)
	assert exists_before.status_code == 200
	assert exists_before.json()["is_exist"] is False

	create_resp = await client.post(
		"/api/v1/purchases/supply-contracts",
		json={"buyer_company_id": buyer_id, "seller_company_id": seller_id},
	)
	assert create_resp.status_code == 200
	contract = create_resp.json()
	assert contract["buyer_company_id"] == buyer_id
	assert contract["seller_company_id"] == seller_id
	assert contract["number"]

	dup_resp = await client.post(
		"/api/v1/purchases/supply-contracts",
		json={"buyer_company_id": buyer_id, "seller_company_id": seller_id},
	)
	assert dup_resp.status_code == 409

	exists_after = await client.get(
		"/api/v1/purchases/supply-contracts/exists",
		params={"buyer_company_id": buyer_id, "seller_company_id": seller_id},
	)
	assert exists_after.status_code == 200
	assert exists_after.json()["is_exist"] is True

	get_resp = await client.get(f"/api/v1/purchases/supply-contracts/{contract['id']}")
	assert get_resp.status_code == 200

	patch_resp = await client.patch(
		f"/api/v1/purchases/supply-contracts/{contract['id']}",
		json={"terms_text": "Условия договора"},
	)
	assert patch_resp.status_code == 200
	assert patch_resp.json()["terms_text"] == "Условия договора"

	spec_resp = await client.post(f"/api/v1/purchases/supply-contracts/{contract['id']}/specifications")
	assert spec_resp.status_code == 200
	spec = spec_resp.json()
	assert spec["supply_contract_id"] == contract["id"]
	assert spec["supply_contract_number"] == contract["number"]

	update_spec_resp = await client.patch(
		f"/api/v1/purchases/supply-specifications/{spec['id']}",
		json={
			"spec_text": "Спецификация №1",
			"spec_items": [
				{
					"name": "Товар 1",
					"article": "ART-1",
					"quantity": 2,
					"units": "шт",
					"price": 100.0,
					"amount": 200.0,
				}
			],
		},
	)
	assert update_spec_resp.status_code == 200
	updated_spec = update_spec_resp.json()
	assert updated_spec["spec_text"] == "Спецификация №1"
	assert len(updated_spec["spec_items"]) == 1

	get_spec_resp = await client.get(f"/api/v1/purchases/supply-specifications/{spec['id']}")
	assert get_spec_resp.status_code == 200


@pytest.mark.asyncio
async def test_supply_contract_forbidden_for_outsider(client, supply_contract_context):
	buyer_id = supply_contract_context["buyer_company_id"]
	seller_id = supply_contract_context["seller_company_id"]

	create_resp = await client.post(
		"/api/v1/purchases/supply-contracts",
		json={"buyer_company_id": buyer_id, "seller_company_id": seller_id},
	)
	contract_id = create_resp.json()["id"]

	from app.db.base import AsyncSessionLocal

	unique = uuid4().hex[:8]
	outsider_data = _company_payload(f"outsider-{unique}", 5000000000 + int(unique[:6], 16) % 499999999)

	async with AsyncSessionLocal() as session:
		outsider_company = Company(**outsider_data)
		session.add(outsider_company)
		await session.flush()

		from app.api.authentication.models.user import User

		outsider_user = User(
			email=f"outsider-{unique}@example.com",
			phone="+79005556677",
			first_name="Out",
			last_name="Sider",
			hashed_password="test",
			is_active=True,
			company_id=outsider_company.id,
		)
		session.add(outsider_user)
		await session.commit()
		await session.refresh(outsider_user)

	async def override_outsider():
		return outsider_user

	app.dependency_overrides[get_current_user] = override_outsider

	get_resp = await client.get(f"/api/v1/purchases/supply-contracts/{contract_id}")
	assert get_resp.status_code == 403

	app.dependency_overrides.clear()
