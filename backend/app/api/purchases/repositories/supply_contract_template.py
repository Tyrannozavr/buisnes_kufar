from typing import Optional

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.models import SupplyContractTemplate, SupplyContractTemplateType


class SupplyContractTemplateRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def list_by_company(
		self,
		company_id: int,
		template_type: SupplyContractTemplateType,
	) -> list[SupplyContractTemplate]:
		result = await self.session.execute(
			select(SupplyContractTemplate)
			.where(
				and_(
					SupplyContractTemplate.company_id == company_id,
					SupplyContractTemplate.type == template_type,
				)
			)
			.order_by(SupplyContractTemplate.is_default.desc(), SupplyContractTemplate.name)
		)
		return list(result.scalars().all())

	async def get_default(
		self,
		company_id: int,
		template_type: SupplyContractTemplateType,
	) -> Optional[SupplyContractTemplate]:
		result = await self.session.execute(
			select(SupplyContractTemplate).where(
				and_(
					SupplyContractTemplate.company_id == company_id,
					SupplyContractTemplate.type == template_type,
					SupplyContractTemplate.is_default.is_(True),
				)
			)
		)
		return result.scalar_one_or_none()

	async def get_by_id(
		self,
		template_id: int,
		company_id: int,
	) -> Optional[SupplyContractTemplate]:
		result = await self.session.execute(
			select(SupplyContractTemplate).where(
				and_(
					SupplyContractTemplate.id == template_id,
					SupplyContractTemplate.company_id == company_id,
				)
			)
		)
		return result.scalar_one_or_none()

	async def create(
		self,
		*,
		company_id: int,
		template_type: SupplyContractTemplateType,
		name: str,
		content_html: str,
		is_default: bool,
	) -> SupplyContractTemplate:
		template = SupplyContractTemplate(
			company_id=company_id,
			type=template_type,
			name=name,
			content_html=content_html,
			is_default=is_default,
		)
		self.session.add(template)
		await self.session.flush()
		return template

	async def unset_default(
		self,
		company_id: int,
		template_type: SupplyContractTemplateType,
		exclude_id: Optional[int] = None,
	) -> None:
		query = (
			update(SupplyContractTemplate)
			.where(
				and_(
					SupplyContractTemplate.company_id == company_id,
					SupplyContractTemplate.type == template_type,
					SupplyContractTemplate.is_default.is_(True),
				)
			)
			.values(is_default=False)
		)
		if exclude_id is not None:
			query = query.where(SupplyContractTemplate.id != exclude_id)
		await self.session.execute(query)

	async def delete(self, template: SupplyContractTemplate) -> None:
		await self.session.delete(template)
