"""Background side-effects for purchases (checkout chat notify)."""
from __future__ import annotations

from typing import Iterable, Sequence

from app.api.purchases.models import OrderType
from app_logging.logger import logger


async def run_checkout_seller_notify(
    *,
    buyer_company_id: int,
    buyer_user_id: int,
    seller_company_id: int,
    deal_id: int,
    seller_order_number: str,
    order_type: str | OrderType,
    product_names: Sequence[str] | Iterable[str],
) -> None:
    """Создать чат + сообщение продавцу в отдельной сессии (после ответа checkout)."""
    from app.api.purchases.services.checkout_chat_notify import (
        notify_seller_about_checkout_order,
    )
    from app.db.base import AsyncSessionLocal

    if isinstance(order_type, OrderType):
        order_type_enum = order_type
    else:
        order_type_enum = OrderType(order_type)

    names = [str(n).strip() for n in product_names if str(n).strip()]
    async with AsyncSessionLocal() as session:
        try:
            await notify_seller_about_checkout_order(
                session,
                buyer_company_id=buyer_company_id,
                buyer_user_id=buyer_user_id,
                seller_company_id=seller_company_id,
                deal_id=deal_id,
                seller_order_number=seller_order_number,
                order_type=order_type_enum,
                product_names=names,
            )
            if session.is_active:
                await session.commit()
        except Exception:
            logger.exception(
                "Checkout seller notify failed deal=%s seller=%s",
                deal_id,
                seller_company_id,
            )
            if session.is_active:
                await session.rollback()
