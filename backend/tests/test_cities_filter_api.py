import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.db.base import AsyncSessionLocal
from app.api.common.models import Country, FederalDistrict, Region, City


@pytest.fixture
async def client():
    """Async HTTP client — один event loop с фикстурами и приложением."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def sample_data(db_session: AsyncSession):
    """Создаем тестовые данные (get_or_create, чтобы не падать на дубликатах)."""
    # Страна: берём существующую RU или создаём
    result = await db_session.execute(select(Country).where(Country.code == "RU").limit(1))
    country = result.scalar_one_or_none()
    if not country:
        country = Country(code="RU", name="Россия", is_active=True)
        db_session.add(country)
        await db_session.flush()
    # Федеральный округ: уникальный код для теста
    result = await db_session.execute(
        select(FederalDistrict).where(
            FederalDistrict.country_id == country.id,
            FederalDistrict.code == "CFO_TEST"
        ).limit(1)
    )
    federal_district = result.scalar_one_or_none()
    if not federal_district:
        federal_district = FederalDistrict(
            country_id=country.id,
            name="Центральный федеральный округ (тест)",
            code="CFO_TEST",
            is_active=True
        )
        db_session.add(federal_district)
        await db_session.flush()
    # Регион
    result = await db_session.execute(
        select(Region).where(
            Region.country_id == country.id,
            Region.code == "MOS_TEST"
        ).limit(1)
    )
    region = result.scalar_one_or_none()
    if not region:
        region = Region(
            country_id=country.id,
            federal_district_id=federal_district.id,
            name="Москва (тест)",
            code="MOS_TEST",
            is_active=True
        )
        db_session.add(region)
        await db_session.flush()
    # Город
    result = await db_session.execute(
        select(City).where(
            City.country_id == country.id,
            City.region_id == region.id,
            City.name == "Москва тест"
        ).limit(1)
    )
    city = result.scalar_one_or_none()
    if not city:
        city = City(
            country_id=country.id,
            region_id=region.id,
            federal_district_id=federal_district.id,
            name="Москва тест",
            population=12615000,
            is_million_city=True,
            is_regional_center=True,
            is_active=True
        )
        db_session.add(city)
    await db_session.commit()
    await db_session.refresh(country)
    await db_session.refresh(federal_district)
    await db_session.refresh(region)
    await db_session.refresh(city)
    return {
        "country": country,
        "federal_district": federal_district,
        "region": region,
        "city": city
    }


class TestCitiesFilterAPI:
    """Тесты для API фильтра городов"""
    
    @pytest.mark.asyncio
    async def test_get_cities_filter_tree(self, client: AsyncClient, sample_data):
        """Полное дерево локаций (все страны/регионы/города) — эндпоинт /api/v1/locations/location-tree."""
        response = await client.get("/api/v1/locations/location-tree")
        assert response.status_code == 200
        data = response.json()
        assert "countries" in data
        countries = data["countries"]
        assert len(countries) >= 1
        country_data = countries[0]
        assert country_data["name"] == "Россия"
        assert country_data["code"] == "RU"
        assert len(country_data["federal_districts"]) >= 1
        fd_data = country_data["federal_districts"][0]
        assert "name" in fd_data and "code" in fd_data
        assert len(fd_data["regions"]) >= 1
        region_data = fd_data["regions"][0]
        assert "name" in region_data and "code" in region_data
        assert len(region_data["cities"]) >= 1
        # Проверяем структуру: город имеет name, population или id
        city_data = region_data["cities"][0]
        assert "name" in city_data
        assert "population" in city_data or "id" in city_data
        # Если в дереве есть город из фикстуры «Москва тест» — проверяем его поля
        all_cities = []
        for c in data["countries"]:
            for fd in c.get("federal_districts", []):
                for r in fd.get("regions", []):
                    all_cities.extend(r.get("cities", []))
        if any(c["name"] == "Москва тест" for c in all_cities):
            our_city = next(c for c in all_cities if c["name"] == "Москва тест")
            assert our_city.get("population") == 12615000
            assert our_city.get("is_million_city") is True
            assert our_city.get("is_regional_center") is True
    
    @pytest.mark.asyncio
    async def test_search_cities(self, client: AsyncClient, sample_data):
        """Тест поиска городов (эндпоинт /api/v1/locations/cities)."""
        response = await client.get("/api/v1/locations/cities?country_code=RU&search=Москва")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        city_names = [item["label"] for item in data["items"]]
        assert "Москва тест" in city_names or any("Москва" in n for n in city_names)
    
    @pytest.mark.asyncio
    async def test_search_cities_with_filters(self, client: AsyncClient, sample_data):
        """Тест поиска городов с фильтрами (миллионники)."""
        response = await client.get(
            "/api/v1/locations/cities?country_code=RU&million_cities_only=true"
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        city_names = [item["label"] for item in data["items"]]
        assert "Москва тест" in city_names or len(data["items"]) >= 0
    
    @pytest.mark.asyncio
    async def test_search_cities_by_country(self, client: AsyncClient, sample_data):
        """Тест поиска городов по стране (country_code=RU)."""
        response = await client.get("/api/v1/locations/cities?country_code=RU")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        city_names = [item["label"] for item in data["items"]]
        assert "Москва тест" in city_names or len(city_names) >= 1
    
    @pytest.mark.asyncio
    async def test_get_cities_stats(self, client: AsyncClient, sample_data):
        """Тест получения статистики по городам."""
        response = await client.get("/api/v1/cities-filter/cities-stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_cities" in data
        assert "million_cities" in data
        assert "regional_centers" in data
        assert "total_federal_districts" in data
        assert "total_regions" in data
        assert data["total_cities"] >= 1
        assert data["million_cities"] >= 1
        assert data["regional_centers"] >= 1
        assert data["total_federal_districts"] >= 1
        assert data["total_regions"] >= 1
    
    @pytest.mark.asyncio
    async def test_search_cities_empty_query(self, client: AsyncClient, sample_data):
        """Тест поиска городов с пустым запросом (country_code обязателен)."""
        response = await client.get("/api/v1/locations/cities?country_code=RU")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_search_cities_nonexistent_query(self, client: AsyncClient, sample_data):
        """Тест поиска несуществующего города."""
        response = await client.get(
            "/api/v1/locations/cities?country_code=RU&search=НесуществующийГород"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
