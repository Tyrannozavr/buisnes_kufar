"""Celery tasks for chat email notifications (off the request path)."""
from __future__ import annotations

import asyncio
from typing import Optional

from app.celery_app import celery_app
from app_logging.logger import logger


def enqueue_message_email_notify(
    *,
    chat_id: int,
    sender_user_id: int,
    sender_company_id: int,
    content: Optional[str] = None,
    file_name: Optional[str] = None,
) -> None:
    """Fire-and-forget; never block the request on SMTP."""
    try:
        notify_message_email.delay(
            chat_id,
            sender_user_id,
            sender_company_id,
            content,
            file_name,
        )
        return
    except Exception as exc:
        logger.warning("Celery enqueue failed, scheduling inline notify: %s", exc)

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(
            _notify_async(chat_id, sender_user_id, sender_company_id, content, file_name)
        )
    except RuntimeError:
        asyncio.run(
            _notify_async(chat_id, sender_user_id, sender_company_id, content, file_name)
        )


@celery_app.task(name="chats.notify_message_email")
def notify_message_email(
    chat_id: int,
    sender_user_id: int,
    sender_company_id: int,
    content: Optional[str] = None,
    file_name: Optional[str] = None,
) -> None:
    asyncio.run(
        _notify_async(chat_id, sender_user_id, sender_company_id, content, file_name)
    )


async def _notify_async(
    chat_id: int,
    sender_user_id: int,
    sender_company_id: int,
    content: Optional[str],
    file_name: Optional[str],
) -> None:
    from app.api.chats.services.email_notify import notify_recipients_about_new_message
    from app.db.base import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await notify_recipients_about_new_message(
            session,
            chat_id=chat_id,
            sender_user_id=sender_user_id,
            sender_company_id=sender_company_id,
            content=content,
            file_name=file_name,
        )
