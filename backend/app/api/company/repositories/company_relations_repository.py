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
