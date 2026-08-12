"""
Общие фикстуры для тестов backend.
Engine пересоздаётся на loop сессии — иначе asyncpg «attached to a different loop».
"""
import sys

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app


@pytest.fixture(scope="function", autouse=True)
async def ensure_tables():
	"""Пересоздать async engine на текущем loop и создать таблицы."""
	from app.core.config import settings
	from app.db import base as db_base

	await db_base.engine.dispose()
	db_base.engine = create_async_engine(
		settings.ASYNC_DATABASE_URL,
		echo=False,
		future=True,
		pool_size=5,
		max_overflow=10,
		pool_pre_ping=True,
	)
	db_base.AsyncSessionLocal = sessionmaker(
		db_base.engine, class_=AsyncSession, expire_on_commit=False
	)
	# Обновить все модули, которые импортировали AsyncSessionLocal по имени
	for module in sys.modules.values():
		if module is None or module is db_base:
			continue
		if getattr(module, "AsyncSessionLocal", None) is not None:
			try:
				setattr(module, "AsyncSessionLocal", db_base.AsyncSessionLocal)
			except Exception:
				pass
	async with db_base.engine.begin() as conn:
		await conn.run_sync(db_base.Base.metadata.create_all)


@pytest.fixture
async def async_client():
	"""Асинхронный HTTP-клиент для тестов API (без аутентификации)."""
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://testserver") as client:
		yield client
