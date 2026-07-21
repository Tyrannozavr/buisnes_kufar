"""Carrier transport API flow: search, request, acceptance, shipment and favorites."""
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.chats.models.chat_participant import ChatParticipant
from app.api.company.models.company import BusinessType, Company, CompanyRelation, TradeActivity
from app.api.company.models.fleet import CompanyDriver, CompanyVehicle
from app.api.messages.models.message import Message
from app.api.shipments.models import RequestFavorite, Shipment, ShipmentRequest, VehicleFavorite
from app.api.shipments.tasks import purge_expired_requests
from app.db.base import AsyncSessionLocal
from app.main import app


def _company(suffix: str, carrier: bool) -> Company:
	# Уникальный ИНН на роль: клиент и перевозчик в одном тесте не должны делить inn_key.
	role_offset = 1 if carrier else 0
	seed = 7700000000 + (int(suffix[:6], 16) + role_offset) % 80000000
	return Company(
		name=f"{'Carrier' if carrier else 'Client'} {suffix}",
		slug=f"{'carrier' if carrier else 'client'}-{suffix}",
		type="ООО",
		trade_activity=TradeActivity.CARRIER if carrier else TradeActivity.SELLER,
		business_type=BusinessType.SERVICES,
		activity_type="Перевозки",
		description="Test",
		inn=f"{seed:010d}",
		ogrn=f"{seed:013d}",
		kpp=f"{seed % 10**9:09d}",
		country="Россия",
		federal_district="ЦФО",
		region="Москва",
		city="Москва",
		full_name=f"Test {suffix}",
		registration_date=datetime.utcnow(),
		legal_address="Тест, 1",
		production_address="Тест, 2",
		phone="+79000000001",
		email=f"{'carrier' if carrier else 'client'}-{suffix}@example.com",
		website="https://example.com",
		is_active=True,
	)


@pytest.mark.asyncio
async def test_carrier_transport_flow():
	suffix = uuid4().hex[:8]
	async with AsyncSessionLocal() as session:
		client_company, carrier_company = _company(suffix, False), _company(suffix, True)
		session.add_all([client_company, carrier_company])
		await session.flush()
		client_user = User(email=f"client-{suffix}@test.local", phone="+79001111111", first_name="Client", last_name="Test", hashed_password="x", company_id=client_company.id, is_active=True)
		carrier_user = User(email=f"carrier-{suffix}@test.local", phone="+79002222222", first_name="Carrier", last_name="Test", hashed_password="x", company_id=carrier_company.id, is_active=True)
		vehicle = CompanyVehicle(company_id=carrier_company.id, name="MAN", plate_number="A123AA77", body_type="Тентованный", capacity_tons=20, volume_m3=80, loading_methods=["Задняя"], adr_classes=["Класс 3 (ADR-3)"], from_locations=[{"name": "Москва"}], to_locations=[{"name": "Тула"}], partial_load=True, partial_load_weight_kg=1000)
		driver = CompanyDriver(company_id=carrier_company.id, full_name="Иванов И.И.")
		session.add_all([client_user, carrier_user, vehicle, driver])
		await session.commit()
		client_user_id, carrier_user_id = client_user.id, carrier_user.id
		client_company_id, carrier_company_id = client_company.id, carrier_company.id
		vehicle_id, driver_id = vehicle.id, driver.id

	current_user_id = client_user_id

	async def _override_current_user():
		async with AsyncSessionLocal() as session:
			return await session.get(User, current_user_id)

	app.dependency_overrides[get_current_user] = _override_current_user
	try:
		async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as api:
			search = await api.post(
				"/api/v1/transport/search",
				json={
					"body_types": ["Тентованный"],
					"cargo_weight_kg": 500,
					"from_locations": [{"name": "Москва"}],
					"to_locations": [{"name": "Тула"}],
				},
			)
			assert search.status_code == 200, search.text
			matched_ids = [item["id"] for item in search.json()["vehicles"]]
			assert vehicle_id in matched_ids
			async with AsyncSessionLocal() as session:
				request = (await session.execute(
					select(ShipmentRequest).where(
						ShipmentRequest.client_company_id == client_company_id,
						ShipmentRequest.carrier_company_id == carrier_company_id,
					).order_by(ShipmentRequest.id.desc())
				)).scalars().first()
				assert request is not None
				request_id = request.id
			assert (await api.post(f"/api/v1/transport/requests/{request_id}/activate")).status_code == 200
			assert (await api.post(f"/api/v1/transport/favorites/vehicles/{vehicle_id}")).status_code == 201

			current_user_id = carrier_user_id
			requests = await api.get("/api/v1/transport/requests")
			assert requests.status_code == 200 and requests.json()[0]["is_highlighted"]
			assert (await api.post(f"/api/v1/transport/favorites/requests/{request_id}")).status_code == 201
			accepted = await api.post(f"/api/v1/transport/requests/{request_id}/accept")
			assert accepted.status_code == 200, accepted.text
			shipment_id = accepted.json()["id"]
			transport = await api.patch(f"/api/v1/transport/shipments/{shipment_id}/transport", json={"vehicle_id": vehicle_id, "driver_id": driver_id})
			assert transport.status_code == 200 and transport.json()["transport_snapshot"]["driver"]["id"] == driver_id

			current_user_id = client_user_id
			cargo = await api.patch(f"/api/v1/transport/shipments/{shipment_id}/cargo", json={"cargo_name": "Тестовый груз", "gross_weight": 500})
			assert cargo.status_code == 200 and cargo.json()["cargo_data"]["cargo_name"] == "Тестовый груз"

			async with AsyncSessionLocal() as session:
				session.add(ShipmentRequest(client_company_id=client_company_id, carrier_company_id=carrier_company_id, search_filters={}, matched_vehicle_ids=[], expires_at=datetime.utcnow() - timedelta(seconds=1)))
				await session.commit()
			assert await purge_expired_requests() >= 1
	finally:
		app.dependency_overrides.pop(get_current_user, None)
		async with AsyncSessionLocal() as session:
			await session.execute(delete(RequestFavorite).where(RequestFavorite.carrier_company_id == carrier_company_id))
			await session.execute(delete(VehicleFavorite).where(VehicleFavorite.client_company_id == client_company_id))
			await session.execute(delete(Shipment).where(Shipment.client_company_id == client_company_id))
			await session.execute(delete(ShipmentRequest).where(ShipmentRequest.client_company_id == client_company_id))
			await session.execute(delete(Message).where(
				Message.sender_user_id.in_([client_user_id, carrier_user_id])
				| Message.sender_company_id.in_([client_company_id, carrier_company_id])
			))
			await session.execute(delete(ChatParticipant).where(
				ChatParticipant.user_id.in_([client_user_id, carrier_user_id])
				| ChatParticipant.company_id.in_([client_company_id, carrier_company_id])
			))
			await session.execute(delete(CompanyDriver).where(CompanyDriver.company_id == carrier_company_id))
			await session.execute(delete(CompanyVehicle).where(CompanyVehicle.company_id == carrier_company_id))
			await session.execute(delete(CompanyRelation).where(
				CompanyRelation.company_id.in_([client_company_id, carrier_company_id])
				| CompanyRelation.related_company_id.in_([client_company_id, carrier_company_id])
			))
			await session.execute(delete(User).where(User.id.in_([client_user_id, carrier_user_id])))
			await session.execute(delete(Company).where(Company.id.in_([client_company_id, carrier_company_id])))
			await session.commit()
