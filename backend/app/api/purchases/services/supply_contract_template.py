from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.models import SupplyContractTemplate, SupplyContractTemplateType
from app.api.purchases.repositories.supply_contract_template import SupplyContractTemplateRepository
from app.api.purchases.schemas import (
	SupplyContractTemplateCreate,
	SupplyContractTemplateResponse,
	SupplyContractTemplateUpdate,
)


class SupplyContractTemplateAlreadyExistsError(Exception):
	"""Шаблон с таким именем уже существует для компании и типа."""


class SupplyContractTemplateService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repository = SupplyContractTemplateRepository(session)

	@staticmethod
	def _to_response(template: SupplyContractTemplate) -> SupplyContractTemplateResponse:
		return SupplyContractTemplateResponse(
			id=template.id,
			company_id=template.company_id,
			type=template.type.value,
			name=template.name,
			content_html=template.content_html,
			is_default=template.is_default,
			created_at=template.created_at,
			updated_at=template.updated_at,
		)

	async def list_templates(
		self,
		company_id: int,
		template_type: SupplyContractTemplateType,
	) -> list[SupplyContractTemplateResponse]:
		templates = await self.repository.list_by_company(company_id, template_type)
		return [self._to_response(t) for t in templates]

	async def get_default_template(
		self,
		company_id: int,
		template_type: SupplyContractTemplateType,
	) -> Optional[SupplyContractTemplateResponse]:
		template = await self.repository.get_default(company_id, template_type)
		if template is None:
			return None
		return self._to_response(template)

	async def get_template(
		self,
		template_id: int,
		company_id: int,
	) -> Optional[SupplyContractTemplateResponse]:
		template = await self.repository.get_by_id(template_id, company_id)
		if template is None:
			return None
		return self._to_response(template)

	async def create_template(
		self,
		company_id: int,
		data: SupplyContractTemplateCreate,
	) -> SupplyContractTemplateResponse:
		template_type = SupplyContractTemplateType(data.type)
		name = data.name.strip()
		if not name:
			raise ValueError("Template name is required")

		if data.is_default:
			await self.repository.unset_default(company_id, template_type)

		try:
			template = await self.repository.create(
				company_id=company_id,
				template_type=template_type,
				name=name,
				content_html=data.content_html or "",
				is_default=bool(data.is_default),
			)
			await self.session.commit()
			await self.session.refresh(template)
		except IntegrityError as exc:
			await self.session.rollback()
			raise SupplyContractTemplateAlreadyExistsError() from exc

		return self._to_response(template)

	async def update_template(
		self,
		template_id: int,
		company_id: int,
		data: SupplyContractTemplateUpdate,
	) -> Optional[SupplyContractTemplateResponse]:
		template = await self.repository.get_by_id(template_id, company_id)
		if template is None:
			return None

		if data.name is not None:
			name = data.name.strip()
			if not name:
				raise ValueError("Template name is required")
			template.name = name

		if data.content_html is not None:
			template.content_html = data.content_html

		if data.is_default is not None:
			if data.is_default:
				await self.repository.unset_default(
					company_id,
					template.type,
					exclude_id=template.id,
				)
			template.is_default = data.is_default

		try:
			await self.session.commit()
			await self.session.refresh(template)
		except IntegrityError as exc:
			await self.session.rollback()
			raise SupplyContractTemplateAlreadyExistsError() from exc

		return self._to_response(template)

	async def delete_template(
		self,
		template_id: int,
		company_id: int,
	) -> bool:
		template = await self.repository.get_by_id(template_id, company_id)
		if template is None:
			return False
		await self.repository.delete(template)
		await self.session.commit()
		return True
