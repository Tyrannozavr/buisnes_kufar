from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.models import ContractConditionTemplateType
from app.api.purchases.repositories.contract_condition_template import (
	ContractConditionTemplateRepository,
)
from app.api.purchases.schemas import (
	ContractConditionTemplateCreate,
	ContractConditionTemplateResponse,
	ContractConditionTemplateUpdate,
)

ALLOWED_TYPES = {
	ContractConditionTemplateType.BILL_CONTRACT.value,
	ContractConditionTemplateType.BILL_OFFER.value,
}


class ContractConditionTemplateAlreadyExistsError(Exception):
	"""Шаблон с таким именем уже существует для компании и типа."""


class ContractConditionTemplateService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repository = ContractConditionTemplateRepository(session)

	@staticmethod
	def _to_response(template) -> ContractConditionTemplateResponse:
		return ContractConditionTemplateResponse(
			id=template.id,
			company_id=template.company_id,
			type=template.type,
			name=template.name,
			content_text=template.content_text,
			is_default=template.is_default,
			created_at=template.created_at,
			updated_at=template.updated_at,
		)

	async def list_templates(
		self,
		company_id: int,
		template_type: Optional[str] = None,
	) -> list[ContractConditionTemplateResponse]:
		if template_type and template_type not in ALLOWED_TYPES:
			raise ValueError("Invalid template type")
		templates = await self.repository.list_by_company(company_id, template_type)
		return [self._to_response(t) for t in templates]

	async def get_default_template(
		self,
		company_id: int,
		template_type: str,
	) -> Optional[ContractConditionTemplateResponse]:
		if template_type not in ALLOWED_TYPES:
			raise ValueError("Invalid template type")
		template = await self.repository.get_default(company_id, template_type)
		if template is None:
			return None
		return self._to_response(template)

	async def get_template(
		self,
		template_id: int,
		company_id: int,
	) -> Optional[ContractConditionTemplateResponse]:
		template = await self.repository.get_by_id(template_id, company_id)
		if template is None:
			return None
		return self._to_response(template)

	async def create_template(
		self,
		company_id: int,
		data: ContractConditionTemplateCreate,
	) -> ContractConditionTemplateResponse:
		if data.type not in ALLOWED_TYPES:
			raise ValueError("Invalid template type")
		name = data.name.strip()
		if not name:
			raise ValueError("Template name is required")

		if data.is_default:
			await self.repository.unset_default(company_id, data.type)

		try:
			template = await self.repository.create(
				company_id=company_id,
				template_type=data.type,
				name=name,
				content_text=data.content_text or "",
				is_default=data.is_default,
			)
		except IntegrityError as e:
			raise ContractConditionTemplateAlreadyExistsError() from e

		await self.session.commit()
		await self.session.refresh(template)
		return self._to_response(template)

	async def update_template(
		self,
		template_id: int,
		company_id: int,
		data: ContractConditionTemplateUpdate,
	) -> Optional[ContractConditionTemplateResponse]:
		template = await self.repository.get_by_id(template_id, company_id)
		if template is None:
			return None

		if data.name is not None:
			name = data.name.strip()
			if not name:
				raise ValueError("Template name is required")
			template.name = name
		if data.content_text is not None:
			template.content_text = data.content_text
		if data.is_default is True:
			await self.repository.unset_default(company_id, template.type, exclude_id=template.id)
			template.is_default = True
		elif data.is_default is False:
			template.is_default = False

		try:
			await self.session.commit()
		except IntegrityError as e:
			await self.session.rollback()
			raise ContractConditionTemplateAlreadyExistsError() from e

		await self.session.refresh(template)
		return self._to_response(template)

	async def delete_template(self, template_id: int, company_id: int) -> bool:
		template = await self.repository.get_by_id(template_id, company_id)
		if template is None:
			return False
		await self.repository.delete(template)
		await self.session.commit()
		return True
