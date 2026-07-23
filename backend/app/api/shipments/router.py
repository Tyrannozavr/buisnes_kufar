from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, func, or_, select

from app.api.authentication.dependencies import current_user_dep
from app.api.chats.schemas.chat import ChatCreate
from app.api.chats.services.chat_service import ChatService
from app.api.company.models.company import Company, CompanyRelationType, TradeActivity
from app.api.company.models.fleet import CompanyDriver, CompanyVehicle
from app.api.company.repositories.company_relations_repository import CompanyRelationsRepository
from app.api.purchases.models import Order, OrderStatus
from app.api.shipments.models import RequestFavorite, Shipment, ShipmentRequest, VehicleFavorite
from app.api.shipments.schemas import (
	CargoUpdate, DealUpdate, ShipmentRequestResponse, ShipmentResponse,
	TransportSearchFilters, TransportUpdate,
)
from app.db.dependencies import async_db_dep

router = APIRouter(tags=["transport"])

_SEARCH_LIMIT = 200
_LIST_DEFAULT = 50
_LIST_MAX = 100


def _company_id(user) -> int:
	if not user or not user.company_id:
		raise HTTPException(status_code=404, detail="Company not found for current user")
	return user.company_id


def _locations_match(vehicle_locations: list, requested_locations: list) -> bool:
	if not requested_locations:
		return True
	if not vehicle_locations:
		return False
	requested_names = [str(item.get("name", "")).lower() for item in requested_locations]
	for vehicle_location in vehicle_locations:
		vehicle_name = str(vehicle_location.get("name", "")).lower()
		if any(name and (name in vehicle_name or vehicle_name in name) for name in requested_names):
			return True
	return False


def _matches(vehicle: CompanyVehicle, filters: TransportSearchFilters) -> bool:
	if not vehicle.is_active:
		return False
	if filters.body_types and vehicle.body_type not in filters.body_types:
		return False
	if filters.loading_methods and not set(filters.loading_methods).intersection(vehicle.loading_methods or []):
		return False
	if filters.adr_classes and not set(filters.adr_classes).issubset(set(vehicle.adr_classes or [])):
		return False
	weight = filters.cargo_weight_kg or filters.capacity_min_kg
	volume = filters.cargo_volume_m3 or filters.volume_min_m3
	if filters.partial_load:
		if not vehicle.partial_load:
			return False
		if weight and (vehicle.partial_load_weight_kg or 0) < weight:
			return False
		if volume and (vehicle.partial_load_volume_m3 or 0) < volume:
			return False
	else:
		if weight and (vehicle.capacity_tons or 0) * 1000 < weight:
			return False
		if volume and (vehicle.volume_m3 or 0) < volume:
			return False
	if filters.capacity_max_kg and (vehicle.capacity_tons or 0) * 1000 > filters.capacity_max_kg:
		return False
	if filters.volume_max_m3 and (vehicle.volume_m3 or 0) > filters.volume_max_m3:
		return False
	if filters.load_date and vehicle.load_date and vehicle.load_date != filters.load_date:
		return False
	return (
		_locations_match(vehicle.from_locations or [], filters.from_locations)
		and _locations_match(vehicle.to_locations or [], filters.to_locations)
	)


def _vehicle_response(vehicle: CompanyVehicle, company: Company) -> dict:
	return {
		"id": vehicle.id,
		"company_id": company.id,
		"name": vehicle.name,
		"plate_number": vehicle.plate_number,
		"trailer_plate_number": vehicle.trailer_plate_number,
		"body_type": vehicle.body_type,
		"capacity_tons": vehicle.capacity_tons,
		"volume_m3": vehicle.volume_m3,
		"loading_methods": vehicle.loading_methods or [],
		"adr_classes": vehicle.adr_classes or [],
		"from_locations": vehicle.from_locations or [],
		"to_locations": vehicle.to_locations or [],
		"partial_load": vehicle.partial_load,
		"company": {
			"id": company.id, "name": company.name, "type": company.type, "inn": company.inn,
			"legal_address": company.legal_address, "phone": company.phone, "email": company.email,
		},
	}


