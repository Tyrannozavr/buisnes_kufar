from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.repositories.company_contract import CompanyContractRepository
from app.api.purchases.schemas import (
	CompanyContractCreate,
	CompanyContractListResponse,
	CompanyContractNextNumberResponse,
	CompanyContractResponse,
	CompanyContractUpdate,
)


def _utc_now_naive() -> datetime:
	return datetime.now(timezone.utc).replace(tzinfo=None)


def _normalize_datetime(value: datetime) -> datetime:
	if value.tzinfo is None:
		return value
	return value.astimezone(timezone.utc).replace(tzinfo=None)


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

	@staticmethod
	def _resolve_pair(
		company_id: int,
		counterparty_company_id: int,
		relation: str,
	) -> tuple[int, int]:
		if relation == "as_seller":
			return company_id, counterparty_company_id
		return counterparty_company_id, company_id

	async def get_next_number(
		self,
		company_id: int,
		*,
		relation: str = "as_seller",
		counterparty_company_id: int | None = None,
	) -> CompanyContractNextNumberResponse:
		if relation == "as_buyer" and not counterparty_company_id:
			raise ValueError("counterparty_company_id is required when relation is as_buyer")
		seller_id = (
			company_id
			if relation == "as_seller"
			else counterparty_company_id  # type: ignore[assignment]
		)
		now = _utc_now_naive()
		number = await self.repository.generate_next_number(seller_id, year=now.year)
		return CompanyContractNextNumberResponse(number=number, date=now)

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

		seller_id, buyer_id = self._resolve_pair(
			company_id,
			payload.counterparty_company_id,
			payload.relation,
		)
		contract_date = _normalize_datetime(payload.date) if payload.date else _utc_now_naive()
		contract_number = (payload.number or "").strip()
		if not contract_number:
			contract_number = await self.repository.generate_next_number(
				seller_id,
				year=contract_date.year,
			)

		try:
			contract = await self.repository.create_contract(
				seller_company_id=seller_id,
				buyer_company_id=buyer_id,
				number=contract_number,
				date=contract_date,
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
				date=_normalize_datetime(payload.date) if payload.date is not None else None,
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
