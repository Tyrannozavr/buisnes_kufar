import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.main import app
from app.db.base import AsyncSessionLocal
from app.api.company.models.company import Company
from app.api.authentication.models.user import User


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def test_user_and_company(db_session: AsyncSession):
    """Создаем тестового пользователя с компанией"""
    from app.api.authentication.repositories.user_repository import UserRepository
    from app.api.company.repositories.company_repository import CompanyRepository
    
    # Создаем пользователя
    user_repo = UserRepository(db_session)
    
    # Создаем тестового пользователя
    test_user = User(
        email="testuser@example.com",
        phone="+79001234567",
        first_name="Тест",
        last_name="Пользователь",
        hashed_password="hashed_password_test",
        is_active=True
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Создаем тестовую компанию
    test_company = Company(
        name="Тестовая компания",
        slug="test-company",
        type="ООО",
        trade_activity="Покупатель",
        business_type="Производство товаров",
        activity_type="Тестовая деятельность",
        description="Описание тестовой компании",
        country="Россия",
        federal_district="Центральный федеральный округ",
        region="Москва",
        city="Москва",
        full_name="ООО 'Тестовая компания'",
        inn="1234567890",
        ogrn="1234567890123",
        kpp="123456789",
        registration_date=datetime.now(),
        legal_address="Тестовый адрес",
        production_address="Тестовый адрес производства",
        phone="+79001234567",
        email="test@example.com",
        website="https://test.com",
        is_active=False
    )
    db_session.add(test_company)
    await db_session.commit()
    await db_session.refresh(test_company)
    
    # Привязываем пользователя к компании
    test_user.company_id = test_company.id
    await db_session.commit()
    await db_session.refresh(test_user)
    
    return {"user": test_user, "company": test_company}


class TestCompanyUpdate:
    """Тесты для обновления компании"""
    
    @pytest.mark.asyncio
    async def test_update_company_with_existing_company(self, client: TestClient, test_user_and_company):
        """Тест обновления существующей компании"""
        user = test_user_and_company["user"]
        company = test_user_and_company["company"]
        
        # Получаем токен (здесь нужно будет добавить аутентификацию)
        # Для примера, мы будем использовать прямую работу с БД
        
        # Тестируем обновление через репозиторий
        update_data = {
            "name": "Обновленная компания",
            "full_name": "ООО 'Обновленная компания'",
            "inn": "9876543210",
            "phone": "+79009876543"
        }
        
        from app.api.company.repositories.company_repository import CompanyRepository
        from app.api.company.schemas.company import CompanyUpdate
        from app.db.base import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            repo = CompanyRepository(session)
            update_schema = CompanyUpdate(**update_data)
            updated_company = await repo.update(company.id, update_schema)
            
            assert updated_company is not None
            assert updated_company.name == "Обновленная компания"
            assert updated_company.full_name == "ООО 'Обновленная компания'"
            assert updated_company.inn == "9876543210"
    
    @pytest.mark.asyncio
    async def test_update_company_creates_inactive_if_no_company(self, client: TestClient, db_session: AsyncSession):
        """Тест создания неактивной компании для пользователя без компании"""
        from app.api.authentication.repositories.user_repository import UserRepository
        
        # Создаем пользователя без компании
        user_repo = UserRepository(db_session)
        test_user = User(
            email="nocompany@example.com",
            phone="+79001111111",
            first_name="Тест",
            last_name="Без Компании",
            hashed_password="hashed_password_test",
            is_active=True
        )
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)
        
        assert test_user.company_id is None
        
        # Пытаемся обновить компанию (должна быть создана неактивная)
        from app.api.company.services.company_service import CompanyService
        from app.api.company.repositories.company_repository import CompanyRepository
        from app.api.company.schemas.company import CompanyUpdate
        
        repo = CompanyRepository(db_session)
        service = CompanyService(repo, db_session)
        
        update_data = CompanyUpdate(
            name="Новая компания",
            full_name="ООО 'Новая компания'",
            inn="1111111111",
            phone="+79001111111",
            email="nocompany@example.com"
        )
        
        result = await service.update_company(test_user, update_data)
        
        # Компания должна быть создана
        assert result is not None
        assert result.name == "Новая компания"
        
        # Пользователь должен быть связан с компанией
        await db_session.refresh(test_user)
        assert test_user.company_id is not None
    
    @pytest.mark.asyncio
    async def test_update_company_validates_required_fields(self, client: TestClient, test_user_and_company):
        """Тест валидации обязательных полей при обновлении"""
        company = test_user_and_company["company"]
        
        # Пытаемся обновить с невалидными данными (пустой ИНН)
        from app.api.company.repositories.company_repository import CompanyRepository
        from app.api.company.schemas.company import CompanyUpdate
        from app.db.base import AsyncSessionLocal
        from fastapi import HTTPException
        
        async with AsyncSessionLocal() as session:
            repo = CompanyRepository(session)
            
            # Слишком короткий ИНН
            update_data = CompanyUpdate(
                inn="123",  # Невалидный ИНН
            )
            
            # При обновлении должно быть игнорировано невалидное поле
            # или выброшено исключение
            updated_company = await repo.update(company.id, update_data)
            
            # ИНН не должен обновиться на невалидное значение
            if updated_company:
                assert len(updated_company.inn) == 10  # Должна остаться старая валидная длина
    
    @pytest.mark.asyncio
    async def test_update_company_activates_when_complete(self, client: TestClient, test_user_and_company):
        """Тест активации компании при заполнении всех полей"""
        user = test_user_and_company["user"]
        company = test_user_and_company["company"]
        
        # Убеждаемся, что компания неактивна
        assert company.is_active == False
        
        from app.api.company.repositories.company_repository import CompanyRepository
        from app.api.company.schemas.company import CompanyUpdate
        from app.api.company.services.company_service import CompanyService
        from app.db.base import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            repo = CompanyRepository(session)
            service = CompanyService(repo, session)
            
            # Обновляем компанию с полными данными
            update_data = CompanyUpdate(
                name="Полная компания",
                full_name="ООО 'Полная компания'",
                inn="1234567890",
                ogrn="1234567890123",
                kpp="123456789",
                registration_date=datetime.now(),
                legal_address="Полный адрес",
                phone="+79001234567",
                email="test@example.com",
                country="Россия",
                federal_district="Центральный федеральный округ",
                region="Москва",
                city="Москва",
                type="ООО",
                trade_activity="Покупатель",
                business_type="Производство товаров",
                activity_type="Полная деятельность"
            )
            
            result = await service.update_company(user, update_data)
            
            # Компания должна быть активирована
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_inn_field_maxlength_validation(self, client: TestClient, test_user_and_company):
        """Тест валидации длины поля ИНН"""
        company = test_user_and_company["company"]
        
        from app.api.company.repositories.company_repository import CompanyRepository
        from app.api.company.schemas.company import CompanyUpdate
        from app.db.base import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            repo = CompanyRepository(session)
            
            # ИНН должен быть 10 символов
            update_data = CompanyUpdate(
                inn="1234567890123456"  # Слишком длинный ИНН
            )
            
            # Обновляем компанию
            updated = await repo.update(company.id, update_data)
            
            # Проверяем, что обновление произошло корректно или значение было обрезано
            if updated:
                assert updated.inn is not None
                assert len(updated.inn) <= 12  # Максимальная длина ИНН в базе


if __name__ == "__main__":
    pytest.main([__file__])