def _page_clamp(page: int, per_page: int) -> tuple[int, int]:
	return max(1, page), min(max(1, per_page), _LIST_MAX)


@router.post("/search")
async def search_transport(
	filters: TransportSearchFilters,
	db: async_db_dep,
	current_user: current_user_dep,
):
	"""Поиск ТС без записи заявок — заявка создаётся только в send-request."""
	client_company_id = _company_id(current_user)
	stmt = (
		select(CompanyVehicle, Company)
		.join(Company, Company.id == CompanyVehicle.company_id)
		.where(
			Company.trade_activity.in_([TradeActivity.CARRIER, TradeActivity.FORWARDER]),
			Company.id != client_company_id,
			CompanyVehicle.is_active.is_(True),
		)
	)
	if filters.body_types:
		stmt = stmt.where(CompanyVehicle.body_type.in_(filters.body_types))
	if filters.partial_load:
		stmt = stmt.where(CompanyVehicle.partial_load.is_(True))
		weight = filters.cargo_weight_kg or filters.capacity_min_kg
		volume = filters.cargo_volume_m3 or filters.volume_min_m3
		if weight is not None:
			stmt = stmt.where(CompanyVehicle.partial_load_weight_kg >= weight)
		if volume is not None:
			stmt = stmt.where(CompanyVehicle.partial_load_volume_m3 >= volume)
	else:
		weight = filters.cargo_weight_kg or filters.capacity_min_kg
		volume = filters.cargo_volume_m3 or filters.volume_min_m3
		if weight is not None:
			stmt = stmt.where((CompanyVehicle.capacity_tons * 1000) >= weight)
		if volume is not None:
			stmt = stmt.where(CompanyVehicle.volume_m3 >= volume)
	if filters.capacity_max_kg is not None:
		stmt = stmt.where((CompanyVehicle.capacity_tons * 1000) <= filters.capacity_max_kg)
	if filters.volume_max_m3 is not None:
		stmt = stmt.where(CompanyVehicle.volume_m3 <= filters.volume_max_m3)
	if filters.load_date is not None:
		stmt = stmt.where(
			or_(CompanyVehicle.load_date.is_(None), CompanyVehicle.load_date == filters.load_date)
		)

	# Cap candidate set before Python JSON/location matching
	stmt = stmt.limit(_SEARCH_LIMIT * 3)
	rows = (await db.execute(stmt)).all()
	matched = [(vehicle, company) for vehicle, company in rows if _matches(vehicle, filters)]
	matched = matched[:_SEARCH_LIMIT]
	return {"vehicles": [_vehicle_response(vehicle, company) for vehicle, company in matched]}


@router.post("/requests/{request_id}/activate", response_model=ShipmentRequestResponse)
async def activate_request(request_id: int, db: async_db_dep, current_user: current_user_dep):
	request = await db.get(ShipmentRequest, request_id)
	if not request or request.client_company_id != _company_id(current_user):
		raise HTTPException(status_code=404, detail="Shipment request not found")
	if request.status in {"accepted", "expired"}:
		raise HTTPException(status_code=409, detail="Shipment request cannot be activated")
	request.status, request.is_highlighted, request.activated_at, request.updated_at = "active", True, datetime.utcnow(), datetime.utcnow()
	await db.commit()
	await db.refresh(request)
	return request


