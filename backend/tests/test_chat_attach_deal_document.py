"""Фоновая копия скана сделки во вложение чата."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.chats.tasks import enqueue_attach_deal_document


@pytest.mark.asyncio
async def test_enqueue_attach_on_running_loop_uses_create_task():
	with patch("app.api.chats.tasks.attach_deal_document_to_message") as task:
		task.delay = MagicMock()
		with patch("asyncio.get_running_loop") as get_loop:
			loop = MagicMock()
			loop.is_running.return_value = True

			def _create_task(coro):
				coro.close()
				return MagicMock()

			loop.create_task = MagicMock(side_effect=_create_task)
			get_loop.return_value = loop
			enqueue_attach_deal_document(
				message_id=10,
				deal_id=1,
				document_id=2,
				company_id=3,
			)
			loop.create_task.assert_called_once()
			task.delay.assert_not_called()


def test_enqueue_attach_without_loop_uses_celery():
	with patch("app.api.chats.tasks.attach_deal_document_to_message") as task:
		task.delay = MagicMock()
		with patch("asyncio.get_running_loop", side_effect=RuntimeError):
			enqueue_attach_deal_document(
				message_id=10,
				deal_id=1,
				document_id=2,
				company_id=3,
			)
		task.delay.assert_called_once_with(10, 1, 2, 3, None)


@pytest.mark.asyncio
async def test_attach_skips_when_message_missing():
	from app.api.chats.tasks import _attach_deal_document_async

	session = AsyncMock()
	session.get = AsyncMock(return_value=None)
	session.__aenter__ = AsyncMock(return_value=session)
	session.__aexit__ = AsyncMock(return_value=None)

	with patch("app.db.base.AsyncSessionLocal", return_value=session):
		await _attach_deal_document_async(99, 1, 2, 3)

	session.commit.assert_not_called()
