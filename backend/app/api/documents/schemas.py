"""
Схемы API документов. Для фронта: payload — произвольный JSON формы (заказ, счёт и т.д.).
counterparty_updated_at / updated_by_company_id — для диалога «Контрагент изменил данные. Обновить?».
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# Допустимые типы документов (вкладки редактора). Сергей может расширить.
DOCUMENT_TYPES = ("order", "bill", "supply_contract", "act", "invoice", "contract", "others")


class DocumentPayloadUpdate(BaseModel):
    """Тело PUT: сохранить payload формы."""
    payload: dict = Field(..., description="Данные формы (JSON). Структура зависит от document_type.")


class DocumentResponse(BaseModel):
    """Ответ GET: документ по сделке и типу."""
    model_config = {"from_attributes": True}

    deal_id: int
    document_type: str
    payload: dict = Field(default_factory=dict)
    updated_at: datetime
    updated_by_company_id: Optional[int] = None
