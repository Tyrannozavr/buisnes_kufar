"""Celery tasks for chat (email notify + background deal-doc attach)."""
from __future__ import annotations

import asyncio
import mimetypes
import os
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
    """Fire-and-forget; never block the request on SMTP/broker.

    На request-path сначала create_task: иначе kombu.delay при недоступном
    брокере ждёт ~6с Connection refused и тормозит POST /chats/.../send.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(
            _notify_async(chat_id, sender_user_id, sender_company_id, content, file_name)
        )
        return

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
        logger.warning("Celery enqueue failed, running inline notify: %s", exc)

    asyncio.run(
        _notify_async(chat_id, sender_user_id, sender_company_id, content, file_name)
    )


def enqueue_attach_deal_document(
    *,
    message_id: int,
    deal_id: int,
    document_id: int,
    company_id: int,
    original_filename: Optional[str] = None,
) -> None:
    """Copy deal document into chat_files without blocking the send response.

    На request-path предпочитаем asyncio.create_task (ответ уже ушёл, воркер
    Celery в dev часто не запущен). Celery — fallback из sync-контекста.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(
            _attach_deal_document_async(
                message_id, deal_id, document_id, company_id, original_filename
            )
        )
        return

    try:
        attach_deal_document_to_message.delay(
            message_id,
            deal_id,
            document_id,
            company_id,
            original_filename,
        )
        return
    except Exception as exc:
        logger.warning(
            "Celery enqueue attach failed, running sync: message=%s err=%s",
            message_id,
            exc,
        )

    asyncio.run(
        _attach_deal_document_async(
            message_id, deal_id, document_id, company_id, original_filename
        )
    )


