import asyncio
import asyncpg
import random
import json
from datetime import datetime
from typing import List, Dict, Any

DATABASE_URL = 'postgresql://postgres:postgres@db/postgres'

class RealisticDataPopulator:
    def __init__(self):
        self.connection = None
        self.cities = []
        self.regions = []
        self.federal_districts = []
        
    async def connect(self):
        self.connection = await asyncpg.connect(DATABASE_URL)
        print("✅ Подключение к базе данных установлено")
        
    async def disconnect(self):
        if self.connection:
            await self.connection.close()
            print("✅ Соединение с базой данных закрыто")
    
    async def load_cities_data(self):
        """Загружаем реальные города из базы данных"""
        print("🔄 Загружаем данные о городах...")
        
        # Загружаем города с регионами и федеральными округами
        query = """
            SELECT 
                c.id as city_id,
                c.name as city_name,
                c.population,
                c.is_million_city,
                c.is_regional_center,
                r.id as region_id,
                r.name as region_name,
                fd.id as federal_district_id,
                fd.name as federal_district_name
            FROM cities c
            JOIN regions r ON c.region_id = r.id
            JOIN federal_districts fd ON r.federal_district_id = fd.id
            ORDER BY c.population DESC
        """
        
        result = await self.connection.fetch(query)
        self.cities = [dict(row) for row in result]
        
        print(f"✅ Загружено {len(self.cities)} городов")
        
        # Показываем топ-10 городов
        print("\n🏙️ Топ-10 городов по населению:")
        for i, city in enumerate(self.cities[:10], 1):
            print(f"{i:2d}. {city['city_name']} ({city['population']:,} чел.) - {city['region_name']}")
    
    async def clear_existing_data(self):
        """Очищаем существующие тестовые данные"""
        print("🔄 Очищаем существующие тестовые данные...")
        
        # Удаляем в правильном порядке (сначала зависимые таблицы)
        await self.connection.execute("DELETE FROM announcements WHERE company_id IN (SELECT id FROM companies WHERE name LIKE '%Тест%' OR name LIKE '%ООО%')")
        await self.connection.execute("DELETE FROM products WHERE company_id IN (SELECT id FROM companies WHERE name LIKE '%Тест%' OR name LIKE '%ООО%')")
        await self.connection.execute("DELETE FROM companies WHERE name LIKE '%Тест%' OR name LIKE '%ООО%'")
        
        print("✅ Тестовые данные очищены")
    
    async def create_companies(self, count: int = 100):
        """Создаем компании в реальных городах"""
        print(f"🔄 Создаем {count} компаний...")
        
        company_types = [
            "ООО", "ИП", "ЗАО", "ОАО", "АО", "ПАО", "ТОО", "ЧП"
        ]
        
        business_activities = [
            "IT-услуги и разработка", "Консалтинг", "Образование", "Медицинские услуги",
            "Юридические услуги", "Логистика и доставка", "Ремонт и обслуживание",
            "Дизайн и маркетинг", "Бухгалтерские услуги", "Строительство",
            "Красота и здоровье", "Туризм и отдых", "Финансовые услуги",
            "Производство", "Торговля", "Общественное питание", "Недвижимость",
            "Автомобильные услуги", "Сельское хозяйство", "Энергетика"
        ]
        
        trade_activities = ["BUYER", "SELLER", "BOTH"]
        business_types = ["GOODS", "SERVICES", "BOTH"]
        
        companies_created = 0
        
        for i in range(count):
            try:
                # Выбираем случайный город
                city = random.choice(self.cities)
                
                # Генерируем название компании
                company_type = random.choice(company_types)
                activity = random.choice(business_activities)
                company_name = f"{company_type} \"{activity}\""
                
                # Создаем slug
                slug = f"company-{companies_created + 1}"
                
                # Генерируем уникальные реквизиты
                inn = f"{random.randint(1000000000, 9999999999)}"
                ogrn = f"{random.randint(1000000000000, 9999999999999)}"
                kpp = f"{random.randint(100000000, 999999999)}"
                
                # Проверяем уникальность ИНН
                existing_inn = await self.connection.fetchval("SELECT inn FROM companies WHERE inn = $1", inn)
                if existing_inn:
                    inn = f"{random.randint(1000000000, 9999999999)}"
                
                # Вставляем компанию
                company_id = await self.connection.fetchval("""
                    INSERT INTO companies (
                        name, slug, type, trade_activity, business_type, activity_type, description,
                        country, federal_district, region, city,
                        country_id, federal_district_id, region_id, city_id,
                        full_name, inn, ogrn, kpp, registration_date, legal_address, production_address,
                        phone, email, website, total_views, monthly_views, total_purchases,
                        user_id, is_active, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, $30, NOW(), NOW())
                    RETURNING id
                """,
                    company_name,
                    slug,
                    company_type,
                    random.choice(trade_activities),
                    random.choice(business_types),
                    activity,
                    f"Профессиональные услуги в сфере {activity.lower()}. Качественное выполнение работ с гарантией результата.",
                    "Российская Федерация",
                    city['federal_district_name'],
                    city['region_name'],
                    city['city_name'],
                    1,  # country_id для России
                    city['federal_district_id'],
                    city['region_id'],
                    city['city_id'],
                    f"{company_type} \"{activity}\"",
                    inn,
                    ogrn,
                    kpp,
                    datetime.now(),
                    f"{city['city_name']}, ул. Примерная, д. {random.randint(1, 100)}",
                    f"{city['city_name']}, ул. Производственная, д. {random.randint(1, 100)}",
                    f"+7 ({random.randint(900, 999)}) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
                    f"info@{slug}.ru",
                    f"https://{slug}.ru",
                    0, 0, 0, 1, True
                )
                
                companies_created += 1
                
                if companies_created % 10 == 0:
                    print(f"✅ Создано {companies_created} компаний...")
                    
            except Exception as e:
                print(f"❌ Ошибка при создании компании {i+1}: {e}")
                continue
        
        print(f"✅ Создано {companies_created} компаний")
        return companies_created
    
    async def create_products(self, companies_count: int, products_per_company: int = 3):
        """Создаем товары и услуги для компаний"""
        print(f"🔄 Создаем товары и услуги...")
        
        # Получаем все компании
        companies = await self.connection.fetch("SELECT id, name, activity_type FROM companies ORDER BY id")
        
        goods_categories = [
            "Электроника", "Одежда", "Мебель", "Продукты питания", "Книги",
            "Спортивные товары", "Автомобили", "Строительные материалы", "Инструменты",
            "Косметика", "Игрушки", "Бытовая техника", "Компьютеры", "Телефоны"
        ]
        
        services_categories = [
            "Веб-разработка", "Дизайн", "Консалтинг", "Обучение", "Ремонт",
            "Доставка", "Уборка", "Переводы", "Бухгалтерия", "Юридические услуги",
            "Медицинские услуги", "Красота", "Фитнес", "Туризм", "Логистика"
        ]
        
        products_created = 0
        
        for company in companies:
            try:
                # Создаем товары для компании
                for i in range(random.randint(1, products_per_company)):
                    is_service = random.choice([True, False])
                    
                    if is_service:
                        category = random.choice(services_categories)
                        product_name = f"{category} {random.choice(['Профессиональный', 'Экспертный', 'Базовый', 'Премиум'])}"
                        product_type = "SERVICE"
                        price = random.randint(1000, 50000)
                        unit = random.choice(["час", "день", "месяц", "проект", "усл"])
                    else:
                        category = random.choice(goods_categories)
                        product_name = f"{category} {random.choice(['Качественный', 'Премиум', 'Стандартный', 'Эконом'])}"
                        product_type = "GOOD"
                        price = random.randint(100, 100000)
                        unit = random.choice(["шт", "кг", "м", "л", "упак"])
                    
                    # Генерируем характеристики
                    characteristics = {
                        "Категория": category,
                        "Срок выполнения": f"{random.randint(1, 30)} дней",
                        "Гарантия": f"{random.randint(6, 24)} месяцев",
                        "Поддержка": "24/7" if is_service else "Рабочие дни",
                        "Опыт": f"{random.randint(1, 15)} лет"
                    }
                    
                    # Создаем slug
                    slug = f"product-{products_created + 1}"
                    
                    # Вставляем продукт
                    product_id = await self.connection.fetchval("""
                        INSERT INTO products (
                            name, slug, description, article, type, price, images, characteristics,
                            is_hidden, is_deleted, unit_of_measurement, company_id, created_at, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW(), NOW())
                        RETURNING id
                    """,
                        product_name,
                        slug,
                        f"{product_name}. Качественный товар/услуга с гарантией качества.",
                        f"ART-{random.randint(100000, 999999)}",
                        product_type,
                        price,
                        "[]",
                        json.dumps(characteristics),
                        False,
                        False,
                        unit,
                        company['id']
                    )
                    
                    products_created += 1
                    
            except Exception as e:
                print(f"❌ Ошибка при создании продукта для компании {company['id']}: {e}")
                continue
        
        print(f"✅ Создано {products_created} товаров и услуг")
        return products_created

async def main():
    populator = RealisticDataPopulator()
    
    try:
        await populator.connect()
        await populator.load_cities_data()
        await populator.clear_existing_data()
        
        companies_count = await populator.create_companies(100)
        products_count = await populator.create_products(companies_count, 3)
        
        print(f"\n🎉 Готово!")
        print(f"📊 Статистика:")
        print(f"   - Компаний: {companies_count}")
        print(f"   - Товаров и услуг: {products_count}")
        print(f"   - Городов использовано: {len(populator.cities)}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await populator.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
