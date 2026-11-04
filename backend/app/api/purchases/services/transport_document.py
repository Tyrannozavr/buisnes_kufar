"""Сервис документов перевозки / экспедиции (§1.2)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.models import (
	TRANSPORT_CHILD_PARENT,
	TRANSPORT_FRAMEWORK_TYPES,
	Order,
	TransportDocument,
	TransportDocumentType,
)
from app.api.purchases.repositories import DealRepository
from app.api.purchases.repositories.transport_document import TransportDocumentRepository
from app.api.purchases.schemas import (
	TransportDocumentBindRequest,
	TransportDocumentCreate,
	TransportDocumentListResponse,
	TransportDocumentNextNumberResponse,
	TransportDocumentResponse,
	TransportDocumentUpdate,
)


def _utc_now_naive() -> datetime:
	return datetime.now(timezone.utc).replace(tzinfo=None)


def _normalize_datetime(value: datetime) -> datetime:
	if value.tzinfo is None:
		return value
	return value.astimezone(timezone.utc).replace(tzinfo=None)


class TransportDocumentError(Exception):
	"""Базовая ошибка домена документов перевозки."""

	def __init__(self, message: str):
		self.message = message
		super().__init__(message)


class TransportDocumentDuplicateError(TransportDocumentError):
	pass


class TransportDocumentAccessError(TransportDocumentError):
	pass


class TransportDocumentValidationError(TransportDocumentError):
	pass


class TransportDocumentService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repository = TransportDocumentRepository(session)
		self.deals = DealRepository(session)

	def _to_response(
		self,
		doc: TransportDocument,
		names: dict[int, str],
	) -> TransportDocumentResponse:
		doc_type = doc.doc_type.value if isinstance(doc.doc_type, TransportDocumentType) else str(doc.doc_type)
		return TransportDocumentResponse(
			id=doc.id,
			owner_company_id=doc.owner_company_id,
			carrier_company_id=doc.carrier_company_id,
			carrier_name=names.get(doc.carrier_company_id, ""),
			doc_type=doc_type,
			number=doc.number,
			date=doc.date,
			parent_id=doc.parent_id,
			deal_id=doc.deal_id,
			payload_json=doc.payload_json if isinstance(doc.payload_json, dict) else None,
		)

	async def _names_for(self, docs: list[TransportDocument]) -> dict[int, str]:
		ids: set[int] = set()
		for doc in docs:
			ids.add(doc.carrier_company_id)
			ids.add(doc.owner_company_id)
		return await self.repository.get_company_names(list(ids))

	@staticmethod
	def _parse_type(raw: str) -> TransportDocumentType:
		try:
			return TransportDocumentType(raw)
		except ValueError as exc:
			raise TransportDocumentValidationError(
				f"Неизвестный тип документа: {raw}"
			) from exc

	async def get_next_number(
		self,
		owner_company_id: int,
		*,
		doc_type: str,
		carrier_company_id: int,
		parent_id: Optional[int] = None,
	) -> TransportDocumentNextNumberResponse:
		parsed = self._parse_type(doc_type)
		if parsed in TRANSPORT_CHILD_PARENT and not parent_id:
			raise TransportDocumentValidationError(
				"Для приложения нужен parent_id (рамочный договор)"
			)
		number = await self.repository.generate_next_number(
			owner_company_id=owner_company_id,
			carrier_company_id=carrier_company_id,
			doc_type=parsed,
			parent_id=parent_id,
		)
		return TransportDocumentNextNumberResponse(
			number=number,
			date=_utc_now_naive(),
			doc_type=parsed.value,
		)

	async def list_for_picker(
		self,
		owner_company_id: int,
		*,
		carrier_company_id: int,
		doc_type: str,
	) -> TransportDocumentListResponse:
		parsed = self._parse_type(doc_type)
		if parsed not in TRANSPORT_FRAMEWORK_TYPES:
			raise TransportDocumentValidationError(
				"Список для пикера доступен только для рамочных договоров "
				"(carriage_contract / expedition_contract)"
			)
		docs = await self.repository.list_for_picker(
			owner_company_id=owner_company_id,
			carrier_company_id=carrier_company_id,
			doc_type=parsed,
		)
		names = await self._names_for(docs)
		return TransportDocumentListResponse(
			documents=[self._to_response(d, names) for d in docs]
		)

	async def list_for_deal(
		self,
		owner_company_id: int,
		deal_id: int,
	) -> TransportDocumentListResponse:
		order = await self.deals.get_order_transport_context(deal_id, owner_company_id)
		if not order:
			raise TransportDocumentAccessError("Сделка не найдена или нет доступа")
		docs = await self.repository.list_by_deal(
			owner_company_id=owner_company_id,
			deal_id=deal_id,
		)
		# Рамочный на сделке может быть только в JSON без deal_id — подтянем по ids
		extra_ids: list[int] = []
		payload = order.transport_contract if isinstance(order.transport_contract, dict) else None
		if payload:
			for item in payload.get("documents") or []:
				if isinstance(item, dict) and item.get("id"):
					extra_ids.append(int(item["id"]))
		missing = [i for i in extra_ids if i not in {d.id for d in docs}]
		if missing:
			extras = await self.repository.get_by_ids(missing)
			docs.extend(
				d for d in extras if d.owner_company_id == owner_company_id
			)
		# Heal: документы с deal_id есть, а orders.transport_contract пуст (create без sync / wipe)
		await self._heal_order_payload_if_empty(order, owner_company_id, docs)
		names = await self._names_for(docs)
		return TransportDocumentListResponse(
			documents=[self._to_response(d, names) for d in docs]
		)

	async def get(self, document_id: int, owner_company_id: int) -> TransportDocumentResponse:
		doc = await self.repository.get_by_id(document_id)
		if not doc or doc.owner_company_id != owner_company_id:
			raise TransportDocumentAccessError("Документ не найден")
		names = await self._names_for([doc])
		return self._to_response(doc, names)

	async def update(
		self,
		document_id: int,
		owner_company_id: int,
		body: TransportDocumentUpdate,
	) -> TransportDocumentResponse:
		doc = await self.repository.get_by_id(document_id)
		if not doc or doc.owner_company_id != owner_company_id:
			raise TransportDocumentAccessError("Документ не найден")
		if body.number is not None:
			number = body.number.strip()
			if not number:
				raise TransportDocumentValidationError("Номер не может быть пустым")
			doc.number = number
		if body.date is not None:
			doc.date = _normalize_datetime(body.date)
		if body.payload_json is not None:
			from app.core.html_sanitize import assert_payload_size, sanitize_payload_json

			try:
				assert_payload_size(body.payload_json)
			except ValueError as exc:
				raise TransportDocumentValidationError(str(exc)) from exc
			doc.payload_json = sanitize_payload_json(body.payload_json)
		try:
			await self.session.commit()
		except IntegrityError as exc:
			await self.session.rollback()
			raise TransportDocumentDuplicateError(
				"Документ с таким номером уже существует"
			) from exc
		await self.session.refresh(doc)
		names = await self._names_for([doc])
		return self._to_response(doc, names)

	async def _validate_parent(
		self,
		*,
		owner_company_id: int,
		carrier_company_id: int,
		doc_type: TransportDocumentType,
		parent_id: Optional[int],
	) -> Optional[TransportDocument]:
		required_parent = TRANSPORT_CHILD_PARENT.get(doc_type)
		if required_parent is None:
			if parent_id is not None:
				raise TransportDocumentValidationError(
					"У этого типа документа не должно быть parent_id"
				)
			return None
		if parent_id is None:
			raise TransportDocumentValidationError(
				f"Для {doc_type.value} нужен parent_id ({required_parent.value})"
			)
		parent = await self.repository.get_by_id(parent_id)
		if not parent or parent.owner_company_id != owner_company_id:
			raise TransportDocumentValidationError("Родительский договор не найден")
		parent_type = (
			parent.doc_type
			if isinstance(parent.doc_type, TransportDocumentType)
			else TransportDocumentType(str(parent.doc_type))
		)
		if parent_type != required_parent:
			raise TransportDocumentValidationError(
				f"Родитель должен быть типа {required_parent.value}"
			)
		if parent.carrier_company_id != carrier_company_id:
			raise TransportDocumentValidationError(
				"Перевозчик дочернего документа должен совпадать с родителем"
			)
		return parent

	async def create(
		self,
		owner_company_id: int,
		body: TransportDocumentCreate,
	) -> TransportDocumentResponse:
		doc_type = self._parse_type(body.doc_type)
		if not await self.repository.is_carrier_relation(
			owner_company_id, body.carrier_company_id
		):
			raise TransportDocumentValidationError(
				"Добавьте организацию в раздел Перевозчики для создания договора"
			)
		await self._validate_parent(
			owner_company_id=owner_company_id,
			carrier_company_id=body.carrier_company_id,
			doc_type=doc_type,
			parent_id=body.parent_id,
		)
		deal_id = body.deal_id
		if deal_id is not None:
			order = await self.deals.get_order_transport_context(deal_id, owner_company_id)
			if not order:
				raise TransportDocumentAccessError("Сделка не найдена или нет доступа")
			if order.seller_company_id != owner_company_id:
				raise TransportDocumentAccessError(
					"Только продавец может привязывать документы перевозки к сделке"
				)
		doc_date = _normalize_datetime(body.date) if body.date else _utc_now_naive()
		explicit_number = (body.number or "").strip()
		# Автономер: при гонке/устаревшем max — несколько попыток со свежим next.
		# Явный number от клиента — без ретрая, сразу 409.
		max_attempts = 1 if explicit_number else 8
		doc: TransportDocument | None = None
		last_exc: BaseException | None = None
		for attempt in range(max_attempts):
			number = explicit_number or await self.repository.generate_next_number(
				owner_company_id=owner_company_id,
				carrier_company_id=body.carrier_company_id,
				doc_type=doc_type,
				parent_id=body.parent_id,
				year=doc_date.year,
			)
			try:
				doc = await self.repository.create(
					owner_company_id=owner_company_id,
					carrier_company_id=body.carrier_company_id,
					doc_type=doc_type,
					number=number,
					date=doc_date,
					parent_id=body.parent_id,
					deal_id=deal_id,
					payload_json=None,
				)
				await self.session.commit()
				break
			except IntegrityError as exc:
				await self.session.rollback()
				last_exc = exc
				if explicit_number:
					raise TransportDocumentDuplicateError(
						"Документ с таким номером уже существует"
					) from exc
				# иначе — ещё одна попытка с новым generate_next_number
		if doc is None:
			raise TransportDocumentDuplicateError(
				"Не удалось подобрать свободный номер документа"
			) from last_exc
		await self.session.refresh(doc)
		names = await self._names_for([doc])
		# Dual-write сразу при create с deal_id (не только на bind) —
		# иначе ячейка Продаж пустая, если bind пропущен/упал.
		if deal_id is not None:
			order = await self.deals.get_order_transport_context(deal_id, owner_company_id)
			if order:
				await self._sync_order_payload(order, owner_company_id, doc, names)
				await self.session.commit()
				await self.session.refresh(doc)
		return self._to_response(doc, names)

	def _document_snapshot(
		self,
		doc: TransportDocument,
		names: dict[int, str],
	) -> dict:
		doc_type = doc.doc_type.value if isinstance(doc.doc_type, TransportDocumentType) else str(doc.doc_type)
		return {
			"id": doc.id,
			"type": doc_type,
			"number": doc.number,
			"date": doc.date.isoformat() if isinstance(doc.date, datetime) else str(doc.date),
			"carrier_company_id": doc.carrier_company_id,
			"carrier_name": names.get(doc.carrier_company_id, ""),
			"parent_id": doc.parent_id,
		}

	def _primary_from_documents(self, documents: list[dict]) -> dict:
		primary = documents[0] if documents else {}
		for item in documents:
			if isinstance(item, dict) and item.get("type") in {
				TransportDocumentType.CARRIAGE_CONTRACT.value,
				TransportDocumentType.EXPEDITION_CONTRACT.value,
				TransportDocumentType.CARRIAGE_ORDER.value,
				"transport_expedition",
			}:
				return item
		return primary if isinstance(primary, dict) else {}

	async def _heal_order_payload_if_empty(
		self,
		order: Order,
		owner_company_id: int,
		docs: list[TransportDocument],
	) -> None:
		"""Восстановить orders.transport_contract, если JSON пуст, а документы с deal_id есть."""
		payload = order.transport_contract if isinstance(order.transport_contract, dict) else None
		existing = list((payload or {}).get("documents") or []) if payload else []
		if existing or not docs:
			return
		names = await self._names_for(docs)
		documents = [self._document_snapshot(d, names) for d in docs]
		primary = self._primary_from_documents(documents)
		order.transport_contract = {
			"documents": documents,
			"number": primary.get("number"),
			"date": primary.get("date"),
			"type": primary.get("type"),
			"carrier_company_id": primary.get("carrier_company_id"),
			"carrier_name": primary.get("carrier_name"),
		}
		order.updated_at = _utc_now_naive()
		self.deals._add_order_history(
			order.row_id,
			owner_company_id,
			"transport_document_healed",
			f"Восстановлен снимок перевозки ({len(documents)} док.)",
			None,
			order.transport_contract,
		)
		await self.session.commit()

	async def _sync_order_payload(
		self,
		order: Order,
		owner_company_id: int,
		doc: TransportDocument,
		names: dict[int, str],
	) -> None:
		"""Dual-write в orders.transport_contract для ячейки Продаж (§1.4 позже)."""
		payload = order.transport_contract if isinstance(order.transport_contract, dict) else {}
		documents = list(payload.get("documents") or [])
		snap = self._document_snapshot(doc, names)
		replaced = False
		for idx, item in enumerate(documents):
			if isinstance(item, dict) and item.get("id") == doc.id:
				documents[idx] = snap
				replaced = True
				break
		if not replaced:
			documents.append(snap)
		primary = self._primary_from_documents(documents) or snap
		order.transport_contract = {
			"documents": documents,
			"number": primary.get("number"),
			"date": primary.get("date"),
			"type": primary.get("type"),
			"carrier_company_id": primary.get("carrier_company_id"),
			"carrier_name": primary.get("carrier_name"),
		}
		order.updated_at = _utc_now_naive()
		self.deals._add_order_history(
			order.row_id,
			owner_company_id,
			"transport_document_bound",
			f"Привязан документ перевозки {snap.get('type')} № {snap.get('number')}",
			None,
			order.transport_contract,
		)

	async def bind_to_deal(
		self,
		owner_company_id: int,
		deal_id: int,
		body: TransportDocumentBindRequest,
	) -> TransportDocumentResponse:
		order = await self.deals.get_order_transport_context(deal_id, owner_company_id)
		if not order:
			raise TransportDocumentAccessError("Сделка не найдена или нет доступа")
		if order.seller_company_id != owner_company_id:
			raise TransportDocumentAccessError("Только продавец может привязывать документы перевозки")
		doc = await self.repository.get_by_id(body.document_id)
		if not doc or doc.owner_company_id != owner_company_id:
			raise TransportDocumentAccessError("Документ не найден")

		doc_type = (
			doc.doc_type
			if isinstance(doc.doc_type, TransportDocumentType)
			else TransportDocumentType(str(doc.doc_type))
		)
		# Дочерние и договор-заявка фиксируем на сделке; рамочные переиспользуются
		if doc_type not in TRANSPORT_FRAMEWORK_TYPES:
			doc.deal_id = deal_id
		names = await self._names_for([doc])
		await self._sync_order_payload(order, owner_company_id, doc, names)
		await self.session.commit()
		await self.session.refresh(doc)
		return self._to_response(doc, names)
