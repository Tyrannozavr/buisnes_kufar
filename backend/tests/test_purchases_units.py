"""
Тесты API единиц измерения (ОКЕИ).
Эндпоинт GET /api/v1/purchases/units не требует аутентификации.
"""
import pytest
from httpx import AsyncClient

from app.main import app
from httpx import ASGITransport


@pytest.fixture
async def client():
    """Async HTTP client для тестов."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_units_of_measurement_returns_200_and_list(client: AsyncClient):
    """GET /api/v1/purchases/units возвращает 200 и список объектов с полями id, name, symbol, code."""
    response = await client.get("/api/v1/purchases/units")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    for unit in data:
        assert "id" in unit
        assert "name" in unit
        assert "symbol" in unit
        assert "code" in unit


@pytest.mark.asyncio
async def test_get_units_okei_codes_when_seeded(client: AsyncClient):
    """Если в БД загружены единицы из ТЗ, код для 'шт' равен 796 (ОКЕИ)."""
    response = await client.get("/api/v1/purchases/units")
    assert response.status_code == 200
    data = response.json()
    if data:
        first = data[0]
        assert isinstance(first["id"], int)
        assert isinstance(first["name"], str)
        assert isinstance(first["symbol"], str)
        assert isinstance(first["code"], str)
        by_symbol = {u["symbol"]: u["code"] for u in data}
        if "шт" in by_symbol:
            assert by_symbol["шт"] == "796"
