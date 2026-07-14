"""
Тесты API шаблонов условий счёт-договора / оферты — этап 4.4.
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
from app.api.purchases.models import ContractConditionTemplate
from app.db.base import AsyncSessionLocal
from app.main import app


def _company_payload(suffix: str, inn_seed: int, *, trade: TradeActivity) -> dict:
	return {
		"name": f"Tpl Co {suffix}",
		"slug": f"tpl-co-{suffix}",
		"type": "ООО",
		"trade_activity": trade,
		"business_type": BusinessType.GOODS,
		"activity_type": "Тест",
		"description": "Тест",
		"country": "Россия",
		"federal_district": "ЦФО",
		"region": "Москва",
		"city": "Москва",
		"full_name": f"ООО Tpl {suffix}",
		"inn": f"{inn_seed:010d}",
		"ogrn": f"{inn_seed:013d}",
		"kpp": f"{(inn_seed % 10**9):09d}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000000",
		"email": f"tpl-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.fixture
async def template_pair():
	suffix = uuid4().hex[:8]
	seller_inn = int(uuid4().int % 9_000_000_000) + 1_000_000_000
	other_inn = seller_inn + 1
	seller_id: int | None = None
	other_id: int | None = None
	seller_user_id: int | None = None
	other_user_id: int | None = None

	async with AsyncSessionLocal() as session:
		seller = Company(**_company_payload(f"s-{suffix}", seller_inn, trade=TradeActivity.SELLER))
		other = Company(**_company_payload(f"o-{suffix}", other_inn, trade=TradeActivity.SELLER))
		session.add_all([seller, other])
		await session.flush()
		seller_id = seller.id
		other_id = other.id

		seller_user = User(
			email=f"seller-tpl-{suffix}@example.com",
			phone="+79003334458",
			first_name="Tpl",
			last_name="Seller",
			hashed_password="x",
			is_active=True,
			role=UserRole.OWNER,
			company_id=seller.id,
		)
		other_user = User(
			email=f"other-tpl-{suffix}@example.com",
			phone="+79003334459",
			first_name="Tpl",
			last_name="Other",
			hashed_password="x",
			is_active=True,
			role=UserRole.OWNER,
			company_id=other.id,
		)
		session.add_all([seller_user, other_user])
		await session.flush()
		seller_user_id = seller_user.id
		other_user_id = other_user.id
		await session.commit()

		yield {
			"seller_user": seller_user,
			"other_user": other_user,
			"seller_company_id": seller_id,
			"other_company_id": other_id,
		}

	async with AsyncSessionLocal() as cleanup:
		if seller_id is not None:
			await cleanup.execute(
				delete(ContractConditionTemplate).where(
					ContractConditionTemplate.company_id == seller_id
				)
			)
		if other_id is not None:
			await cleanup.execute(
				delete(ContractConditionTemplate).where(
					ContractConditionTemplate.company_id == other_id
				)
			)
		if seller_user_id is not None and other_user_id is not None:
			await cleanup.execute(
				delete(User).where(User.id.in_([seller_user_id, other_user_id]))
			)
		if seller_id is not None and other_id is not None:
			await cleanup.execute(delete(Company).where(Company.id.in_([seller_id, other_id])))
		await cleanup.commit()


@pytest.fixture
async def client():
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
		yield ac


@pytest.mark.asyncio
async def test_contract_condition_templates_crud_and_default(
	client: AsyncClient, template_pair: dict
):
	pair = template_pair
	app.dependency_overrides[get_current_user] = lambda: pair["seller_user"]

	try:
		create_default = await client.post(
			"/api/v1/purchases/contract-condition-templates",
			json={
				"type": "bill_contract",
				"name": "Стандартный, доставка Поставщика",
				"content_text": "1. Условие {{ СРОК_ОПЛАТЫ }}\n2. {{ СРОК_ПОСТАВКИ }}",
				"is_default": True,
			},
		)
		assert create_default.status_code == 200, create_default.text
		default_tpl = create_default.json()
		assert default_tpl["is_default"] is True
		assert default_tpl["company_id"] == pair["seller_company_id"]
		default_id = default_tpl["id"]

		create_other = await client.post(
			"/api/v1/purchases/contract-condition-templates",
			json={
				"type": "bill_contract",
				"name": "Стандартный, доставка Покупателя",
				"content_text": "Покупатель доставляет",
				"is_default": False,
			},
		)
		assert create_other.status_code == 200, create_other.text
		other_id = create_other.json()["id"]

		listed = await client.get(
			"/api/v1/purchases/contract-condition-templates",
			params={"type": "bill_contract"},
		)
		assert listed.status_code == 200
		names = {t["name"] for t in listed.json()}
		assert "Стандартный, доставка Поставщика" in names
		assert "Стандартный, доставка Покупателя" in names

		default_resp = await client.get(
			"/api/v1/purchases/contract-condition-templates/default",
			params={"type": "bill_contract"},
		)
		assert default_resp.status_code == 200
		assert default_resp.json()["id"] == default_id

		# Переназначить default
		patch_resp = await client.patch(
			f"/api/v1/purchases/contract-condition-templates/{other_id}",
			json={"is_default": True, "content_text": "Обновлённый текст"},
		)
		assert patch_resp.status_code == 200, patch_resp.text
		assert patch_resp.json()["is_default"] is True
		assert patch_resp.json()["content_text"] == "Обновлённый текст"

		new_default = await client.get(
			"/api/v1/purchases/contract-condition-templates/default",
			params={"type": "bill_contract"},
		)
		assert new_default.json()["id"] == other_id

		delete_resp = await client.delete(
			f"/api/v1/purchases/contract-condition-templates/{default_id}"
		)
		assert delete_resp.status_code == 204

		listed_after = await client.get(
			"/api/v1/purchases/contract-condition-templates",
			params={"type": "bill_contract"},
		)
		ids = {t["id"] for t in listed_after.json()}
		assert default_id not in ids
		assert other_id in ids
	finally:
		app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_contract_condition_templates_company_scoped(
	client: AsyncClient, template_pair: dict
):
	pair = template_pair
	app.dependency_overrides[get_current_user] = lambda: pair["seller_user"]

	try:
		created = await client.post(
			"/api/v1/purchases/contract-condition-templates",
			json={
				"type": "bill_offer",
				"name": "Секретный шаблон",
				"content_text": "private",
				"is_default": True,
			},
		)
		assert created.status_code == 200, created.text
		template_id = created.json()["id"]

		app.dependency_overrides[get_current_user] = lambda: pair["other_user"]
		listed = await client.get(
			"/api/v1/purchases/contract-condition-templates",
			params={"type": "bill_offer"},
		)
		assert listed.status_code == 200
		assert all(t["id"] != template_id for t in listed.json())

		patch = await client.patch(
			f"/api/v1/purchases/contract-condition-templates/{template_id}",
			json={"name": "взлом"},
		)
		assert patch.status_code == 404

		delete = await client.delete(
			f"/api/v1/purchases/contract-condition-templates/{template_id}"
		)
		assert delete.status_code == 404
	finally:
		app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_contract_condition_templates_invalid_type(
	client: AsyncClient, template_pair: dict
):
	pair = template_pair
	app.dependency_overrides[get_current_user] = lambda: pair["seller_user"]

	try:
		create_resp = await client.post(
			"/api/v1/purchases/contract-condition-templates",
			json={
				"type": "invalid_type",
				"name": "Bad",
				"content_text": "x",
			},
		)
		assert create_resp.status_code == 400

		list_resp = await client.get(
			"/api/v1/purchases/contract-condition-templates",
			params={"type": "not-a-type"},
		)
		assert list_resp.status_code == 400

		default_resp = await client.get(
			"/api/v1/purchases/contract-condition-templates/default",
			params={"type": "bill"},
		)
		assert default_resp.status_code == 400
	finally:
		app.dependency_overrides.pop(get_current_user, None)
