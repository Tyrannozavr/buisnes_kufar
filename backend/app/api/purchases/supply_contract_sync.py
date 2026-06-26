"""Dual-write и read-switch между legacy-полями Order и сущностью SupplyContract."""

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.purchases.models import Order
from app.api.purchases.models import SupplyContract as SupplyContractModel
from app.api.purchases.models import SupplyContractSpecification as SupplyContractSpecificationModel
from app.api.purchases.schemas import (
	CompanyOfficialInDealResponse,
	SupplyContractInDealResponse,
	SupplyContractInUpdate,
)


def officials_to_json(officials) -> list[dict]:
	return [
		{
			"id": o.id,
			"company_id": getattr(o, "company_id", None),
			"full_name": o.full_name,
			"position": o.position,
			"is_base": o.is_base,
			"base_document": o.base_document,
			"base_document_name": o.base_document_name,
		}
		for o in officials
	]


def officials_from_json(stored: Optional[list]) -> list[CompanyOfficialInDealResponse]:
	if not stored or not isinstance(stored, list):
		return []
	return [CompanyOfficialInDealResponse.model_validate(item) for item in stored]


async def _load_entity_by_id(
	session: AsyncSession,
	contract_id: int,
) -> Optional[SupplyContractModel]:
	result = await session.execute(
		select(SupplyContractModel)
		.options(
			selectinload(SupplyContractModel.specifications).selectinload(
				SupplyContractSpecificationModel.spec_items
			)
		)
		.where(SupplyContractModel.id == contract_id)
	)
	return result.scalar_one_or_none()


async def find_entity_by_company_pair(
	session: AsyncSession,
	buyer_company_id: int,
	seller_company_id: int,
) -> Optional[SupplyContractModel]:
	result = await session.execute(
		select(SupplyContractModel)
		.options(
			selectinload(SupplyContractModel.specifications).selectinload(
				SupplyContractSpecificationModel.spec_items
			)
		)
		.where(
			and_(
				SupplyContractModel.buyer_company_id == buyer_company_id,
				SupplyContractModel.seller_company_id == seller_company_id,
			)
		)
	)
	return result.scalar_one_or_none()


async def load_order_supply_contract_entity(
	session: AsyncSession,
	order: Order,
) -> Optional[SupplyContractModel]:
	if order.supply_contract_id:
		entity = await _load_entity_by_id(session, order.supply_contract_id)
		if entity:
			return entity
	return await find_entity_by_company_pair(
		session,
		order.buyer_company_id,
		order.seller_company_id,
	)


def _resolve_linked_specification(
	order: Order,
	entity: SupplyContractModel,
) -> Optional[SupplyContractSpecificationModel]:
	"""Не обращаться к entity.specifications без eager load — иначе MissingGreenlet в async."""
	from sqlalchemy.orm import attributes

	state = attributes.instance_state(entity)
	if state.attrs.specifications.loaded_value is attributes.NO_VALUE:
		return None

	specs = entity.specifications
	if not specs:
		return None
	if order.supply_spec_id:
		for spec in specs:
			if spec.id == order.supply_spec_id:
				return spec
	return specs[-1]


async def build_supply_contract_in_deal_response(
	session: AsyncSession,
	order: Order,
) -> SupplyContractInDealResponse:
	entity = await load_order_supply_contract_entity(session, order)

	if entity:
		spec = _resolve_linked_specification(order, entity)
		number = entity.number or order.supply_contracts_number or ""
		supply_date = entity.date or order.supply_contracts_date
		return SupplyContractInDealResponse(
			entity_id=entity.id,
			specification_entity_id=spec.id if spec else None,
			number=number,
			officials=officials_from_json(entity.officials_json),
			specification_number=spec.spec_number if spec else "",
			specification_date=spec.spec_date if spec else None,
			template_supply_contract=str(order.supply_contract_template_id or ""),
			template_specification=str(order.supply_specification_template_id or ""),
			supply_contract_text=entity.terms_text or "",
			specification_text=(spec.spec_text or "") if spec else "",
			supplier_details_check=entity.supplier_details_check,
			buyer_details_check=entity.buyer_details_check,
			cover_letter_check=entity.cover_letter_check,
		)

	return SupplyContractInDealResponse(
		number=order.supply_contracts_number or "",
		officials=[],
		specification_number="",
		specification_date=None,
		template_supply_contract=str(order.supply_contract_template_id or ""),
		template_specification=str(order.supply_specification_template_id or ""),
	)


async def ensure_supply_contract_entity_for_order(
	session: AsyncSession,
	order: Order,
	*,
	number: Optional[str] = None,
	contract_date: Optional[datetime] = None,
) -> SupplyContractModel:
	entity = await load_order_supply_contract_entity(session, order)
	resolved_number = (number or order.supply_contracts_number or order.seller_order_number or "").strip()
	resolved_date = contract_date or order.supply_contracts_date or datetime.utcnow()

	if entity is None:
		entity = SupplyContractModel(
			seller_company_id=order.seller_company_id,
			buyer_company_id=order.buyer_company_id,
			number=resolved_number or "00001",
			date=resolved_date,
			terms_text="",
		)
		session.add(entity)
		await session.flush()
	else:
		if resolved_number and entity.number != resolved_number:
			entity.number = resolved_number
		if resolved_date:
			entity.date = resolved_date

	order.supply_contract_id = entity.id
	reloaded = await _load_entity_by_id(session, entity.id)
	return reloaded or entity


async def dual_write_supply_contract_from_order_update(
	session: AsyncSession,
	order: Order,
	sc: SupplyContractInUpdate,
	*,
	supply_date: Optional[datetime] = None,
) -> None:
	entity = await ensure_supply_contract_entity_for_order(
		session,
		order,
		number=sc.number if sc.number else None,
		contract_date=supply_date,
	)

	if sc.officials is not None:
		entity.officials_json = officials_to_json(sc.officials)
		for item in entity.officials_json:
			item.setdefault("company_id", order.seller_company_id)
	if sc.terms_text is not None:
		entity.terms_text = sc.terms_text
	if sc.specification_text:
		spec = _resolve_linked_specification(order, entity)
		if spec is not None:
			spec.spec_text = sc.specification_text
	if sc.supplier_details_check is not None:
		entity.supplier_details_check = sc.supplier_details_check
	if sc.buyer_details_check is not None:
		entity.buyer_details_check = sc.buyer_details_check
	if sc.cover_letter_check is not None:
		entity.cover_letter_check = sc.cover_letter_check

	if sc.template_supply_contract is not None:
		order.supply_contract_template_id = _parse_optional_template_id(sc.template_supply_contract)
	if sc.template_specification is not None:
		order.supply_specification_template_id = _parse_optional_template_id(sc.template_specification)


def _parse_optional_template_id(raw: Optional[str]) -> Optional[int]:
	if raw is None:
		return None
	value = str(raw).strip()
	if not value:
		return None
	try:
		parsed = int(value)
	except ValueError:
		return None
	return parsed if parsed > 0 else None


async def dual_write_assign_supply_contract(
	session: AsyncSession,
	order: Order,
	number: str,
	contract_date: datetime,
) -> None:
	await ensure_supply_contract_entity_for_order(
		session,
		order,
		number=number,
		contract_date=contract_date,
	)
