from typing import Optional

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.models import ContractConditionTemplate


class ContractConditionTemplateRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def list_by_company(
		self,
		company_id: int,
		template_type: Optional[str] = None,
	) -> list[ContractConditionTemplate]:
		query = select(ContractConditionTemplate).where(
			ContractConditionTemplate.company_id == company_id
		)
		if template_type:
			query = query.where(ContractConditionTemplate.type == template_type)
		query = query.order_by(
			ContractConditionTemplate.is_default.desc(),
			ContractConditionTemplate.name,
		)
		result = await self.session.execute(query)
		return list(result.scalars().all())

	async def get_default(
		self,
		company_id: int,
		template_type: str,
	) -> Optional[ContractConditionTemplate]:
		result = await self.session.execute(
			select(ContractConditionTemplate).where(
				and_(
					ContractConditionTemplate.company_id == company_id,
					ContractConditionTemplate.type == template_type,
					ContractConditionTemplate.is_default.is_(True),
				)
			)
		)
		return result.scalar_one_or_none()

	async def get_by_id(
		self,
		template_id: int,
		company_id: int,
	) -> Optional[ContractConditionTemplate]:
		result = await self.session.execute(
			select(ContractConditionTemplate).where(
				and_(
					ContractConditionTemplate.id == template_id,
					ContractConditionTemplate.company_id == company_id,
				)
			)
		)
		return result.scalar_one_or_none()

	async def create(
		self,
		*,
		company_id: int,
		template_type: str,
		name: str,
		content_text: str,
		is_default: bool,
	) -> ContractConditionTemplate:
		template = ContractConditionTemplate(
			company_id=company_id,
			type=template_type,
			name=name,
			content_text=content_text,
			is_default=is_default,
		)
		self.session.add(template)
		await self.session.flush()
		return template

	async def unset_default(
		self,
		company_id: int,
		template_type: str,
		exclude_id: Optional[int] = None,
	) -> None:
		query = (
			update(ContractConditionTemplate)
			.where(
				and_(
					ContractConditionTemplate.company_id == company_id,
					ContractConditionTemplate.type == template_type,
					ContractConditionTemplate.is_default.is_(True),
				)
			)
			.values(is_default=False)
		)
		if exclude_id is not None:
			query = query.where(ContractConditionTemplate.id != exclude_id)
		await self.session.execute(query)

	async def delete(self, template: ContractConditionTemplate) -> None:
		await self.session.delete(template)

	async def upsert_seed(
		self,
		*,
		company_id: int,
		template_type: str,
		name: str,
		content_text: str,
		is_default: bool = False,
	) -> ContractConditionTemplate:
		result = await self.session.execute(
			select(ContractConditionTemplate).where(
				and_(
					ContractConditionTemplate.company_id == company_id,
					ContractConditionTemplate.type == template_type,
					ContractConditionTemplate.name == name,
				)
			)
		)
		existing = result.scalar_one_or_none()
		if existing:
			existing.content_text = content_text
			if is_default:
				await self.unset_default(company_id, template_type, exclude_id=existing.id)
				existing.is_default = True
			return existing
		if is_default:
			await self.unset_default(company_id, template_type)
		return await self.create(
			company_id=company_id,
			template_type=template_type,
			name=name,
			content_text=content_text,
			is_default=is_default,
		)
