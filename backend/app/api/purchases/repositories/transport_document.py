"""Репозиторий реестра документов перевозки / экспедиции (§1.2)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.company.models.company import Company, CompanyRelation, CompanyRelationType
from app.api.purchases.models import (
	TRANSPORT_CHILD_PARENT,
	TRANSPORT_FRAMEWORK_TYPES,
	TransportDocument,
	TransportDocumentType,
)


def _utc_now_naive() -> datetime:
	return datetime.now(timezone.utc).replace(tzinfo=None)


class TransportDocumentRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def get_by_id(self, document_id: int) -> Optional[TransportDocument]:
		result = await self.session.execute(
			select(TransportDocument).where(TransportDocument.id == document_id)
		)
		return result.scalar_one_or_none()

	async def get_by_ids(self, document_ids: list[int]) -> list[TransportDocument]:
		if not document_ids:
			return []
		result = await self.session.execute(
			select(TransportDocument).where(TransportDocument.id.in_(document_ids))
		)
		return list(result.scalars().all())

	async def list_for_picker(
		self,
		*,
		owner_company_id: int,
		carrier_company_id: int,
		doc_type: TransportDocumentType,
	) -> list[TransportDocument]:
		"""Рамочные договоры для пикера (справа от списка организаций)."""
		if doc_type not in TRANSPORT_FRAMEWORK_TYPES:
			return []
		query = (
			select(TransportDocument)
			.where(
				TransportDocument.owner_company_id == owner_company_id,
				TransportDocument.carrier_company_id == carrier_company_id,
				TransportDocument.doc_type == doc_type,
				TransportDocument.parent_id.is_(None),
			)
			.order_by(TransportDocument.date.desc(), TransportDocument.id.desc())
		)
		result = await self.session.execute(query)
		return list(result.scalars().all())

	async def list_by_deal(
		self,
		*,
		owner_company_id: int,
		deal_id: int,
	) -> list[TransportDocument]:
		query = (
			select(TransportDocument)
			.where(
				TransportDocument.owner_company_id == owner_company_id,
				TransportDocument.deal_id == deal_id,
			)
			.order_by(TransportDocument.id.asc())
		)
		result = await self.session.execute(query)
		return list(result.scalars().all())

	async def list_children(
		self,
		*,
		parent_id: int,
		doc_type: Optional[TransportDocumentType] = None,
	) -> list[TransportDocument]:
		clauses = [TransportDocument.parent_id == parent_id]
		if doc_type is not None:
			clauses.append(TransportDocument.doc_type == doc_type)
		query = (
			select(TransportDocument)
			.where(and_(*clauses))
			.order_by(TransportDocument.id.asc())
		)
		result = await self.session.execute(query)
		return list(result.scalars().all())

	async def is_carrier_relation(self, owner_company_id: int, carrier_company_id: int) -> bool:
		result = await self.session.execute(
			select(CompanyRelation.id).where(
				CompanyRelation.company_id == owner_company_id,
				CompanyRelation.related_company_id == carrier_company_id,
				CompanyRelation.relation_type == CompanyRelationType.CARRIER,
			).limit(1)
		)
		return result.scalar_one_or_none() is not None

	async def get_company_names(self, company_ids: list[int]) -> dict[int, str]:
		if not company_ids:
			return {}
		result = await self.session.execute(
			select(Company.id, Company.full_name, Company.name).where(Company.id.in_(company_ids))
		)
		out: dict[int, str] = {}
		for row in result.all():
			out[row[0]] = (row[1] or row[2] or "").strip()
		return out

	async def generate_next_number(
		self,
		*,
		owner_company_id: int,
		carrier_company_id: int,
		doc_type: TransportDocumentType,
		parent_id: Optional[int] = None,
		year: Optional[int] = None,
	) -> str:
		"""Нумерация по ТЗ: рамочные 00001; договор-заявка 000001; дети 1,2,3… внутри родителя."""
		if doc_type in TRANSPORT_CHILD_PARENT:
			if parent_id is None:
				raise ValueError("parent_id is required for child document type")
			result = await self.session.execute(
				select(func.max(TransportDocument.number)).where(
					TransportDocument.parent_id == parent_id,
					TransportDocument.doc_type == doc_type,
				)
			)
			max_number = result.scalar()
			next_n = 1
			if max_number:
				digits = "".join(ch for ch in str(max_number) if ch.isdigit())
				try:
					next_n = int(digits) + 1 if digits else 1
				except ValueError:
					next_n = 1
			return str(next_n)

		current_year = year or _utc_now_naive().year
		year_start = datetime(current_year, 1, 1)
		year_end = datetime(current_year + 1, 1, 1)
		query = (
			select(func.max(TransportDocument.number))
			.where(
				TransportDocument.owner_company_id == owner_company_id,
				TransportDocument.carrier_company_id == carrier_company_id,
				TransportDocument.doc_type == doc_type,
				TransportDocument.parent_id.is_(None),
				TransportDocument.date >= year_start,
				TransportDocument.date < year_end,
			)
		)
		result = await self.session.execute(query)
		max_number = result.scalar()
		next_n = 1
		if max_number:
			digits = "".join(ch for ch in str(max_number) if ch.isdigit())
			try:
				next_n = int(digits) + 1 if digits else 1
			except ValueError:
				next_n = 1
		if doc_type == TransportDocumentType.CARRIAGE_ORDER:
			return f"{next_n:06d}"
		return f"{next_n:05d}"

	async def create(
		self,
		*,
		owner_company_id: int,
		carrier_company_id: int,
		doc_type: TransportDocumentType,
		number: str,
		date: datetime,
		parent_id: Optional[int] = None,
		deal_id: Optional[int] = None,
		payload_json: Optional[dict] = None,
	) -> TransportDocument:
		if date.tzinfo is not None:
			date = date.astimezone(timezone.utc).replace(tzinfo=None)
		doc = TransportDocument(
			owner_company_id=owner_company_id,
			carrier_company_id=carrier_company_id,
			doc_type=doc_type,
			number=number.strip(),
			date=date,
			parent_id=parent_id,
			deal_id=deal_id,
			payload_json=payload_json,
		)
		self.session.add(doc)
		await self.session.flush()
		return doc
