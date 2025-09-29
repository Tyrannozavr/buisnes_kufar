#!/usr/bin/env python3
"""
Демонстрационный скрипт для показа возможностей заполнения базы данных
Создает разнообразные примеры данных для демонстрации
"""

import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent))

from seed_database import DatabaseSeeder, RUSSIAN_CITIES, BUSINESS_ACTIVITIES
from app.api.authentication.models.user import User
from app.api.company.models.company import Company, TradeActivity, BusinessType
from app.api.products.models.product import Product, ProductType
from app.api.company.models.announcement import Announcement
from app.db.base import AsyncSessionLocal
import bcrypt


class DemoSeeder(DatabaseSeeder):
    """Демонстрационный седер с конкретными примерами"""
    
    async def create_demo_data(self):
        """Создание демонстрационных данных"""
        print("🎭 Создание демонстрационных данных...")
        
        # Создаем конкретных пользователей для демонстрации
        demo_users = [
            {
                "name": "Иван Петров",
                "email": "ivan.petrov@example.com",
                "position": "Генеральный директор",
                "company_type": "Производство мебели"
            },
            {
                "name": "Анна Сидорова", 
                "email": "anna.sidorova@example.com",
                "position": "Коммерческий директор",
                "company_type": "IT-услуги"
            },
            {
                "name": "Михаил Козлов",
                "email": "mikhail.kozlov@example.com", 
                "position": "Директор по развитию",
                "company_type": "Строительство"
            }
        ]
        
        for i, user_data in enumerate(demo_users, 1):
            first_name, last_name = user_data["name"].split()
            
            user = User(
                email=user_data["email"],
                first_name=first_name,
                last_name=last_name,
                patronymic="Александрович" if i == 1 else "Сергеевич" if i == 2 else "Владимирович",
                phone=f"+7 9{random.randint(10, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
                inn=f"{random.randint(1000000000, 9999999999)}",
                position=user_data["position"],
                hashed_password=bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=True
            )
            self.session.add(user)
            self.users.append(user)
        
        await self.session.flush()
        
        # Создаем демонстрационные компании
        demo_companies_data = [
            {
                "name": "Мебельная фабрика 'Дуб'",
                "activity": "Производство мебели",
                "city": "Москва",
                "description": "Производим качественную мебель из натурального дерева. Работаем с 1995 года."
            },
            {
                "name": "IT-компания 'ТехноСофт'", 
                "activity": "IT-услуги",
                "city": "Санкт-Петербург",
                "description": "Разрабатываем веб-приложения и мобильные приложения. Современные технологии."
            },
            {
                "name": "Строительная компания 'СтройМастер'",
                "activity": "Строительство", 
                "city": "Екатеринбург",
                "description": "Строим дома и коммерческие объекты. Полный цикл строительных работ."
            }
        ]
        
        for i, (user, company_data) in enumerate(zip(self.users, demo_companies_data), 1):
            company = Company(
                name=company_data["name"],
                slug=f"demo-company-{i}",
                logo=None,
                type="ООО",
                trade_activity=TradeActivity.BOTH,
                business_type=BusinessType.BOTH,
                activity_type=company_data["activity"],
                description=company_data["description"],
                country="Россия",
                federal_district="Центральный федеральный округ" if i == 1 else "Северо-Западный федеральный округ" if i == 2 else "Уральский федеральный округ",
                region="Московская область" if i == 1 else "Ленинградская область" if i == 2 else "Свердловская область",
                city=company_data["city"],
                full_name=f"ООО '{company_data['name']}'",
                inn=f"{random.randint(1000000000, 9999999999)}",
                ogrn=f"{random.randint(1000000000000, 9999999999999)}",
                kpp=f"{random.randint(100000000, 999999999)}",
                registration_date=datetime.now() - timedelta(days=random.randint(1000, 5000)),
                legal_address=f"{company_data['city']}, ул. Промышленная, д.{i}",
                production_address=f"{company_data['city']}, пр. Заводской, д.{i}",
                phone=f"+7 9{random.randint(10, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
                email=f"info@{company_data['name'].lower().replace(' ', '').replace("'", '')}.ru",
                website=f"www.{company_data['name'].lower().replace(' ', '').replace("'", '')}.ru",
                total_views=random.randint(1000, 50000),
                monthly_views=random.randint(100, 5000),
                total_purchases=random.randint(50, 1000),
                user_id=user.id,
                is_active=True
            )
            self.session.add(company)
            self.companies.append(company)
        
        await self.session.flush()
        
        # Создаем демонстрационные товары
        demo_products = [
            {
                "name": "Диван угловой 'Премиум'",
                "description": "Угловой диван из натуральной кожи. Современный дизайн, максимальный комфорт.",
                "price": 125000.00,
                "characteristics": [
                    {"key": "Материал", "value": "Натуральная кожа"},
                    {"key": "Цвет", "value": "Коричневый"},
                    {"key": "Размер", "value": "Большой"}
                ],
                "company_index": 0
            },
            {
                "name": "Кровать двуспальная 'Классик'",
                "description": "Двуспальная кровать из массива дуба. Классический стиль, долговечность.",
                "price": 85000.00,
                "characteristics": [
                    {"key": "Материал", "value": "Массив дуба"},
                    {"key": "Цвет", "value": "Натуральный"},
                    {"key": "Размер", "value": "200x160 см"}
                ],
                "company_index": 0
            },
            {
                "name": "Разработка веб-сайта 'Корпоративный'",
                "description": "Полный цикл разработки корпоративного веб-сайта. Современные технологии, адаптивный дизайн.",
                "price": 250000.00,
                "characteristics": [
                    {"key": "Технологии", "value": "React, Node.js, PostgreSQL"},
                    {"key": "Срок выполнения", "value": "2 месяца"},
                    {"key": "Сложность", "value": "Высокая"}
                ],
                "company_index": 1,
                "type": ProductType.SERVICE
            },
            {
                "name": "Мобильное приложение 'Бизнес'",
                "description": "Разработка мобильного приложения для iOS и Android. Нативная разработка.",
                "price": 500000.00,
                "characteristics": [
                    {"key": "Платформы", "value": "iOS, Android"},
                    {"key": "Срок выполнения", "value": "3 месяца"},
                    {"key": "Сложность", "value": "Экспертная"}
                ],
                "company_index": 1,
                "type": ProductType.SERVICE
            },
            {
                "name": "Коттедж 'Семейный' 150м²",
                "description": "Строительство коттеджа под ключ. Качественные материалы, современные технологии.",
                "price": 3500000.00,
                "characteristics": [
                    {"key": "Площадь", "value": "150 м²"},
                    {"key": "Материал", "value": "Кирпич"},
                    {"key": "Срок строительства", "value": "6 месяцев"}
                ],
                "company_index": 2,
                "type": ProductType.SERVICE
            }
        ]
        
        for i, product_data in enumerate(demo_products, 1):
            product_type = product_data.get("type", ProductType.GOOD)
            company = self.companies[product_data["company_index"]]
            
            product = Product(
                name=product_data["name"],
                slug=f"demo-{product_type.value.lower()}-{i}",
                description=product_data["description"],
                article=f"D{i:06}",
                type=product_type,
                price=product_data["price"],
                images=[],
                characteristics=product_data["characteristics"],
                is_hidden=False,
                is_deleted=False,
                unit_of_measurement="шт" if product_type == ProductType.GOOD else "проект",
                company_id=company.id
            )
            self.session.add(product)
            if product_type == ProductType.GOOD:
                self.products.append(product)
            else:
                self.services.append(product)
        
        # Создаем демонстрационные объявления
        demo_announcements = [
            {
                "title": "Ищем поставщиков древесины",
                "content": "Мебельная фабрика 'Дуб' ищет надежных поставщиков качественной древесины. Готовы к долгосрочному сотрудничеству.",
                "category": "Покупка",
                "company_index": 0
            },
            {
                "title": "Продаем мебель со склада",
                "content": "Большой выбор готовой мебели со склада. Скидки до 30%. Быстрая доставка по Москве и области.",
                "category": "Продажа", 
                "company_index": 0
            },
            {
                "title": "Ищем IT-специалистов",
                "content": "IT-компания 'ТехноСофт' приглашает на работу разработчиков. Удаленная работа, конкурентная зарплата.",
                "category": "Вакансии",
                "company_index": 1
            },
            {
                "title": "Предлагаем услуги разработки",
                "content": "Разрабатываем веб-сайты, мобильные приложения, корпоративные системы. Современные технологии.",
                "category": "Услуги",
                "company_index": 1
            },
            {
                "title": "Строительство домов под ключ",
                "content": "Строим дома и коттеджи под ключ. Индивидуальные проекты, качественные материалы, гарантия.",
                "category": "Услуги",
                "company_index": 2
            },
            {
                "title": "Ищем строительные материалы",
                "content": "Строительная компания 'СтройМастер' ищет поставщиков кирпича, бетона, арматуры.",
                "category": "Покупка",
                "company_index": 2
            }
        ]
        
        for announcement_data in demo_announcements:
            company = self.companies[announcement_data["company_index"]]
            
            announcement = Announcement(
                title=announcement_data["title"],
                content=announcement_data["content"],
                category=announcement_data["category"],
                images=[],
                published=True,
                company_id=company.id
            )
            self.session.add(announcement)
            self.announcements.append(announcement)


