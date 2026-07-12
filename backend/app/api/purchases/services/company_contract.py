from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.repositories.company_contract import CompanyContractRepository
from app.api.purchases.schemas import (
	CompanyContractCreate,
	CompanyContractListResponse,
	CompanyContractResponse,
	CompanyContractUpdate,
)


class CompanyContractDuplicateError(Exception):
	"""Договор с таким номером для пары компаний уже существует."""


class CompanyContractAccessError(Exception):
	"""Нет доступа к договору."""


class CompanyContractService:
	"""Договоры компании с контрагентом (ЛК «Договоры»)."""

	def __init__(self, session: AsyncSession):
		self.session = session
		self.repository = CompanyContractRepository(session)

	@staticmethod
	def _counterparty_meta(
		contract,
		company_id: int,
		names: dict[int, str],
	) -> tuple[int, str, str]:
		if contract.seller_company_id == company_id:
			counterparty_id = contract.buyer_company_id
			counterparty_role = "buyer"
		else:
			counterparty_id = contract.seller_company_id
			counterparty_role = "seller"
		return counterparty_id, names.get(counterparty_id, ""), counterparty_role

	def _to_response(
		self,
		contract,
		company_id: int,
		names: dict[int, str],
	) -> CompanyContractResponse:
		counterparty_id, counterparty_name, counterparty_role = self._counterparty_meta(
			contract, company_id, names
		)
		return CompanyContractResponse(
			id=contract.id,
			seller_company_id=contract.seller_company_id,
			buyer_company_id=contract.buyer_company_id,
			number=contract.number,
			date=contract.date,
			counterparty_company_id=counterparty_id,
			counterparty_name=counterparty_name,
			counterparty_role=counterparty_role,
		)

	async def _names_for_contracts(self, contracts, company_id: int) -> dict[int, str]:
		ids: set[int] = set()
		for contract in contracts:
			ids.add(contract.seller_company_id)
			ids.add(contract.buyer_company_id)
		return await self.repository.get_company_names(list(ids))

	async def list_by_counterparty(
		self,
		company_id: int,
		counterparty_company_id: int,
	) -> CompanyContractListResponse:
		contracts = await self.repository.list_by_counterparty(company_id, counterparty_company_id)
		names = await self._names_for_contracts(contracts, company_id)
		return CompanyContractListResponse(
			contracts=[
				self._to_response(item, company_id, names) for item in contracts
			]
		)

	async def list_for_company(self, company_id: int) -> CompanyContractListResponse:
		contracts = await self.repository.list_for_company(company_id)
		names = await self._names_for_contracts(contracts, company_id)
		return CompanyContractListResponse(
			contracts=[
				self._to_response(item, company_id, names) for item in contracts
			]
		)

	async def get_for_companies(
		self,
		contract_id: int,
		company_id: int,
		counterparty_company_id: int,
	) -> Optional[CompanyContractResponse]:
		contract = await self.repository.get_by_id(contract_id)
		if contract is None:
			return None
		pair = {contract.seller_company_id, contract.buyer_company_id}
		if company_id not in pair or counterparty_company_id not in pair:
			return None
		names = await self.repository.get_company_names(list(pair))
		return self._to_response(contract, company_id, names)

	async def create(
		self,
		company_id: int,
		payload: CompanyContractCreate,
	) -> CompanyContractResponse:
		if payload.counterparty_company_id == company_id:
			raise ValueError("Counterparty must differ from current company")

		if payload.relation == "as_seller":
			seller_id, buyer_id = company_id, payload.counterparty_company_id
		else:
			seller_id, buyer_id = payload.counterparty_company_id, company_id

		try:
			contract = await self.repository.create_contract(
				seller_company_id=seller_id,
				buyer_company_id=buyer_id,
				number=payload.number,
				date=payload.date,
			)
			await self.session.commit()
			await self.session.refresh(contract)
		except IntegrityError as exc:
			await self.session.rollback()
			raise CompanyContractDuplicateError() from exc

		names = await self.repository.get_company_names([seller_id, buyer_id])
		return self._to_response(contract, company_id, names)

	async def update(
		self,
		contract_id: int,
		company_id: int,
		payload: CompanyContractUpdate,
	) -> CompanyContractResponse:
		contract = await self.repository.get_by_id(contract_id)
		if contract is None:
			raise CompanyContractAccessError()
		if company_id not in (contract.seller_company_id, contract.buyer_company_id):
			raise CompanyContractAccessError()

		if payload.number is None and payload.date is None:
			raise ValueError("At least one field must be provided")

		try:
			await self.repository.update_contract(
				contract,
				number=payload.number,
				date=payload.date,
			)
			await self.session.commit()
			await self.session.refresh(contract)
		except IntegrityError as exc:
			await self.session.rollback()
			raise CompanyContractDuplicateError() from exc

		names = await self.repository.get_company_names(
			[contract.seller_company_id, contract.buyer_company_id]
		)
		return self._to_response(contract, company_id, names)

	async def delete(self, contract_id: int, company_id: int) -> None:
		contract = await self.repository.get_by_id(contract_id)
		if contract is None:
			raise CompanyContractAccessError()
		if company_id not in (contract.seller_company_id, contract.buyer_company_id):
			raise CompanyContractAccessError()

		await self.repository.delete_contract(contract)
		await self.session.commit()
