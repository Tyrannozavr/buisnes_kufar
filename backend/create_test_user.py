"""
Script to create a test user for development
Bypasses email verification for quick testing
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.authentication.models.user import User, RegistrationToken
from app.api.company.models.company import Company, TradeActivity, BusinessType
from app.core.security import get_password_hash
from app.db.base import Base

# Database URL - use environment variable or default
# When running in Docker, use 'db' as hostname, otherwise 'localhost'
DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/buisnes_kufar"
)

# Test user data
TEST_USER = {
    "email": "test@example.com",
    "phone": "+1234567890",
    "password": "Test123!",
    "first_name": "Test",
    "last_name": "User",
    "patronymic": "Testovich"
}

TEST_COMPANY = {
    "name": "Test Company LLC",
    "full_name": "Test Company Limited Liability Company",
    "inn": "1234567890",
    "ogrn": "1234567890123",
    "kpp": "123456789",
    "slug": "test-company-llc",
    "type": "ООО",
    "trade_activity": TradeActivity.BOTH,
    "business_type": BusinessType.BOTH,
    "activity_type": "Информационные технологии",
    "description": "Test company for development",
    "country": "Россия",
    "federal_district": "Центральный федеральный округ",
    "region": "Москва",
    "city": "Москва",
    "legal_address": "г. Москва, ул. Тестовая, д. 1",
    "phone": "+79001234567",
    "email": "info@testcompany.com",
    "registration_date": datetime.now(),
    "is_active": True
}


def create_test_user():
    """Create a test user with company in the database"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("🧪 Creating test user and company...\n")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == TEST_USER["email"]).first()
        if existing_user:
            print(f"⚠️  User with email {TEST_USER['email']} already exists!")
            print("   Deleting existing user and company...\n")
            if existing_user.company:
                db.delete(existing_user.company)
            db.delete(existing_user)
            db.commit()
        
        # Check if company with INN exists
        existing_company = db.query(Company).filter(Company.inn == TEST_COMPANY["inn"]).first()
        if existing_company:
            print(f"⚠️  Company with INN {TEST_COMPANY['inn']} already exists!")
            print("   Deleting existing company...\n")
            db.delete(existing_company)
            db.commit()
        
        # Create company first
        print("📦 Creating test company...")
        company = Company(**TEST_COMPANY)
        db.add(company)
        db.flush()  # Get the company ID
        print(f"✅ Company created with ID: {company.id}")
        
        # Create user
        print("\n👤 Creating test user...")
        user = User(
            email=TEST_USER["email"],
            phone=TEST_USER["phone"],
            first_name=TEST_USER["first_name"],
            last_name=TEST_USER["last_name"],
            patronymic=TEST_USER["patronymic"],
            hashed_password=get_password_hash(TEST_USER["password"]),
            company_id=company.id,
            is_active=True
        )
        db.add(user)
        db.commit()
        print(f"✅ User created with ID: {user.id}")
        
        # Print credentials
        print("\n" + "="*60)
        print("✅ Test user and company created successfully!")
        print("="*60)
        print("\n🔐 Login credentials:")
        print(f"   URL: http://localhost:3001/auth/login")
        print(f"   Email: {TEST_USER['email']}")
        print(f"   Password: {TEST_USER['password']}")
        print(f"\n🏢 Company info:")
        print(f"   Name: {TEST_COMPANY['name']}")
        print(f"   INN: {TEST_COMPANY['inn']}")
        print(f"   Profile: http://localhost:3001/companies/{TEST_COMPANY['slug']}")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error creating test user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Check database connection first
    try:
        engine = create_engine(DATABASE_URL)
        engine.connect()
        print("✅ Database connection successful\n")
    except Exception as e:
        print(f"❌ Cannot connect to database: {e}")
        print("\nMake sure the database container is running:")
        print("   docker-compose -f docker-compose.dev.yml up -d db\n")
        sys.exit(1)
    
    create_test_user()
