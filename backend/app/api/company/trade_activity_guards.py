"""Запрет разделов ЛК для компаний Перевозчик / Экспедитор (ТЗ_15 §5.3)."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select

from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.company.models.company import Company, TradeActivity
from app.db.dependencies import async_db_dep


LOGISTICS_FORBIDDEN_DETAIL = (
    "Раздел недоступен для компании с торговой деятельностью "
    "«Перевозчик» или «Экспедитор»"
)


def _as_trade_activity(raw) -> TradeActivity | None:
    if raw is None:
        return None
    if isinstance(raw, TradeActivity):
        return raw
    if isinstance(raw, str):
        try:
            return TradeActivity(raw)
        except ValueError:
            try:
                return TradeActivity[raw]
            except KeyError:
                return None
    return None


async def require_not_logistics_company(
    current_user: Annotated[User, Depends(get_current_user)],
    db: async_db_dep,
) -> User:
    """403 если trade_activity компании — Перевозчик или Экспедитор."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    result = await db.execute(
        select(Company.trade_activity).where(Company.id == current_user.company_id)
    )
    activity = _as_trade_activity(result.scalar_one_or_none())
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    if activity.is_logistics_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=LOGISTICS_FORBIDDEN_DETAIL,
        )
    return current_user
