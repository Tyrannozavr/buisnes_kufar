"""
Script to create multiple test users with companies and products for development
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
from app.api.products.models.product import Product, ProductType
from app.core.security import get_password_hash
from app.db.base import Base

# Database URL - use environment variable or default
# When running in Docker, use 'db' as hostname, otherwise 'localhost'
DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/buisnes_kufar"
)

# Test users data
TEST_USERS = [
    {
        "email": "test1@example.com",
        "phone": "+1234567890",
        "password": "Test123!",
        "first_name": "Иван",
        "last_name": "Петров",
        "patronymic": "Сергеевич"
    },
    {
        "email": "test2@example.com",
        "phone": "+1234567891",
        "password": "Test123!",
        "first_name": "Мария",
        "last_name": "Сидорова",
        "patronymic": "Александровна"
    },
    {
        "email": "test3@example.com",
        "phone": "+1234567892",
        "password": "Test123!",
        "first_name": "Алексей",
        "last_name": "Иванов",
        "patronymic": "Дмитриевич"
    },
    {
        "email": "test4@example.com",
        "phone": "+1234567893",
        "password": "Test123!",
        "first_name": "Елена",
        "last_name": "Кузнецова",
        "patronymic": "Викторовна"
    },
    {
        "email": "test5@example.com",
        "phone": "+1234567894",
        "password": "Test123!",
        "first_name": "Дмитрий",
        "last_name": "Смирнов",
        "patronymic": "Павлович"
    }
]

TEST_COMPANIES = [
    {
        "name": "ТехноСервис ООО",
        "full_name": "Общество с ограниченной ответственностью ТехноСервис",
        "inn": "1234567890",
        "ogrn": "1234567890123",
        "kpp": "123456789",
        "slug": "technoservice-llc",
        "type": "ООО",
        "trade_activity": TradeActivity.BOTH,
        "business_type": BusinessType.BOTH,
        "activity_type": "Информационные технологии",
        "description": "Компания занимается продажей компьютерной техники и программного обеспечения",
        "country": "Россия",
        "federal_district": "Центральный федеральный округ",
        "region": "Москва",
        "city": "Москва",
        "legal_address": "г. Москва, ул. Тверская, д. 10",
        "phone": "+79001234567",
        "email": "info@technoservice.com",
        "registration_date": datetime.now(),
        "is_active": True
    },
    {
        "name": "СтройМаркет ООО",
        "full_name": "Общество с ограниченной ответственностью СтройМаркет",
        "inn": "2345678901",
        "ogrn": "2345678901234",
        "kpp": "234567890",
        "slug": "stroymarket-llc",
        "type": "ООО",
        "trade_activity": TradeActivity.SELLER,
        "business_type": BusinessType.BOTH,
        "activity_type": "Строительные материалы",
        "description": "Оптовая и розничная продажа строительных материалов",
        "country": "Россия",
        "federal_district": "Центральный федеральный округ",
        "region": "Московская область",
        "city": "Красногорск",
        "legal_address": "г. Красногорск, ул. Строительная, д. 5",
        "phone": "+79002345678",
        "email": "info@stroymarket.com",
        "registration_date": datetime.now(),
        "is_active": True
    },
    {
        "name": "ЭлектроТорг ИП",
        "full_name": "Индивидуальный предприниматель Иванов Алексей Дмитриевич",
        "inn": "3456789012",
        "ogrn": "3456789012345",
        "kpp": "345678901",
        "slug": "electrotorg-ip",
        "type": "ИП",
        "trade_activity": TradeActivity.BOTH,
        "business_type": BusinessType.BOTH,
        "activity_type": "Электроника и бытовая техника",
        "description": "Розничная продажа электроники и бытовой техники",
        "country": "Россия",
        "federal_district": "Центральный федеральный округ",
        "region": "Москва",
        "city": "Москва",
        "legal_address": "г. Москва, ул. Ленинская, д. 15",
        "phone": "+79003456789",
        "email": "info@electrotorg.com",
        "registration_date": datetime.now(),
        "is_active": True
    },
    {
        "name": "МебельДизайн ООО",
        "full_name": "Общество с ограниченной ответственностью МебельДизайн",
        "inn": "4567890123",
        "ogrn": "4567890123456",
        "kpp": "456789012",
        "slug": "mebeldesign-llc",
        "type": "ООО",
        "trade_activity": TradeActivity.BOTH,
        "business_type": BusinessType.GOODS,
        "activity_type": "Производство мебели",
        "description": "Производство и продажа дизайнерской мебели",
        "country": "Россия",
        "federal_district": "Центральный федеральный округ",
        "region": "Москва",
        "city": "Москва",
        "legal_address": "г. Москва, ул. Мебельная, д. 20",
        "phone": "+79004567890",
        "email": "info@mebeldesign.com",
        "registration_date": datetime.now(),
        "is_active": True
    },
    {
        "name": "АвтоЗапчасти Плюс",
        "full_name": "Общество с ограниченной ответственностью АвтоЗапчасти Плюс",
        "inn": "5678901234",
        "ogrn": "5678901234567",
        "kpp": "567890123",
        "slug": "avtozapchasti-plus",
        "type": "ООО",
        "trade_activity": TradeActivity.SELLER,
        "business_type": BusinessType.GOODS,
        "activity_type": "Автозапчасти",
        "description": "Оптовая торговля автомобильными запчастями",
        "country": "Россия",
        "federal_district": "Центральный федеральный округ",
        "region": "Москва",
        "city": "Москва",
        "legal_address": "г. Москва, ул. Автомобильная, д. 30",
        "phone": "+79005678901",
        "email": "info@avtozapchasti.com",
        "registration_date": datetime.now(),
        "is_active": True
    }
]

# Products for each company
TEST_PRODUCTS = [
    # Products for ТехноСервис (IT)
    [
        {
            "name": "Ноутбук Dell XPS 15",
            "slug": "noutbuk-dell-xps-15",
            "description": "Профессиональный ноутбук для работы и развлечений",
            "article": "DELL-XPS-15-001",
            "type": ProductType.GOOD,
            "price": 125000.00,
            "unit_of_measurement": "шт",
            "characteristics": [
                {"name": "Процессор", "value": "Intel Core i7"},
                {"name": "ОЗУ", "value": "16 ГБ"},
                {"name": "SSD", "value": "512 ГБ"}
            ]
        },
        {
            "name": "Мышь Logitech MX Master 3",
            "slug": "mysh-logitech-mx-master-3",
            "description": "Беспроводная мышь для продуктивной работы",
            "article": "LOGI-MX3-001",
            "type": ProductType.GOOD,
            "price": 8500.00,
            "unit_of_measurement": "шт",
            "characteristics": [
                {"name": "Тип", "value": "Беспроводная"},
                {"name": "DPI", "value": "4000"}
            ]
        },
        {
            "name": "Установка Windows 10",
            "slug": "ustanovka-windows-10",
            "description": "Профессиональная установка операционной системы",
            "article": "SERV-WIN10-001",
            "type": ProductType.SERVICE,
            "price": 2500.00,
            "unit_of_measurement": "услуга",
            "characteristics": []
        }
    ],
    # Products for СтройМаркет (Construction)
    [
        {
            "name": "Цемент М500",
            "slug": "cement-m500",
            "description": "Портландцемент марки М500, мешок 50 кг",
            "article": "CEM-M500-50",
            "type": ProductType.GOOD,
            "price": 450.00,
            "unit_of_measurement": "мешок",
            "characteristics": [
                {"name": "Марка", "value": "М500"},
                {"name": "Вес", "value": "50 кг"}
            ]
        },
        {
            "name": "Кирпич керамический",
            "slug": "kirpich-keramicheskiy",
            "description": "Кирпич керамический рядовой полнотелый",
            "article": "KIR-KER-001",
            "type": ProductType.GOOD,
            "price": 18.00,
            "unit_of_measurement": "шт",
            "characteristics": [
                {"name": "Тип", "value": "Рядовой"},
                {"name": "Размер", "value": "250x120x65"}
            ]
        },
        {
            "name": "Гипсокартон Knauf",
            "slug": "gipsokarton-knauf",
            "description": "Гипсокартонный лист Knauf 2500x1200x12.5 мм",
            "article": "GIPS-KNAUF-001",
            "type": ProductType.GOOD,
            "price": 350.00,
            "unit_of_measurement": "лист",
            "characteristics": [
                {"name": "Размер", "value": "2500x1200x12.5 мм"}
            ]
        }
    ],
    # Products for ЭлектроТорг (Electronics)
    [
        {
            "name": "Телевизор Samsung 55 4K",
            "slug": "televizor-samsung-55-4k",
            "description": "Smart TV Samsung 55 дюймов с поддержкой 4K",
            "article": "SAM-TV-55-4K",
            "type": ProductType.GOOD,
            "price": 45000.00,
            "unit_of_measurement": "шт",
            "characteristics": [
                {"name": "Диагональ", "value": "55 дюймов"},
                {"name": "Разрешение", "value": "4K UHD"}
            ]
        },
        {
            "name": "Холодильник LG",
            "slug": "holodilnik-lg",
            "description": "Двухкамерный холодильник LG с системой No Frost",
            "article": "LG-FRIDGE-001",
            "type": ProductType.GOOD,
            "price": 38000.00,
            "unit_of_measurement": "шт",
            "characteristics": [
                {"name": "Объем", "value": "350 л"},
                {"name": "Класс", "value": "A++"}
            ]
        },
        {
            "name": "Пылесос Dyson V11",
            "slug": "pylesos-dyson-v11",
            "description": "Беспроводной пылесос Dyson V11 Absolute",
            "article": "DYSON-V11-001",
            "type": ProductType.GOOD,
            "price": 42000.00,
            "unit_of_measurement": "шт",
            "characteristics": [
                {"name": "Тип", "value": "Беспроводной"},
                {"name": "Время работы", "value": "60 мин"}
            ]
        }
    ],
    # Products for МебельДизайн (Furniture)
    [
        {
            "name": "Диван угловой 'Комфорт'",
            "slug": "divan-uglovoy-komfort",
            "description": "Современный угловой диван с механизмом трансформации",
            "article": "DIV-UGL-001",
            "type": ProductType.GOOD,
            "price": 65000.00,
            "unit_of_measurement": "шт",
            "characteristics": [
                {"name": "Материал", "value": "Велюр"},
                {"name": "Размер", "value": "280x180 см"}
            ]
        },
        {
            "name": "Шкаф-купе 'Премиум'",
            "slug": "shkaf-kupe-premium",
            "description": "Шкаф-купе с зеркальными дверями",
            "article": "SHKAF-KUP-001",
            "type": ProductType.GOOD,
            "price": 48000.00,
            "unit_of_measurement": "шт",
            "characteristics": [
                {"name": "Ширина", "value": "200 см"},
                {"name": "Высота", "value": "240 см"}
            ]
        },
        {
            "name": "Изготовление мебели на заказ",
            "slug": "izgotovlenie-mebeli-na-zakaz",
            "description": "Индивидуальное изготовление мебели по вашим размерам",
            "article": "SERV-MEB-001",
            "type": ProductType.SERVICE,
            "price": 15000.00,
            "unit_of_measurement": "проект",
            "characteristics": []
        }
    ],
    # Products for АвтоЗапчасти (Auto parts)
    [
        {
            "name": "Масло моторное Shell 5W-40",
            "slug": "maslo-motornoe-shell-5w-40",
            "description": "Синтетическое моторное масло Shell Helix Ultra 5W-40, 4л",
            "article": "SHELL-5W40-4L",
            "type": ProductType.GOOD,
            "price": 2800.00,
            "unit_of_measurement": "канистра",
            "characteristics": [
                {"name": "Тип", "value": "Синтетическое"},
                {"name": "Объем", "value": "4 л"}
            ]
        },
        {
            "name": "Тормозные колодки Brembo",
            "slug": "tormoznye-kolodki-brembo",
            "description": "Передние тормозные колодки Brembo",
            "article": "BREMBO-PAD-001",
            "type": ProductType.GOOD,
            "price": 3500.00,
            "unit_of_measurement": "комплект",
            "characteristics": [
                {"name": "Производитель", "value": "Brembo"},
                {"name": "Тип", "value": "Передние"}
            ]
        },
        {
            "name": "Аккумулятор Bosch 60Ah",
            "slug": "akkumulyator-bosch-60ah",
            "description": "Автомобильный аккумулятор Bosch S4 60Ah",
            "article": "BOSCH-S4-60",
            "type": ProductType.GOOD,
            "price": 6500.00,
            "unit_of_measurement": "шт",
            "characteristics": [
                {"name": "Емкость", "value": "60 Ah"},
                {"name": "Пусковой ток", "value": "540 A"}
            ]
        }
    ]
]


def create_test_users():
    """Create multiple test users with companies and products in the database"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("🧪 Creating test users, companies and products...\n")
        
        # Clean up existing test data
        print("🧹 Cleaning up existing test data...")
        for test_user in TEST_USERS:
            existing_user = db.query(User).filter(User.email == test_user["email"]).first()
            if existing_user:
                print(f"   Deleting user: {test_user['email']}")
                if existing_user.company:
                    # Delete products first (cascade should handle it, but being explicit)
                    products = db.query(Product).filter(Product.company_id == existing_user.company.id).all()
                    for product in products:
                        db.delete(product)
                    db.delete(existing_user.company)
                db.delete(existing_user)
        
        for test_company in TEST_COMPANIES:
            existing_company = db.query(Company).filter(Company.inn == test_company["inn"]).first()
            if existing_company:
                print(f"   Deleting company: {test_company['name']}")
                # Delete products
                products = db.query(Product).filter(Product.company_id == existing_company.id).all()
                for product in products:
                    db.delete(product)
                db.delete(existing_company)
        
        db.commit()
        print("✅ Cleanup complete\n")
        
        created_users = []
        
        # Create users, companies and products
        for idx, (test_user, test_company, products_data) in enumerate(zip(TEST_USERS, TEST_COMPANIES, TEST_PRODUCTS), 1):
            print(f"\n{'='*60}")
            print(f"Creating #{idx}: {test_user['first_name']} {test_user['last_name']}")
            print(f"{'='*60}")
            
            # Create company
            print(f"📦 Creating company: {test_company['name']}...")
            company = Company(**test_company)
            db.add(company)
            db.flush()  # Get the company ID
            print(f"✅ Company created with ID: {company.id}")
            
            # Create user
            print(f"👤 Creating user: {test_user['email']}...")
            user = User(
                email=test_user["email"],
                phone=test_user["phone"],
                first_name=test_user["first_name"],
                last_name=test_user["last_name"],
                patronymic=test_user["patronymic"],
                hashed_password=get_password_hash(test_user["password"]),
                company_id=company.id,
                is_active=True
            )
            db.add(user)
            db.flush()
            print(f"✅ User created with ID: {user.id}")
            
            # Create products
            print(f"🛍️  Creating {len(products_data)} products...")
            for product_data in products_data:
                product = Product(
                    company_id=company.id,
                    **product_data
                )
                db.add(product)
                print(f"   ✓ {product_data['name']} - {product_data['price']} руб.")
            
            db.flush()
            
            created_users.append({
                "user": test_user,
                "company": test_company,
                "products_count": len(products_data)
            })
        
        # Commit all changes
        db.commit()
        
        # Print summary
        print("\n" + "="*60)
        print("✅ All test data created successfully!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   Total users: {len(created_users)}")
        print(f"   Total companies: {len(TEST_COMPANIES)}")
        total_products = sum(item["products_count"] for item in created_users)
        print(f"   Total products: {total_products}")
        
        print("\n🔐 Login credentials (password for all: Test123!):")
        print(f"   URL: http://localhost:3001/auth/login\n")
        
        for idx, item in enumerate(created_users, 1):
            user = item["user"]
            company = item["company"]
            print(f"{idx}. {user['first_name']} {user['last_name']}")
            print(f"   Email: {user['email']}")
            print(f"   Company: {company['name']}")
            print(f"   Products: {item['products_count']}")
            print(f"   Profile: http://localhost:3001/companies/{company['slug']}")
            print()
        
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
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
    
    create_test_users()