@router.post("/vehicles/{vehicle_id}/send-request", response_model=ShipmentRequestResponse)
async def send_vehicle_request(vehicle_id: int, db: async_db_dep, current_user: current_user_dep):
	"""Создать/поднять заявку перевозчику по конкретному ТС (явное действие клиента)."""
	company_id = _company_id(current_user)
	vehicle = await db.get(CompanyVehicle, vehicle_id)
	if not vehicle or not vehicle.is_active:
		raise HTTPException(status_code=404, detail="Vehicle not found")
	carrier_company_id = vehicle.company_id
	if carrier_company_id == company_id:
		raise HTTPException(status_code=400, detail="Cannot send request to own vehicle")

	existing = (await db.execute(
		select(ShipmentRequest).where(
			ShipmentRequest.client_company_id == company_id,
			ShipmentRequest.carrier_company_id == carrier_company_id,
			ShipmentRequest.status.in_(["passive", "active"]),
		).order_by(ShipmentRequest.updated_at.desc())
	)).scalars().first()

	now = datetime.utcnow()
	if existing:
		ids = list(existing.matched_vehicle_ids or [])
		if vehicle_id not in ids:
			ids.append(vehicle_id)
		existing.matched_vehicle_ids = ids
		existing.updated_at = now
		await db.commit()
		return await activate_request(existing.id, db, current_user)

	request = ShipmentRequest(
		client_company_id=company_id,
		carrier_company_id=carrier_company_id,
		search_filters={},
		matched_vehicle_ids=[vehicle_id],
		status="active",
		is_highlighted=True,
		activated_at=now,
		expires_at=now + timedelta(days=14),
	)
	db.add(request)
	await db.commit()
	await db.refresh(request)
	return request


@router.get("/requests", response_model=list[ShipmentRequestResponse])
async def list_requests(
	db: async_db_dep,
	current_user: current_user_dep,
	page: int = Query(1, ge=1),
	per_page: int = Query(_LIST_DEFAULT, ge=1, le=_LIST_MAX),
):
	company_id = _company_id(current_user)
	page, per_page = _page_clamp(page, per_page)
	result = await db.execute(
		select(ShipmentRequest).where(ShipmentRequest.carrier_company_id == company_id)
		.order_by(ShipmentRequest.is_highlighted.desc(), ShipmentRequest.updated_at.desc())
		.offset((page - 1) * per_page)
		.limit(per_page)
	)
	return result.scalars().all()


@router.post("/requests/{request_id}/accept", response_model=ShipmentResponse)
async def accept_request(request_id: int, db: async_db_dep, current_user: current_user_dep):
	carrier_company_id = _company_id(current_user)
	request = await db.get(ShipmentRequest, request_id)
	if not request or request.carrier_company_id != carrier_company_id:
		raise HTTPException(status_code=404, detail="Shipment request not found")
	if request.status == "accepted":
		shipment = (await db.execute(select(Shipment).where(Shipment.request_id == request.id))).scalar_one()
		return shipment
	if request.status == "expired":
		raise HTTPException(status_code=409, detail="Shipment request expired")
	year = datetime.utcnow().year
	last_number = (await db.execute(select(func.max(Shipment.number)).where(Shipment.year == year))).scalar()
	next_number = int(last_number or "0") + 1
	shipment = Shipment(
		number=str(next_number).zfill(5), year=year, client_company_id=request.client_company_id,
		carrier_company_id=carrier_company_id, request_id=request.id,
		vehicle_id=(request.matched_vehicle_ids or [None])[0],
	)
	request.status, request.updated_at = "accepted", datetime.utcnow()
	db.add(shipment)
	await db.commit()
	await db.refresh(shipment)
	relations = CompanyRelationsRepository(db)
	await relations.ensure_relation(request.client_company_id, carrier_company_id, CompanyRelationType.PARTNER)
	await relations.ensure_relation(request.client_company_id, carrier_company_id, CompanyRelationType.CARRIER)
	await relations.ensure_relation(carrier_company_id, request.client_company_id, CompanyRelationType.PARTNER)
	carrier = await db.get(Company, carrier_company_id)
	try:
		chat = await ChatService(db).create_chat(
			current_user.id, carrier_company_id, ChatCreate(participant_company_id=request.client_company_id)
		)
		await ChatService(db).send_message(
			chat.id, carrier_company_id, current_user.id,
			f"Перевозчик «{carrier.name}» принял заявку на перевозку груза №{shipment.number}.",
		)
	except Exception:
		pass
	return shipment