async def main():
    """Главная функция демонстрационного скрипта"""
    print("🎭 Демонстрационное заполнение базы данных")
    print("=" * 50)
    
    async with AsyncSessionLocal() as session:
        seeder = DemoSeeder()
        seeder.session = session
        
        # Очищаем базу
        print("🧹 Очистка данных...")
        await seeder._clear_database()
        
        # Создаем демонстрационные данные
        await seeder.create_demo_data()
        
        # Сохраняем
        await seeder.session.commit()
        
        print("\n✅ Демонстрационные данные созданы!")
        print("\n📊 Создано:")
        print(f"👥 Пользователей: {len(seeder.users)}")
        print(f"🏢 Компаний: {len(seeder.companies)}")
        print(f"📦 Товаров: {len(seeder.products)}")
        print(f"🔧 Услуг: {len(seeder.services)}")
        print(f"📢 Объявлений: {len(seeder.announcements)}")
        
        print("\n🎯 Примеры созданных данных:")
        print("👤 Пользователи:")
        for user in seeder.users:
            print(f"   - {user.first_name} {user.last_name} ({user.email}) - {user.position}")
        
        print("\n🏢 Компании:")
        for company in seeder.companies:
            print(f"   - {company.name} ({company.city}) - {company.activity_type}")
        
        print("\n📦 Товары и услуги:")
        for product in seeder.products + seeder.services:
            print(f"   - {product.name} - {product.price:,.0f} руб. ({product.company.name})")


if __name__ == "__main__":
    asyncio.run(main())
