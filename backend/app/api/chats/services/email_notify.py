"""Email-дублирование новых сообщений чата."""
from __future__ import annotations

import html
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.authentication.models.user import User
from app.api.chats.models.chat import Chat
from app.api.chats.models.chat_participant import ChatParticipant
from app.api.company.models.company import Company
from app.core.config import settings
from app.core.email_utils import send_new_message_notification_email
from app.core.security import create_email_unsubscribe_token
from app_logging.logger import logger


def _build_preview(content: Optional[str], file_name: Optional[str] = None) -> str:
    text = (content or "").strip()
    if text:
        return html.escape(text)
    if file_name:
        return html.escape(f"Файл: {file_name}")
    return "Новое сообщение"


async def notify_recipients_about_new_message(
    db: AsyncSession,
    *,
    chat_id: int,
    sender_user_id: int,
    sender_company_id: int,
    content: Optional[str] = None,
    file_name: Optional[str] = None,
) -> None:
    """
    Отправить email участникам чата (кроме отправителя), у кого включены уведомления.
    Ошибки почты не пробрасываются — сообщение в чате уже сохранено.
    """
    try:
        result = await db.execute(
            select(Chat)
            .options(selectinload(Chat.participants).selectinload(ChatParticipant.user))
            .where(Chat.id == chat_id)
        )
        chat = result.scalar_one_or_none()
        if not chat:
            return

        company_result = await db.execute(
            select(Company).where(Company.id == sender_company_id)
        )
        sender_company = company_result.scalar_one_or_none()
        sender_name = (sender_company.name if sender_company else None) or "контрагент"

        preview = _build_preview(content, file_name)
        base_url = settings.FRONTEND_URL.rstrip("/")
        chat_url = f"{base_url}/profile/messages/{chat_id}"

        for participant in chat.participants:
            if participant.user_id == sender_user_id:
                continue
            user = participant.user
            if user is None or not user.email:
                continue
            if not getattr(user, "email_notifications_enabled", False):
                continue

            token = create_email_unsubscribe_token(user.id)
            unsubscribe_url = f"{base_url}/unsubscribe-email?token={token}"

            await send_new_message_notification_email(
                user.email,
                sender_name=sender_name,
                message_preview=preview,
                chat_url=chat_url,
                unsubscribe_url=unsubscribe_url,
            )
    except Exception as exc:
        logger.exception(
            "Не удалось отправить email-уведомления о сообщении в чате %s: %s",
            chat_id,
            exc,
        )
