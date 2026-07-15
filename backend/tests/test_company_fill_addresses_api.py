"""API адресов заполнения — этап 7.2 (ТЗ_15)."""
from datetime import datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.api.company.models.fill_address import CompanyFillAddress, FillAddressKind
from app.db.base import AsyncSessionLocal
from app.main import app


def _company_payload(suffix: str, inn_seed: int) -> dict:
	return {
		"name": f"Fill Co {suffix}",
		"slug": f"fill-co-{suffix}",
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
		"full_name": f"ООО Fill {suffix}",
		"registration_date": datetime.utcnow(),
		"legal_address": "ул. Тест, 1",
		"production_address": "ул. Тест, 2",
		"phone": "+79000000001",
		"email": f"fill-{suffix}@example.com",
		"website": "https://example.com",
		"is_active": True,
	}


@pytest.mark.asyncio
async def test_fill_addresses_crud_default_rules():
	suffix = uuid4().hex[:8]
	seed = 7800000000 + int(suffix[:4], 16) % 80000000
	async with AsyncSessionLocal() as session:
		owner = Company(**_company_payload(f"own-{suffix}", seed))
		other = Company(**_company_payload(f"oth-{suffix}", seed + 1))
		session.add_all([owner, other])
		await session.flush()
		user = User(
			email=f"fill-{suffix}@test.local",
			phone="+79009990022",
			first_name="Fill",
			last_name="Test",
			hashed_password="x",
			company_id=owner.id,
			is_active=True,
		)
		session.add(user)
		await session.commit()
		owner_id, other_id, user_id = owner.id, other.id, user.id

	async def _override():
		async with AsyncSessionLocal() as session:
			return await session.get(User, user_id)

	app.dependency_overrides[get_current_user] = _override
	try:
		transport = ASGITransport(app=app)
		async with AsyncClient(transport=transport, base_url="http://test") as client:
			# Первый адрес loading → default
			r1 = await client.post(
				"/api/v1/company/me/fill-addresses",
				json={"kind": "loading", "address": "Склад А, ул. Погрузки 1"},
			)
			assert r1.status_code == 201, r1.text
			a1 = r1.json()
			assert a1["is_default"] is True
			assert a1["kind"] == "loading"
			id1 = a1["id"]

			# Второй без флага — не default
			r2 = await client.post(
				"/api/v1/company/me/fill-addresses",
				json={"kind": "loading", "address": "Склад Б, ул. Погрузки 2"},
			)
			assert r2.status_code == 201, r2.text
			a2 = r2.json()
			assert a2["is_default"] is False
			id2 = a2["id"]

			# Назначить default второму
			rd = await client.patch(f"/api/v1/company/me/fill-addresses/{id2}/default")
			assert rd.status_code == 200, rd.text
			assert rd.json()["is_default"] is True

			lst = await client.get("/api/v1/company/me/fill-addresses", params={"kind": "loading"})
			assert lst.status_code == 200
			by_id = {row["id"]: row for row in lst.json()}
			assert by_id[id2]["is_default"] is True
			assert by_id[id1]["is_default"] is False

			# Receiving независимо
			rr = await client.post(
				"/api/v1/company/me/fill-addresses",
				json={"kind": "receiving", "address": "Приёмка, ворота 3"},
			)
			assert rr.status_code == 201, rr.text
			assert rr.json()["is_default"] is True
			rid = rr.json()["id"]

			# Чужой адрес — 404
			async with AsyncSessionLocal() as session:
				foreign = CompanyFillAddress(
					company_id=other_id,
					kind=FillAddressKind.LOADING,
					address="Чужой",
					is_default=True,
				)
				session.add(foreign)
				await session.commit()
				foreign_id = foreign.id

			bad = await client.delete(f"/api/v1/company/me/fill-addresses/{foreign_id}")
			assert bad.status_code == 404

			# Удаление default loading → оставшийся становится default
			rm = await client.delete(f"/api/v1/company/me/fill-addresses/{id2}")
			assert rm.status_code == 200
			lst2 = await client.get("/api/v1/company/me/fill-addresses", params={"kind": "loading"})
			left = lst2.json()
			assert len(left) == 1
			assert left[0]["id"] == id1
			assert left[0]["is_default"] is True

			upd = await client.put(
				f"/api/v1/company/me/fill-addresses/{rid}",
				json={"address": "Приёмка, ворота 3 (обновл.)"},
			)
			assert upd.status_code == 200
			assert "обновл" in upd.json()["address"]
	finally:
		app.dependency_overrides.pop(get_current_user, None)
		async with AsyncSessionLocal() as session:
			await session.execute(
				delete(CompanyFillAddress).where(
					CompanyFillAddress.company_id.in_([owner_id, other_id])
				)
			)
			await session.execute(delete(User).where(User.id == user_id))
			await session.execute(delete(Company).where(Company.id.in_([owner_id, other_id])))
			await session.commit()
