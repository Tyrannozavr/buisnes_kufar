"""
API документов редактора: GET/PUT по deal_id и document_type.
Фронт: при открытии вкладки — GET; «Сохранить документ» — PUT.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.documents.schemas import DocumentPayloadUpdate, DocumentResponse
from app.api.documents.service import DocumentFormService
from app.api.purchases.dependencies import deal_service_dep_annotated
from app.api.purchases.services import DealService
from app.db.dependencies import async_db_dep
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["documents", "editor"])


async def _company_id_dep(
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: deal_service_dep_annotated,
) -> int:
    """ID компании текущего пользователя (для проверки доступа к сделке)."""
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company.id


@router.get("/{deal_id}/documents/{document_type}", response_model=DocumentResponse)
async def get_document(
    deal_id: int,
    document_type: str,
    current_user: Annotated[User, Depends(get_current_user)],
    company_id: Annotated[int, Depends(_company_id_dep)],
    session: async_db_dep,
):
    """
    Получить payload формы документа по сделке и типу.
    Фронт: при открытии редактора по ссылке из Продаж/Закупок — GET с deal_id и document_type (order, bill, …).
    Если документа нет — вернётся payload={}, updated_at=now. Для диалога «Контрагент изменил?» используйте
    updated_by_company_id: если != company_id текущего юзера и updated_at > lastSeen — показать «Обновить данные?».
    """
    service = DocumentFormService(session)
    return await service.get_document(deal_id, document_type, company_id)


@router.put("/{deal_id}/documents/{document_type}", response_model=DocumentResponse)
async def save_document(
    deal_id: int,
    document_type: str,
    body: DocumentPayloadUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    company_id: Annotated[int, Depends(_company_id_dep)],
    session: async_db_dep,
):
    """
    Сохранить payload формы документа. Фронт: кнопка «Сохранить документ» — PUT с payload из формы.
    updated_by_company_id будет установлен в company_id текущего юзера (для диалога у контрагента).
    """
    service = DocumentFormService(session)
    return await service.save_document(deal_id, document_type, body.payload, company_id)