def _run_coro_sync(coro):
    """Run async notify from a sync Celery worker without nested-loop crashes."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # Should not happen in a normal Celery prefork worker; best-effort.
        return asyncio.ensure_future(coro, loop=loop)
    return asyncio.run(coro)


@celery_app.task(name="chats.notify_message_email")
def notify_message_email(
    chat_id: int,
    sender_user_id: int,
    sender_company_id: int,
    content: Optional[str] = None,
    file_name: Optional[str] = None,
) -> None:
    _run_coro_sync(
        _notify_async(chat_id, sender_user_id, sender_company_id, content, file_name)
    )


@celery_app.task(name="chats.attach_deal_document_to_message")
def attach_deal_document_to_message(
    message_id: int,
    deal_id: int,
    document_id: int,
    company_id: int,
    original_filename: Optional[str] = None,
) -> None:
    _run_coro_sync(
        _attach_deal_document_async(
            message_id, deal_id, document_id, company_id, original_filename
        )
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


async def _attach_deal_document_async(
    message_id: int,
    deal_id: int,
    document_id: int,
    company_id: int,
    original_filename: Optional[str] = None,
) -> None:
    """Download deal doc from S3 → uploads/chat_files, patch message, WS update."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.api.chats.models.chat import Chat
    from app.api.chats.websocket_manager import chat_manager
    from app.api.messages.models.message import Message
    from app.api.purchases.repositories import DealRepository
    from app.core.config import settings
    from app.core.s3 import get_document_content
    from app.core.uploads import CHAT_EXTENSIONS, sanitize_original_name, unique_filename
    from app.db.base import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        message = await session.get(Message, message_id)
        if not message:
            logger.warning("attach: message %s not found", message_id)
            return
        if message.sender_company_id != company_id:
            logger.warning(
                "attach: company mismatch message=%s company=%s",
                message_id,
                company_id,
            )
            return
        if message.file_path:
            return

        repo = DealRepository(session)
        doc = await repo.get_document_by_id(deal_id, document_id, company_id)
        if not doc or not doc.document_file_path:
            logger.warning(
                "attach: document missing deal=%s doc=%s company=%s",
                deal_id,
                document_id,
                company_id,
            )
            return

        stored_original = None
        if isinstance(doc.document_content, dict):
            stored_original = doc.document_content.get("original_filename")
        display_source = (
            (original_filename or "").strip()
            or (stored_original if isinstance(stored_original, str) else "").strip()
            or os.path.basename(doc.document_file_path)
            or "scan.bin"
        )
        # Расширение берём из storage-ключа (гарантированно валидное), имя — пользовательское
        storage_basename = os.path.basename(doc.document_file_path) or display_source
        ext = os.path.splitext(storage_basename)[1] or os.path.splitext(display_source)[1]
        name_for_unique = f"{os.path.splitext(display_source)[0] or 'file'}{ext}"
        try:
            stored_name, _ = unique_filename(
                name_for_unique, allowed=CHAT_EXTENSIONS
            )
            display_name = sanitize_original_name(display_source)
        except Exception as exc:
            logger.warning(
                "attach: unsupported type for message=%s file=%s: %s",
                message_id,
                name_for_unique,
                exc,
            )
            return

        try:
            content, content_type = await asyncio.to_thread(
                get_document_content, doc.document_file_path
            )
        except Exception as exc:
            logger.exception(
                "attach: S3 download failed message=%s: %s", message_id, exc
            )
            return

        # Тот же лимит, что у прямых загрузок в чат (router._MAX_CHAT_FILE_BYTES).
        _MAX_CHAT_FILE_BYTES = 20 * 1024 * 1024
        if content is None or len(content) > _MAX_CHAT_FILE_BYTES:
            logger.warning(
                "attach: file too large or empty message=%s size=%s",
                message_id,
                0 if content is None else len(content),
            )
            return

        # Только чат с контрагентом по сделке (defense in depth к проверке в router).
        chat_result_pre = await session.execute(
            select(Chat)
            .options(selectinload(Chat.participants))
            .where(Chat.id == message.chat_id)
        )
        chat_pre = chat_result_pre.scalar_one_or_none()
        if chat_pre:
            order = await repo.get_order_by_id(deal_id, company_id)
            if not order:
                logger.warning(
                    "attach: no deal access message=%s deal=%s", message_id, deal_id
                )
                return
            deal_parties = {order.buyer_company_id, order.seller_company_id}
            others = {
                p.company_id
                for p in chat_pre.participants
                if p.company_id is not None and p.company_id != company_id
            }
            if not others or not others.issubset(deal_parties):
                logger.warning(
                    "attach: chat not deal counterpart message=%s deal=%s",
                    message_id,
                    deal_id,
                )
                return

        upload_dir = "uploads/chat_files"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, stored_name)
        if os.path.commonpath(
            [os.path.abspath(upload_dir), os.path.abspath(file_path)]
        ) != os.path.abspath(upload_dir):
            logger.error("attach: path escape blocked for message=%s", message_id)
            return

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        guessed, _ = mimetypes.guess_type(display_name)
        message.file_path = file_path
        message.file_name = display_name
        message.file_size = len(content)
        message.file_type = content_type or guessed or "application/octet-stream"
        await session.commit()
        await session.refresh(message)

        message_data = {
            "id": message.id,
            "chat_id": message.chat_id,
            "sender_company_id": message.sender_company_id,
            "sender_user_id": message.sender_user_id,
            "content": message.content,
            "file_path": settings.public_file_url(message.file_path),
            "file_name": message.file_name,
            "file_size": message.file_size,
            "file_type": message.file_type,
            "is_read": message.is_read,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
        }

        chat = chat_pre
        if chat is None:
            chat_result = await session.execute(
                select(Chat)
                .options(selectinload(Chat.participants))
                .where(Chat.id == message.chat_id)
            )
            chat = chat_result.scalar_one_or_none()
        participant_user_ids = (
            {p.user_id for p in chat.participants} if chat else None
        )

        try:
            await chat_manager.send_message_updated(
                message.chat_id,
                message_data,
                participant_user_ids=participant_user_ids,
            )
        except Exception as exc:
            logger.warning(
                "attach: WS update failed message=%s: %s", message_id, exc
            )
