from typing import Optional, Sequence

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.company.schemas.company_officials import CompanyOfficialCreate, CompanyOfficialUpdate, \
    CompanyOfficialPartialUpdate
from app.api.company.models.official import CompanyOfficial


class CompanyOfficialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, official_id: int) -> Optional[CompanyOfficial]:
        query = select(CompanyOfficial).where(CompanyOfficial.id == official_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_company_id(self, company_id: int) -> Sequence[CompanyOfficial]:
        query = select(CompanyOfficial).where(CompanyOfficial.company_id == company_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, official_data: CompanyOfficialCreate, company_id: int) -> CompanyOfficial:
        official = CompanyOfficial(**official_data.model_dump(), company_id=company_id)
        self.session.add(official)
        await self.session.commit()
        await self.session.refresh(official)
        return official

    async def update(self, official_id: int, official_data: CompanyOfficialUpdate) -> Optional[CompanyOfficial]:
        update_data = official_data.model_dump(exclude_unset=True)
        if update_data:
            await self.session.execute(
                update(CompanyOfficial)
                .where(CompanyOfficial.id == official_id)
                .values(**update_data)
            )
            await self.session.commit()
        return await self.get_by_id(official_id)

    async def partial_update(self,
                             official_id: int,
                             official_data: CompanyOfficialPartialUpdate
                             ) -> Optional[CompanyOfficial]:
        update_data = official_data.model_dump(exclude_unset=True)
        if update_data:
            await self.session.execute(
                update(CompanyOfficial)
                .where(CompanyOfficial.id == official_id)
                .values(**update_data)
            )
            await self.session.commit()
        return await self.get_by_id(official_id)

    async def delete(self, official_id: int) -> bool:
        result = await self.session.execute(
            delete(CompanyOfficial).where(CompanyOfficial.id == official_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def delete_by_company_id(self, company_id: int) -> bool:
        result = await self.session.execute(
            delete(CompanyOfficial).where(CompanyOfficial.company_id == company_id)
        )
        await self.session.commit()
        return result.rowcount > 0