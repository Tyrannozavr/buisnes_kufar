"""Тесты email-уведомлений о новых сообщениях и отписки."""
from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4
import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.main import app
from app.db.base import AsyncSessionLocal
from app.api.authentication.models.roles_positions import UserRole
from app.api.authentication.models.user import User
from app.api.chats.models.chat import Chat
from app.api.chats.models.chat_participant import ChatParticipant
from app.api.chats.services.chat_service import ChatService
from app.api.chats.services.email_notify import notify_recipients_about_new_message
from app.api.company.models.company import Company, TradeActivity, BusinessType
from app.api.messages.models.message import Message
from app.core.security import create_email_unsubscribe_token, verify_email_unsubscribe_token


def _company(**kwargs) -> Company:
    unique = uuid4().hex[:8]
    seed = int(unique[:6], 16) % 10**9
    data = {
        "name": f"Email Co {unique}",
        "slug": f"email-co-{unique}",
        "type": "ООО",
        "trade_activity": TradeActivity.SELLER,
        "business_type": BusinessType.GOODS,
        "activity_type": "Тест",
        "description": "Тест",
        "country": "Россия",
        "federal_district": "ЦФО",
        "region": "Москва",
        "city": "Москва",
        "full_name": f"ООО Email {unique}",
        "inn": f"{seed:010d}",
        "ogrn": f"{seed:013d}",
        "kpp": f"{(seed % 10**9):09d}",
        "registration_date": datetime.utcnow(),
        "legal_address": "ул. Тест, 1",
        "production_address": "ул. Тест, 2",
        "phone": "+79000000000",
        "email": f"co-{unique}@example.com",
        "website": "https://example.com",
        "is_active": True,
    }
    data.update(kwargs)
    return Company(**data)


@pytest.fixture
async def email_notify_context():
    unique = uuid4().hex[:8]
    async with AsyncSessionLocal() as session:
        sender_company = _company(name="Sender Co", slug=f"sender-{unique}")
        recipient_company = _company(name="Recipient Co", slug=f"recipient-{unique}")
        session.add_all([sender_company, recipient_company])
        await session.flush()

        sender = User(
            email=f"sender-{unique}@example.com",
            phone="+79001112233",
            first_name="Sender",
            last_name="User",
            hashed_password="test",
            is_active=True,
            company_id=sender_company.id,
            role=UserRole.OWNER,
            email_notifications_enabled=False,
        )
        recipient = User(
            email=f"recipient-{unique}@example.com",
            phone="+79001112234",
            first_name="Recipient",
            last_name="User",
            hashed_password="test",
            is_active=True,
            company_id=recipient_company.id,
            role=UserRole.OWNER,
            email_notifications_enabled=True,  # явно включаем для позитивных кейсов
        )
        session.add_all([sender, recipient])
        await session.flush()

        chat = Chat(title="Test chat")
        session.add(chat)
        await session.flush()

        session.add_all(
            [
                ChatParticipant(
                    chat_id=chat.id,
                    company_id=sender_company.id,
                    user_id=sender.id,
                ),
                ChatParticipant(
                    chat_id=chat.id,
                    company_id=recipient_company.id,
                    user_id=recipient.id,
                ),
            ]
        )
        await session.commit()

        context = {
            "chat_id": chat.id,
            "sender_user_id": sender.id,
            "sender_company_id": sender_company.id,
            "recipient_user_id": recipient.id,
            "recipient_company_id": recipient_company.id,
            "recipient_email": recipient.email,
            "sender_company_name": sender_company.name,
        }

    yield context

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(Message).where(Message.chat_id == context["chat_id"])
        )
        await session.execute(
            delete(ChatParticipant).where(ChatParticipant.chat_id == context["chat_id"])
        )
        await session.execute(delete(Chat).where(Chat.id == context["chat_id"]))
        await session.execute(
            delete(User).where(
                User.id.in_(
                    [context["sender_user_id"], context["recipient_user_id"]]
                )
            )
        )
        await session.execute(
            delete(Company).where(
                Company.id.in_(
                    [
                        context["sender_company_id"],
                        context["recipient_company_id"],
                    ]
                )
            )
        )
        await session.commit()


