from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.models import SupplyContract
from app.api.purchases.models import SupplyContractSpecification
from app.api.purchases.repositories.supply_contract import SupplyContractRepository
from app.api.purchases.schemas import (
	CompanyOfficialInDealResponse,
	SpecificationItem,
	SpecificationResponse,
	SpecificationUpdate,
	SupplyContractCreate,
	SupplyContractExistsResponse,
	SupplyContractResponse,
	SupplyContractUpdate,
)


class SupplyContractAlreadyExistsError(Exception):
	"""Договор на пару компаний уже существует."""


class SupplyContractService:
	"""Сервис для работы с договорами поставки и спецификациями."""

	def __init__(self, session: AsyncSession):
		self.session = session
		self.repository = SupplyContractRepository(session)

	async def create_contract(
		self,
		company_id: int,
		data: SupplyContractCreate,
	) -> Optional[SupplyContractResponse]:
		if company_id not in (data.buyer_company_id, data.seller_company_id):
			return None

		existing = await self.repository.find_by_company_pair(
			data.buyer_company_id,
			data.seller_company_id,
		)
		if existing is not None:
			raise SupplyContractAlreadyExistsError()

		contract = await self.repository.create_contract(
			data.seller_company_id,
			data.buyer_company_id,
			company_id,
		)
		return self._to_contract_response(contract)

	async def get_contract(
		self,
		contract_id: int,
		company_id: int,
	) -> Optional[SupplyContractResponse]:
		contract = await self.repository.get_contract_by_id(contract_id, company_id)
		if contract is None:
			return None
		return self._to_contract_response(contract)

	async def get_contract_by_id_only(self, contract_id: int) -> Optional[SupplyContract]:
		return await self.repository.get_contract_by_id_only(contract_id)

	async def update_contract(
		self,
		contract_id: int,
		company_id: int,
		data: SupplyContractUpdate,
	) -> Optional[SupplyContractResponse]:
		officials_json = None
		if data.officials_json is not None:
			officials_json = [official.model_dump() for official in data.officials_json]

		contract = await self.repository.update_contract(
			contract_id,
			company_id,
			officials_json=officials_json,
			terms_text=data.terms_text,
			supplier_details_check=data.supplier_details_check,
			buyer_details_check=data.buyer_details_check,
			cover_letter_check=data.cover_letter_check,
		)
		if contract is None:
			return None
		return self._to_contract_response(contract)

	async def exists_by_pair(
		self,
		buyer_company_id: int,
		seller_company_id: int,
	) -> SupplyContractExistsResponse:
		contract = await self.repository.find_by_company_pair(buyer_company_id, seller_company_id)
		if contract is None:
			return SupplyContractExistsResponse(is_exist=False, supply_contract=None)
		return SupplyContractExistsResponse(
			is_exist=True,
			supply_contract=self._to_contract_response(contract),
		)

	async def create_specification(
		self,
		contract_id: int,
		company_id: int,
	) -> Optional[SpecificationResponse]:
		spec = await self.repository.create_specification(contract_id, company_id)
		if spec is None:
			return None
		return self._to_spec_response(spec)

	async def get_specification_by_id_only(self, spec_id: int) -> Optional[SupplyContractSpecification]:
		return await self.repository.get_specification_by_id_only(spec_id)

	async def get_specification(
		self,
		spec_id: int,
		company_id: int,
	) -> Optional[SpecificationResponse]:
		spec = await self.repository.get_specification_by_id(spec_id, company_id)
		if spec is None:
			return None
		return self._to_spec_response(spec)

	async def update_specification(
		self,
		spec_id: int,
		company_id: int,
		data: SpecificationUpdate,
	) -> Optional[SpecificationResponse]:
		spec = await self.repository.update_specification(
			spec_id,
			company_id,
			spec_text=data.spec_text,
			spec_items=data.spec_items,
		)
		if spec is None:
			return None
		return self._to_spec_response(spec)

	async def bind_order_to_contract(
		self,
		order_id: int,
		contract_id: int,
		company_id: int,
	) -> bool:
		return await self.repository.bind_order_to_contract(order_id, contract_id, company_id)

	async def bind_order_to_specification(
		self,
		order_id: int,
		spec_id: int,
		company_id: int,
	) -> bool:
		return await self.repository.bind_order_to_specification(order_id, spec_id, company_id)

	def _officials_from_json(self, officials_json: Optional[list]) -> Optional[list[CompanyOfficialInDealResponse]]:
		if not officials_json:
			return None
		return [CompanyOfficialInDealResponse.model_validate(item) for item in officials_json]

	def _to_contract_response(self, contract: SupplyContract) -> SupplyContractResponse:
		specifications = [
			self._to_spec_response(spec, supply_contract_number=contract.number)
			for spec in contract.specifications
		]
		return SupplyContractResponse(
			id=contract.id,
			buyer_company_id=contract.buyer_company_id,
			seller_company_id=contract.seller_company_id,
			number=contract.number,
			date=contract.date,
			officials_json=self._officials_from_json(contract.officials_json),
			terms_text=contract.terms_text or "",
			specifications=specifications,
			supplier_details_check=contract.supplier_details_check,
			buyer_details_check=contract.buyer_details_check,
			cover_letter_check=contract.cover_letter_check,
		)

	def _to_spec_response(
		self,
		spec: SupplyContractSpecification,
		supply_contract_number: Optional[str] = None,
	) -> SpecificationResponse:
		spec_items = [
			SpecificationItem(
				name=item.name,
				article=item.article,
				quantity=item.quantity,
				units=item.units,
				price=item.price,
				amount=item.amount,
			)
			for item in sorted(spec.spec_items, key=lambda row: row.position)
		]
		if supply_contract_number is None and spec.supply_contract is not None:
			supply_contract_number = spec.supply_contract.number

		return SpecificationResponse(
			id=spec.id,
			supply_contract_id=spec.supply_contract_id,
			supply_contract_number=supply_contract_number,
			spec_number=spec.spec_number,
			spec_date=spec.spec_date,
			spec_text=spec.spec_text or "",
			spec_items=spec_items,
		)
