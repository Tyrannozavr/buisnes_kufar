"""Уведомление продавца в чате при создании заказа из checkout (§2.2)."""
from __future__ import annotations

from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.chats.schemas.chat import ChatCreate
from app.api.chats.services.chat_service import ChatService
from app.api.purchases.models import OrderType
from app.core.config import settings
from app_logging.logger import logger


async def notify_seller_about_checkout_order(
    session: AsyncSession,
    *,
    buyer_company_id: int,
    buyer_user_id: int,
    seller_company_id: int,
    deal_id: int,
    seller_order_number: str,
    order_type: OrderType,
    product_names: Iterable[str],
) -> None:
    """Создать/найти чат между компаниями и отправить сообщение продавцу."""
    try:
        chat_service = ChatService(session)
        chat = await chat_service.create_chat(
            buyer_user_id,
            buyer_company_id,
            ChatCreate(participant_company_id=seller_company_id),
        )

        kind_label = "услуги" if order_type == OrderType.SERVICES else "товары"
        product_list = ", ".join(name for name in product_names if name)
        base_url = settings.FRONTEND_URL.rstrip("/")
        review_url = f"{base_url}/profile/editor?dealId={deal_id}&role=seller#order"
        content = (
            f"Поступил новый заказ № {seller_order_number} ({kind_label}): {product_list}. "
            f"[Просмотр заказа]({review_url})"
        )

        await chat_service.send_message(
            chat_id=chat.id,
            sender_company_id=buyer_company_id,
            sender_user_id=buyer_user_id,
            content=content,
        )
    except Exception as exc:
        logger.exception(
            "Не удалось отправить уведомление в чат по заказу %s: %s",
            deal_id,
            exc,
        )
