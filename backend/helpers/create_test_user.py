"""
Скрипт для создания тестового пользователя и компании
"""
import asyncio
import asyncpg
from app.core.config import settings
from app.core.security import get_password_hash

async def create_test_user():
    """Создание тестового пользователя и компании"""
    # Получаем URL базы данных
    db_url = settings.SQLALCHEMY_DATABASE_URL
    if not db_url:
        db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
    
    try:
        # Подключаемся к базе данных
        conn = await asyncpg.connect(db_url)
        
        # Хешируем пароль
        password_hash = get_password_hash("testpassword123")
        
        # Создаем пользователя
        user_id = await conn.fetchval("""
            INSERT INTO users (email, hashed_password, first_name, last_name, phone, inn, position, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
            RETURNING id
        """, "buyer@test.com", password_hash, "Покупатель", "Тестовый", "+7-999-123-45-67", "9876543210", "Менеджер", True)
        
        print(f"Создан пользователь с ID: {user_id}")
        
        # Создаем компанию-покупателя
        buyer_company_id = await conn.fetchval("""
            INSERT INTO companies (name, slug, type, trade_activity, business_type, activity_type, country, federal_district, region, city, full_name, inn, ogrn, kpp, registration_date, legal_address, phone, email, total_views, monthly_views, total_purchases, user_id, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, NOW(), NOW())
            RETURNING id
        """, "ООО 'Тестовый покупатель'", "test-buyer", "ООО", "BUYER", "GOODS", "Производство", "Россия", "Центральный", "Московская область", "Москва", "Общество с ограниченной ответственностью 'Тестовый покупатель'", "9876543210", "1234567890123", "123456789", "2020-01-01", "г. Москва, ул. Тестовая, д. 1", "+7-999-123-45-67", "buyer@test.com", 0, 0, 0, user_id, True)
        
        print(f"Создана компания-покупатель с ID: {buyer_company_id}")
        
        # Создаем компанию-продавца
        seller_company_id = await conn.fetchval("""
            INSERT INTO companies (name, slug, type, trade_activity, business_type, activity_type, country, federal_district, region, city, full_name, inn, ogrn, kpp, registration_date, legal_address, phone, email, total_views, monthly_views, total_purchases, user_id, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, NOW(), NOW())
            RETURNING id
        """, "ООО 'Тестовый продавец'", "test-seller", "ООО", "SELLER", "GOODS", "Производство", "Россия", "Северо-Западный", "Ленинградская область", "Санкт-Петербург", "Общество с ограниченной ответственностью 'Тестовый продавец'", "1234567890", "9876543210987", "987654321", "2020-01-01", "г. Санкт-Петербург, ул. Продажная, д. 2", "+7-999-987-65-43", "seller@test.com", 0, 0, 0, user_id, True)
        
        print(f"Создана компания-продавец с ID: {seller_company_id}")
        
        await conn.close()
        print("Тестовые данные созданы успешно!")
        print(f"Email: buyer@test.com")
        print(f"Password: testpassword123")
        print(f"INN: 9876543210")
        print(f"Buyer Company ID: {buyer_company_id}")
        print(f"Seller Company ID: {seller_company_id}")
        
    except Exception as e:
        print(f"Ошибка при создании тестовых данных: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(create_test_user())
