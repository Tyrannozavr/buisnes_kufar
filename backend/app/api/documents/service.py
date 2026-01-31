"""
Сервис документов: проверка прав (доступ только buyer/seller сделки), GET/PUT.
"""
from datetime import datetime
from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.documents.models import DealDocumentForm
from app.api.documents.repository import DocumentFormRepository
from app.api.documents.schemas import DocumentResponse
from app.api.purchases.models import Order


async def get_order_and_company_role(
    session: AsyncSession, deal_id: int, company_id: int
) -> Tuple[Optional[Order], Optional[str]]:
    """Возвращает (order, 'buyer'|'seller'|None). None если нет доступа."""
    q = select(Order).where(Order.id == deal_id)
    result = await session.execute(q)
    order = result.scalar_one_or_none()
    if not order:
        return None, None
    if order.buyer_company_id == company_id:
        return order, "buyer"
    if order.seller_company_id == company_id:
        return order, "seller"
    return None, None


class DocumentFormService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DocumentFormRepository(session)

    async def get_document(self, deal_id: int, document_type: str, company_id: int) -> Optional[DocumentResponse]:
        _, role = await get_order_and_company_role(self.session, deal_id, company_id)
        if not role:
            raise HTTPException(status_code=404, detail="Deal not found or access denied")
        if document_type not in ("order", "bill", "supply_contract", "act", "invoice", "contract", "others"):
            raise HTTPException(status_code=400, detail=f"Invalid document_type: {document_type}")
        row = await self.repo.get(deal_id, document_type)
        if not row:
            return DocumentResponse(
                deal_id=deal_id,
                document_type=document_type,
                payload={},
                updated_at=datetime.utcnow(),
                updated_by_company_id=None,
            )
        return DocumentResponse(
            deal_id=row.deal_id,
            document_type=row.document_type,
            payload=row.payload or {},
            updated_at=row.updated_at,
            updated_by_company_id=row.updated_by_company_id,
        )

    async def save_document(
        self, deal_id: int, document_type: str, payload: dict, company_id: int
    ) -> DocumentResponse:
        _, role = await get_order_and_company_role(self.session, deal_id, company_id)
        if not role:
            raise HTTPException(status_code=404, detail="Deal not found or access denied")
        if document_type not in ("order", "bill", "supply_contract", "act", "invoice", "contract", "others"):
            raise HTTPException(status_code=400, detail=f"Invalid document_type: {document_type}")
        row = await self.repo.save(deal_id, document_type, payload, updated_by_company_id=company_id)
        return DocumentResponse(
            deal_id=row.deal_id,
            document_type=row.document_type,
            payload=row.payload or {},
            updated_at=row.updated_at,
            updated_by_company_id=row.updated_by_company_id,
        )