@router.get("/shipments", response_model=list[ShipmentResponse])
async def list_shipments(
	db: async_db_dep,
	current_user: current_user_dep,
	page: int = Query(1, ge=1),
	per_page: int = Query(_LIST_DEFAULT, ge=1, le=_LIST_MAX),
):
	company_id = _company_id(current_user)
	page, per_page = _page_clamp(page, per_page)
	result = await db.execute(
		select(Shipment).where(
			(Shipment.client_company_id == company_id) | (Shipment.carrier_company_id == company_id)
		).order_by(Shipment.created_at.desc())
		.offset((page - 1) * per_page)
		.limit(per_page)
	)
	return result.scalars().all()


async def _shipment_for_company(shipment_id: int, company_id: int, db) -> Shipment:
	shipment = await db.get(Shipment, shipment_id)
	if not shipment or company_id not in {shipment.client_company_id, shipment.carrier_company_id}:
		raise HTTPException(status_code=404, detail="Shipment not found")
	return shipment


@router.patch("/shipments/{shipment_id}/cargo", response_model=ShipmentResponse)
async def update_cargo(shipment_id: int, data: CargoUpdate, db: async_db_dep, current_user: current_user_dep):
	company_id = _company_id(current_user)
	shipment = await _shipment_for_company(shipment_id, company_id, db)
	if shipment.client_company_id != company_id:
		raise HTTPException(status_code=403, detail="Only client can edit cargo")
	shipment.cargo_data = {**(shipment.cargo_data or {}), **data.model_dump(exclude_unset=True, mode="json")}
	shipment.updated_at = datetime.utcnow()
	await db.commit()
	await db.refresh(shipment)
	return shipment


@router.patch("/shipments/{shipment_id}/transport", response_model=ShipmentResponse)
async def update_transport(shipment_id: int, data: TransportUpdate, db: async_db_dep, current_user: current_user_dep):
	company_id = _company_id(current_user)
	shipment = await _shipment_for_company(shipment_id, company_id, db)
	if shipment.carrier_company_id != company_id:
		raise HTTPException(status_code=403, detail="Only carrier can edit transport")
	vehicle = await db.get(CompanyVehicle, data.vehicle_id) if data.vehicle_id else None
	driver = await db.get(CompanyDriver, data.driver_id) if data.driver_id else None
	if vehicle and vehicle.company_id != company_id:
		raise HTTPException(status_code=403, detail="Vehicle does not belong to carrier")
	if driver and driver.company_id != company_id:
		raise HTTPException(status_code=403, detail="Driver does not belong to carrier")
	shipment.vehicle_id, shipment.driver_id = data.vehicle_id, data.driver_id
	shipment.transport_snapshot = {
		"vehicle": {"id": vehicle.id, "name": vehicle.name, "plate_number": vehicle.plate_number,
					"trailer_plate_number": vehicle.trailer_plate_number} if vehicle else None,
		"driver": {"id": driver.id, "full_name": driver.full_name, "phone": driver.phone,
				   "license_number": driver.license_number} if driver else None,
	}
	shipment.updated_at = datetime.utcnow()
	await db.commit()
	await db.refresh(shipment)
	return shipment


@router.patch("/shipments/{shipment_id}/deal", response_model=ShipmentResponse)
async def update_deal(shipment_id: int, data: DealUpdate, db: async_db_dep, current_user: current_user_dep):
	company_id = _company_id(current_user)
	shipment = await _shipment_for_company(shipment_id, company_id, db)
	if shipment.client_company_id != company_id:
		raise HTTPException(status_code=403, detail="Only client can link a deal")
	deal = (await db.execute(
		select(Order).where(
			Order.id == data.deal_id,
			Order.seller_company_id == company_id,
			Order.status == OrderStatus.ACTIVE,
		).order_by(Order.version.desc())
	)).scalars().first()
	if not deal:
		raise HTTPException(status_code=404, detail="Active sales deal not found")
	existing = (await db.execute(select(Shipment).where(Shipment.deal_id == data.deal_id, Shipment.id != shipment.id))).scalar_one_or_none()
	if existing:
		raise HTTPException(status_code=409, detail="Deal is already linked to another shipment")
	shipment.deal_id, shipment.updated_at = data.deal_id, datetime.utcnow()
	await db.commit()
	await db.refresh(shipment)
	return shipment


