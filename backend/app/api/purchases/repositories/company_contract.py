from datetime import datetime
from typing import Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.models import CompanyContract


class CompanyContractRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def list_by_counterparty(
		self,
		company_id: int,
		counterparty_company_id: int,
	) -> list[CompanyContract]:
		query = (
			select(CompanyContract)
			.where(
				or_(
					and_(
						CompanyContract.seller_company_id == company_id,
						CompanyContract.buyer_company_id == counterparty_company_id,
					),
					and_(
						CompanyContract.buyer_company_id == company_id,
						CompanyContract.seller_company_id == counterparty_company_id,
					),
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

		contract = CompanyContract(
			seller_company_id=seller_company_id,
			buyer_company_id=buyer_company_id,
			number=number,
			date=date,
		)
		self.session.add(contract)
		await self.session.flush()
		return contract
