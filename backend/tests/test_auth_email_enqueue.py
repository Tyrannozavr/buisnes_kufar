"""Auth emails уходят в фон (create_task / Celery), не блокируют request."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.authentication.tasks.email import enqueue_auth_email, _send_auth_email_async


@pytest.mark.asyncio
async def test_enqueue_auth_email_on_running_loop_uses_create_task():
	with patch("app.api.authentication.tasks.email.send_auth_email") as task:
		task.delay = MagicMock()
		with patch("asyncio.get_running_loop") as get_loop:
			loop = MagicMock()
			loop.is_running.return_value = True

			def _create_task(coro):
				coro.close()
				return MagicMock()

			loop.create_task = MagicMock(side_effect=_create_task)
			get_loop.return_value = loop
			enqueue_auth_email(
				"verification",
				"user@example.com",
				url="https://example.com/verify",
			)
			loop.create_task.assert_called_once()
			task.delay.assert_not_called()


def test_enqueue_auth_email_without_loop_uses_celery():
	with patch("app.api.authentication.tasks.email.send_auth_email") as task:
		task.delay = MagicMock()
		with patch("asyncio.get_running_loop", side_effect=RuntimeError):
			enqueue_auth_email(
				"password_reset",
				"user@example.com",
				url="https://example.com/reset",
			)
		task.delay.assert_called_once_with(
			"password_reset",
			"user@example.com",
			"https://example.com/reset",
			None,
		)


@pytest.mark.asyncio
async def test_send_auth_email_async_verification():
	with patch(
		"app.core.email_utils.send_verification_email",
		new_callable=AsyncMock,
		return_value=True,
	) as send:
		await _send_auth_email_async(
			"verification",
			"a@b.c",
			url="https://example.com/v",
		)
		send.assert_awaited_once_with("a@b.c", "https://example.com/v")


@pytest.mark.asyncio
async def test_send_auth_email_async_returns_false_on_smtp_fail():
	with patch(
		"app.core.email_utils.send_password_recovery_code",
		new_callable=AsyncMock,
		return_value=False,
	):
		ok = await _send_auth_email_async(
			"password_recovery",
			"a@b.c",
			code="123456",
		)
		assert ok is False
