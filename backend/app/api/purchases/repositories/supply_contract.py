from datetime import datetime
from typing import Optional

from sqlalchemy import and_, desc, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.purchases.models import Order
from app.api.purchases.models import SpecificationItem as SpecificationItemModel
from app.api.purchases.models import SupplyContract as SupplyContractModel
from app.api.purchases.models import SupplyContractSpecification as SupplyContractSpecificationModel
from app.api.purchases.schemas import SpecificationItem as SpecificationItemSchema


class SupplyContractRepository:
	"""Класс для работы с договором поставки и его спецификациями"""

	def __init__(self, session: AsyncSession):
		self.session = session

	def _company_has_access(self, contract: SupplyContractModel, company_id: int) -> bool:
		return company_id in (contract.buyer_company_id, contract.seller_company_id)

	def _spec_access_via_contract(self, spec: SupplyContractSpecificationModel, company_id: int) -> bool:
		return self._company_has_access(spec.supply_contract, company_id)

	def _contract_load_options(self):
		return (
			selectinload(SupplyContractModel.specifications)
			.selectinload(SupplyContractSpecificationModel.spec_items),
		)

	def _spec_load_options(self):
		return (
			selectinload(SupplyContractSpecificationModel.spec_items),
			selectinload(SupplyContractSpecificationModel.supply_contract),
		)

	async def _generate_contract_number(self, seller_company_id: int) -> str:
		"""Генерация номера договора поставки (маска 00001, ежегодное обнуление)"""
		current_year = datetime.utcnow().year
		query = (
			select(func.max(SupplyContractModel.number))
			.where(SupplyContractModel.seller_company_id == seller_company_id)
			.where(SupplyContractModel.number.isnot(None))
			.where(extract("year", SupplyContractModel.date) == current_year)
		)
		result = await self.session.execute(query)
		max_number = result.scalar()

		if max_number:
			try:
				next_number = int("".join(filter(str.isdigit, max_number))) + 1
			except ValueError:
				next_number = 1
		else:
			next_number = 1

		return f"{next_number:05d}"

	async def _generate_spec_number(self, supply_contract_id: int) -> str:
		current_year = datetime.utcnow().year
		query = (
			select(SupplyContractSpecificationModel.spec_number)
			.where(SupplyContractSpecificationModel.supply_contract_id == supply_contract_id)
			.where(SupplyContractSpecificationModel.spec_number.isnot(None))
			.where(extract("year", SupplyContractSpecificationModel.spec_date) == current_year)
		)
		result = await self.session.execute(query)
		rows = result.scalars().all()
		max_number = 0

		for raw_number in rows:
			number = str(raw_number or "").strip()
			if not number:
				continue
			digits = "".join(filter(str.isdigit, number))
			if not digits:
				continue
			try:
				parsed = int(digits)
			except ValueError:
				continue
			if parsed > max_number:
				max_number = parsed

		next_number = max_number + 1

		return str(next_number)

	async def _replace_spec_items(
		self,
		spec: SupplyContractSpecificationModel,
		items: list[SpecificationItemSchema],
	) -> None:
		spec.spec_items.clear()
		await self.session.flush()

		for position, item in enumerate(items, start=1):
			spec.spec_items.append(
				SpecificationItemModel(
					name=item.name,
					article=item.article,
					quantity=item.quantity,
					units=item.units,
					price=item.price,
					amount=item.amount,
					position=position,
				)
			)

	async def create_contract(
		self,
		seller_company_id: int,
		buyer_company_id: int,
		company_id: int,
	) -> SupplyContractModel:
		number = await self._generate_contract_number(seller_company_id)
		contract = SupplyContractModel(
			seller_company_id=seller_company_id,
			buyer_company_id=buyer_company_id,
			number=number,
			date=datetime.utcnow(),
			terms_text="",
		)
		self.session.add(contract)
		await self.session.flush()
		await self.session.commit()
		reloaded = await self.get_contract_by_id(contract.id, company_id)
		assert reloaded is not None
		return reloaded

	async def get_contract_by_id(
		self,
		contract_id: int,
		company_id: int,
	) -> Optional[SupplyContractModel]:
		result = await self.session.execute(
			select(SupplyContractModel)
			.options(*self._contract_load_options())
			.where(SupplyContractModel.id == contract_id)
		)
		contract = result.scalar_one_or_none()
		if contract is None:
			return None
		if not self._company_has_access(contract, company_id):
			return None
		return contract

	async def get_contract_by_id_only(self, contract_id: int) -> Optional[SupplyContractModel]:
		result = await self.session.execute(
			select(SupplyContractModel)
			.options(*self._contract_load_options())
			.where(SupplyContractModel.id == contract_id)
		)
		return result.scalar_one_or_none()

	async def find_by_company_pair(
		self,
		buyer_company_id: int,
		seller_company_id: int,
	) -> Optional[SupplyContractModel]:
		result = await self.session.execute(
			select(SupplyContractModel)
			.options(*self._contract_load_options())
			.where(
				and_(
					SupplyContractModel.buyer_company_id == buyer_company_id,
					SupplyContractModel.seller_company_id == seller_company_id,
				)
			)
		)
		return result.scalar_one_or_none()

	async def update_contract(
		self,
		contract_id: int,
		company_id: int,
		*,
		officials_json: Optional[list[dict]] = None,
		terms_text: Optional[str] = None,
		supplier_details_check: Optional[bool] = None,
		buyer_details_check: Optional[bool] = None,
		cover_letter_check: Optional[bool] = None,
	) -> Optional[SupplyContractModel]:
		contract = await self.get_contract_by_id(contract_id, company_id)
		if contract is None:
			return None

		if officials_json is not None:
			contract.officials_json = officials_json
		if terms_text is not None:
			contract.terms_text = terms_text
		if supplier_details_check is not None:
			contract.supplier_details_check = supplier_details_check
		if buyer_details_check is not None:
			contract.buyer_details_check = buyer_details_check
		if cover_letter_check is not None:
			contract.cover_letter_check = cover_letter_check

		await self.session.commit()
		return await self.get_contract_by_id(contract_id, company_id)

	async def create_specification(
		self,
		contract_id: int,
		company_id: int,
	) -> Optional[SupplyContractSpecificationModel]:
		contract = await self.get_contract_by_id(contract_id, company_id)
		if contract is None:
			return None

		spec_number = await self._generate_spec_number(contract_id)
		spec = SupplyContractSpecificationModel(
			supply_contract_id=contract.id,
			spec_number=spec_number,
			spec_date=datetime.utcnow(),
			spec_text="",
		)
		self.session.add(spec)
		await self.session.flush()
		await self.session.commit()
		return await self.get_specification_by_id(spec.id, company_id)

	async def get_specification_by_id(
		self,
		spec_id: int,
		company_id: int,
	) -> Optional[SupplyContractSpecificationModel]:
		result = await self.session.execute(
			select(SupplyContractSpecificationModel)
			.options(*self._spec_load_options())
			.where(SupplyContractSpecificationModel.id == spec_id)
		)
		spec = result.scalar_one_or_none()
		if spec is None:
			return None
		if not self._spec_access_via_contract(spec, company_id):
			return None
		return spec

	async def get_specification_by_id_only(self, spec_id: int) -> Optional[SupplyContractSpecificationModel]:
		result = await self.session.execute(
			select(SupplyContractSpecificationModel)
			.options(*self._spec_load_options())
			.where(SupplyContractSpecificationModel.id == spec_id)
		)
		return result.scalar_one_or_none()

	async def update_specification(
		self,
		spec_id: int,
		company_id: int,
		*,
		spec_text: Optional[str] = None,
		spec_items: Optional[list[SpecificationItemSchema]] = None,
	) -> Optional[SupplyContractSpecificationModel]:
		spec = await self.get_specification_by_id(spec_id, company_id)
		if spec is None:
			return None

		if spec_text is not None:
			spec.spec_text = spec_text
		if spec_items is not None:
			await self._replace_spec_items(spec, spec_items)

		await self.session.commit()
		return await self.get_specification_by_id(spec_id, company_id)

	async def bind_order_to_contract(
		self,
		order_id: int,
		contract_id: int,
		company_id: int,
	) -> bool:
		contract = await self.get_contract_by_id(contract_id, company_id)
		if contract is None:
			return False

		query = (
			select(Order)
			.where(
				and_(
					Order.id == order_id,
					or_(
						Order.buyer_company_id == company_id,
						Order.seller_company_id == company_id,
					),
				)
			)
			.order_by(desc(Order.version))
			.limit(1)
		)
		result = await self.session.execute(query)
		order = result.scalar_one_or_none()
		if order is None:
			return False

		order.supply_contract_id = contract_id
		order.supply_contracts_number = contract.number
		order.supply_contracts_date = contract.date
		order.updated_at = datetime.utcnow()
		await self.session.commit()
		return True

	async def bind_order_to_specification(
		self,
		order_id: int,
		spec_id: int,
		company_id: int,
	) -> bool:
		spec = await self.get_specification_by_id(spec_id, company_id)
		if spec is None:
			return False

		query = (
			select(Order)
			.where(
				and_(
					Order.id == order_id,
					or_(
						Order.buyer_company_id == company_id,
						Order.seller_company_id == company_id,
					),
				)
			)
			.order_by(desc(Order.version))
			.limit(1)
		)
		result = await self.session.execute(query)
		order = result.scalar_one_or_none()
		if order is None:
			return False

		order.supply_contract_id = spec.supply_contract_id
		order.supply_spec_id = spec.id
		if spec.supply_contract is not None:
			order.supply_contracts_number = spec.supply_contract.number
			order.supply_contracts_date = spec.supply_contract.date
		order.updated_at = datetime.utcnow()
		await self.session.commit()
		return True
