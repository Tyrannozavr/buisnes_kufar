"""
Общие фикстуры для тестов backend.
Один event loop на всю сессию — иначе async engine/пул приложения привязан к другому loop и тесты падают с "attached to a different loop".
Таблицы создаём до тестов через create_db_and_tables, т.к. в тестовом окружении lifespan приложения может не успеть выполниться до первого запроса.
"""
import asyncio
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Один loop на все async-тесты, чтобы app и engine не переключались между loop."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def ensure_tables(event_loop):
    """Создать таблицы в тестовой БД до запуска тестов (engine из app.db.base, URL из env)."""
    from app.db.base import create_db_and_tables
    event_loop.run_until_complete(create_db_and_tables())


@pytest.fixture
async def async_client():
    """Асинхронный HTTP-клиент для тестов API (без аутентификации)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
