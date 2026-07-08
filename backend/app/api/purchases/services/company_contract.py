from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.repositories.company_contract import CompanyContractRepository
from app.api.purchases.schemas import CompanyContractListResponse, CompanyContractResponse


class CompanyContractService:
	"""Договоры компании с контрагентом (ЛК «Договоры»)."""

	def __init__(self, session: AsyncSession):
		self.session = session
		self.repository = CompanyContractRepository(session)

	async def list_by_counterparty(
		self,
		company_id: int,
		counterparty_company_id: int,
	) -> CompanyContractListResponse:
		contracts = await self.repository.list_by_counterparty(company_id, counterparty_company_id)
		return CompanyContractListResponse(
			contracts=[CompanyContractResponse.model_validate(item) for item in contracts]
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
		return CompanyContractResponse.model_validate(contract)