@router.get("/favorites/vehicles")
async def list_vehicle_favorites(
	db: async_db_dep,
	current_user: current_user_dep,
	page: int = Query(1, ge=1),
	per_page: int = Query(_LIST_DEFAULT, ge=1, le=_LIST_MAX),
):
	company_id = _company_id(current_user)
	page, per_page = _page_clamp(page, per_page)
	rows = (await db.execute(
		select(CompanyVehicle, Company, VehicleFavorite)
		.join(VehicleFavorite, VehicleFavorite.vehicle_id == CompanyVehicle.id)
		.join(Company, Company.id == CompanyVehicle.company_id)
		.where(VehicleFavorite.client_company_id == company_id)
		.order_by(VehicleFavorite.created_at.desc())
		.offset((page - 1) * per_page)
		.limit(per_page)
	)).all()
	return [
		{**_vehicle_response(vehicle, company), "favorite_id": favorite.id}
		for vehicle, company, favorite in rows
	]


@router.post("/favorites/vehicles/{vehicle_id}", status_code=status.HTTP_201_CREATED)
async def add_vehicle_favorite(vehicle_id: int, db: async_db_dep, current_user: current_user_dep):
	company_id = _company_id(current_user)
	if not await db.get(CompanyVehicle, vehicle_id):
		raise HTTPException(status_code=404, detail="Vehicle not found")
	existing = (await db.execute(select(VehicleFavorite).where(VehicleFavorite.client_company_id == company_id, VehicleFavorite.vehicle_id == vehicle_id))).scalar_one_or_none()
	if not existing:
		db.add(VehicleFavorite(client_company_id=company_id, vehicle_id=vehicle_id))
		await db.commit()
	return {"vehicle_id": vehicle_id}


@router.delete("/favorites/vehicles/{vehicle_id}")
async def remove_vehicle_favorite(vehicle_id: int, db: async_db_dep, current_user: current_user_dep):
	await db.execute(delete(VehicleFavorite).where(VehicleFavorite.client_company_id == _company_id(current_user), VehicleFavorite.vehicle_id == vehicle_id))
	await db.commit()
	return {"vehicle_id": vehicle_id}


@router.get("/favorites/requests", response_model=list[ShipmentRequestResponse])
async def list_request_favorites(
	db: async_db_dep,
	current_user: current_user_dep,
	page: int = Query(1, ge=1),
	per_page: int = Query(_LIST_DEFAULT, ge=1, le=_LIST_MAX),
):
	company_id = _company_id(current_user)
	page, per_page = _page_clamp(page, per_page)
	return (await db.execute(
		select(ShipmentRequest)
		.join(RequestFavorite, RequestFavorite.request_id == ShipmentRequest.id)
		.where(RequestFavorite.carrier_company_id == company_id)
		.order_by(RequestFavorite.created_at.desc())
		.offset((page - 1) * per_page)
		.limit(per_page)
	)).scalars().all()


@router.post("/favorites/requests/{request_id}", status_code=status.HTTP_201_CREATED)
async def add_request_favorite(request_id: int, db: async_db_dep, current_user: current_user_dep):
	company_id = _company_id(current_user)
	request = await db.get(ShipmentRequest, request_id)
	if not request or request.carrier_company_id != company_id:
		raise HTTPException(status_code=404, detail="Shipment request not found")
	existing = (await db.execute(select(RequestFavorite).where(RequestFavorite.carrier_company_id == company_id, RequestFavorite.request_id == request_id))).scalar_one_or_none()
	if not existing:
		db.add(RequestFavorite(carrier_company_id=company_id, request_id=request_id))
		await db.commit()
	return {"request_id": request_id}


@router.delete("/favorites/requests/{request_id}")
async def remove_request_favorite(request_id: int, db: async_db_dep, current_user: current_user_dep):
	await db.execute(delete(RequestFavorite).where(RequestFavorite.carrier_company_id == _company_id(current_user), RequestFavorite.request_id == request_id))
	await db.commit()
	return {"request_id": request_id}
