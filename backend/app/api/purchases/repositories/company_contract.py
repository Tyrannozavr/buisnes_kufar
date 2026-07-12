from datetime import datetime
from typing import Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.company.models.company import Company
from app.api.purchases.models import CompanyContract


class CompanyContractRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	def _pair_filter(self, company_id: int, counterparty_company_id: int):
		return or_(
			and_(
				CompanyContract.seller_company_id == company_id,
				CompanyContract.buyer_company_id == counterparty_company_id,
			),
			and_(
				CompanyContract.buyer_company_id == company_id,
				CompanyContract.seller_company_id == counterparty_company_id,
			),
		)

	async def list_by_counterparty(
		self,
		company_id: int,
		counterparty_company_id: int,
	) -> list[CompanyContract]:
		query = (
			select(CompanyContract)
			.where(self._pair_filter(company_id, counterparty_company_id))
			.order_by(CompanyContract.date.desc(), CompanyContract.id.desc())
		)
		result = await self.session.execute(query)
		return list(result.scalars().all())

	async def list_for_company(self, company_id: int) -> list[CompanyContract]:
		query = (
			select(CompanyContract)
			.where(
				or_(
					CompanyContract.seller_company_id == company_id,
					CompanyContract.buyer_company_id == company_id,
				)
			)
			.order_by(CompanyContract.date.desc(), CompanyContract.id.desc())
		)
		result = await self.session.execute(query)
		return list(result.scalars().all())

	async def get_by_id(self, contract_id: int) -> Optional[CompanyContract]:
		result = await self.session.execute(
			select(CompanyContract).where(CompanyContract.id == contract_id)
		)
		return result.scalar_one_or_none()

	async def get_company_names(self, company_ids: list[int]) -> dict[int, str]:
		if not company_ids:
			return {}
		result = await self.session.execute(
			select(Company.id, Company.full_name).where(Company.id.in_(company_ids))
		)
		return {row[0]: row[1] for row in result.all()}

	async def create_contract(
		self,
		*,
		seller_company_id: int,
		buyer_company_id: int,
		number: str,
		date: datetime,
	) -> CompanyContract:
		contract = CompanyContract(
			seller_company_id=seller_company_id,
			buyer_company_id=buyer_company_id,
			number=number.strip(),
			date=date,
		)
		self.session.add(contract)
		await self.session.flush()
		return contract

	async def update_contract(
		self,
		contract: CompanyContract,
		*,
		number: Optional[str] = None,
		date: Optional[datetime] = None,
	) -> CompanyContract:
		if number is not None:
			contract.number = number.strip()
		if date is not None:
			contract.date = date
		return contract

	async def delete_contract(self, contract: CompanyContract) -> None:
		await self.session.delete(contract)

	async def upsert_contract(
		self,
		*,
		seller_company_id: int,
		buyer_company_id: int,
		number: str,
		date: datetime,
	) -> CompanyContract:
		result = await self.session.execute(
			select(CompanyContract).where(
				CompanyContract.seller_company_id == seller_company_id,
				CompanyContract.buyer_company_id == buyer_company_id,
				CompanyContract.number == number,
			)
		)
		existing = result.scalar_one_or_none()
		if existing:
			existing.date = date
			return existing

		return await self.create_contract(
			seller_company_id=seller_company_id,
			buyer_company_id=buyer_company_id,
			number=number,
			date=date,
		)