@pytest.mark.asyncio
async def test_unsubscribe_token_roundtrip():
    token = create_email_unsubscribe_token(42)
    assert verify_email_unsubscribe_token(token) == 42
    assert verify_email_unsubscribe_token("bad-token") is None


@pytest.mark.asyncio
async def test_notify_sends_email_when_enabled(email_notify_context):
    ctx = email_notify_context
    with patch(
        "app.api.chats.services.email_notify.send_new_message_notification_email",
        new_callable=AsyncMock,
        return_value=True,
    ) as mock_send:
        async with AsyncSessionLocal() as session:
            await notify_recipients_about_new_message(
                session,
                chat_id=ctx["chat_id"],
                sender_user_id=ctx["sender_user_id"],
                sender_company_id=ctx["sender_company_id"],
                content="Привет из теста",
            )

        mock_send.assert_awaited_once()
        args, kwargs = mock_send.await_args
        assert args[0] == ctx["recipient_email"]
        assert kwargs["sender_name"] == ctx["sender_company_name"]
        assert "Привет из теста" in kwargs["message_preview"]
        assert "/unsubscribe-email?token=" in kwargs["unsubscribe_url"]
        assert f"/profile/messages/{ctx['chat_id']}" in kwargs["chat_url"]


@pytest.mark.asyncio
async def test_notify_skips_when_disabled(email_notify_context):
    ctx = email_notify_context
    async with AsyncSessionLocal() as session:
        user = await session.get(User, ctx["recipient_user_id"])
        user.email_notifications_enabled = False
        await session.commit()

    with patch(
        "app.api.chats.services.email_notify.send_new_message_notification_email",
        new_callable=AsyncMock,
        return_value=True,
    ) as mock_send:
        async with AsyncSessionLocal() as session:
            await notify_recipients_about_new_message(
                session,
                chat_id=ctx["chat_id"],
                sender_user_id=ctx["sender_user_id"],
                sender_company_id=ctx["sender_company_id"],
                content="Не должно уйти",
            )
        mock_send.assert_not_awaited()


@pytest.mark.asyncio
async def test_chat_service_send_message_triggers_email(email_notify_context):
    ctx = email_notify_context

    def _run_notify(**kwargs):
        async def _inner():
            from app.api.chats.services.email_notify import notify_recipients_about_new_message
            async with AsyncSessionLocal() as session:
                await notify_recipients_about_new_message(session, **kwargs)

        asyncio.run(_inner())

    with patch(
        "app.api.chats.services.email_notify.send_new_message_notification_email",
        new_callable=AsyncMock,
        return_value=True,
    ) as mock_send, patch(
        "app.api.chats.tasks.enqueue_message_email_notify",
        side_effect=lambda **kw: _run_notify(**kw),
    ):
        async with AsyncSessionLocal() as session:
            service = ChatService(session)
            await service.send_message(
                chat_id=ctx["chat_id"],
                sender_company_id=ctx["sender_company_id"],
                sender_user_id=ctx["sender_user_id"],
                content="Сообщение через сервис",
            )
        mock_send.assert_awaited_once()


@pytest.mark.asyncio
async def test_unsubscribe_endpoint(email_notify_context):
    ctx = email_notify_context
    token = create_email_unsubscribe_token(ctx["recipient_user_id"])

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/api/v1/auth/email-notifications/unsubscribe",
            params={"token": token},
        )

    assert response.status_code == 200
    assert response.json()["email_notifications_enabled"] is False

    async with AsyncSessionLocal() as session:
        user = await session.get(User, ctx["recipient_user_id"])
        assert user.email_notifications_enabled is False
