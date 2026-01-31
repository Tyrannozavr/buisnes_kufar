"""Репозиторий: чтение/запись форм документов по deal_id и document_type."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.documents.models import DealDocumentForm


class DocumentFormRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, deal_id: int, document_type: str) -> Optional[DealDocumentForm]:
        q = select(DealDocumentForm).where(
            DealDocumentForm.deal_id == deal_id,
            DealDocumentForm.document_type == document_type,
        )
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def save(
        self,
        deal_id: int,
        document_type: str,
        payload: dict,
        updated_by_company_id: Optional[int],
    ) -> DealDocumentForm:
        row = await self.get(deal_id, document_type)
        if row:
            row.payload = payload
            row.updated_by_company_id = updated_by_company_id
            await self.session.flush()
            await self.session.refresh(row)
            return row
        row = DealDocumentForm(
            deal_id=deal_id,
            document_type=document_type,
            payload=payload,
            updated_by_company_id=updated_by_company_id,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return row
