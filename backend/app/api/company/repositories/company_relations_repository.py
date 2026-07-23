from typing import List, Optional

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.company.models.company import CompanyRelation, CompanyRelationType, Company
from app.api.company.schemas.company import CompanyRelationCreate


class CompanyRelationsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_relation(self, company_id: int, data: CompanyRelationCreate) -> CompanyRelation:
        relation = CompanyRelation(
            company_id=company_id,
            related_company_id=data.related_company_id,
            relation_type=data.relation_type
        )
        self.session.add(relation)
        await self.session.commit()
        await self.session.refresh(relation)
        return relation

    async def remove_relation(self, company_id: int, related_company_id: int,
                              relation_type: CompanyRelationType) -> bool:
        stmt = delete(CompanyRelation).where(
            CompanyRelation.company_id == company_id,
            CompanyRelation.related_company_id == related_company_id,
            CompanyRelation.relation_type == relation_type
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_relations(self, company_id: int, relation_type: Optional[CompanyRelationType] = None) -> List[
        CompanyRelation]:
        stmt = select(CompanyRelation).where(CompanyRelation.company_id == company_id)
        if relation_type:
            stmt = stmt.where(CompanyRelation.relation_type == relation_type)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_related_to(self, related_company_id: int, relation_type: Optional[CompanyRelationType] = None) -> \
    List[CompanyRelation]:
        stmt = select(CompanyRelation).where(CompanyRelation.related_company_id == related_company_id)
        if relation_type:
            stmt = stmt.where(CompanyRelation.relation_type == relation_type)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_related_companies(self, company_id: int, relation_type: CompanyRelationType, page: int = 1,
                                    per_page: int = 10):
        stmt = (
            select(Company)
            .options(selectinload(Company.officials))
            .join(CompanyRelation, Company.id == CompanyRelation.related_company_id)
            .where(CompanyRelation.company_id == company_id)
            .where(CompanyRelation.relation_type == relation_type)
            .order_by(Company.id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        count_stmt = (
            select(func.count(Company.id))
            .join(CompanyRelation, Company.id == CompanyRelation.related_company_id)
            .where(CompanyRelation.company_id == company_id)
            .where(CompanyRelation.relation_type == relation_type)
        )
        total = (await self.session.execute(count_stmt)).scalar()
        result = await self.session.execute(stmt)
        companies = result.scalars().all()
        return companies, total

    async def get_counterparties_companies(
        self,
        company_id: int,
        page: int = 1,
        per_page: int = 10,
    ):
        """Общий список контрагентов: партнёры + покупатели + поставщики + перевозчики (distinct)."""
        types = [
            CompanyRelationType.PARTNER,
            CompanyRelationType.BUYER,
            CompanyRelationType.SUPPLIER,
            CompanyRelationType.CARRIER,
        ]
        base = (
            select(Company.id)
            .join(CompanyRelation, Company.id == CompanyRelation.related_company_id)
            .where(CompanyRelation.company_id == company_id)
            .where(CompanyRelation.relation_type.in_(types))
            .distinct()
        )
        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.session.execute(count_stmt)).scalar() or 0

        id_page = (
            base.order_by(Company.id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        ids = list((await self.session.execute(id_page)).scalars().all())
        if not ids:
            return [], total

        stmt = (
            select(Company)
            .options(selectinload(Company.officials))
            .where(Company.id.in_(ids))
            .order_by(Company.id)
        )
        companies = list((await self.session.execute(stmt)).scalars().all())
        return companies, total

    async def remove_all_relations_to(
        self,
        company_id: int,
        related_company_id: int,
    ) -> int:
        stmt = delete(CompanyRelation).where(
            CompanyRelation.company_id == company_id,
            CompanyRelation.related_company_id == related_company_id,
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount or 0

    async def ensure_relation(
        self,
        company_id: int,
        related_company_id: int,
        relation_type: CompanyRelationType,
    ) -> CompanyRelation:
        existing = (
            await self.session.execute(
                select(CompanyRelation).where(
                    CompanyRelation.company_id == company_id,
                    CompanyRelation.related_company_id == related_company_id,
                    CompanyRelation.relation_type == relation_type,
                ).limit(1)
            )
        ).scalar_one_or_none()
        if existing:
            return existing
        return await self.add_relation(
            company_id,
            CompanyRelationCreate(
                related_company_id=related_company_id,
                relation_type=relation_type,
            ),
        )
