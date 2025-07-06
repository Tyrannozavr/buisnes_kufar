import asyncio
import random
from datetime import datetime, timedelta

import bcrypt
from sqlalchemy import text

from app.api.authentication.models.user import User
from app.api.company.models.announcement import Announcement
from app.api.company.models.company import Company, TradeActivity, BusinessType
from app.api.products.models.product import Product, ProductType
from app.core.config import settings
# Import from base to ensure proper model registration order
from app.db.base import AsyncSessionLocal

# Настройки подключения к БД (используем асинхронный URL)
DATABASE_URL = settings.ASYNC_DATABASE_URL

# Примерные справочники
COUNTRIES = ["Россия", "Беларусь", "Казахстан"]
FEDERAL_DISTRICTS = ["Центральный", "Северо-Западный", "Южный", "Приволжский", "Уральский", "Сибирский",
                     "Дальневосточный"]
REGIONS = [f"Регион {i}" for i in range(1, 21)]
CITIES = [f"Город {i}" for i in range(1, 51)]

PRODUCT_NAMES = [f"Продукт {i}" for i in range(1, 101)]
SERVICE_NAMES = [f"Услуга {i}" for i in range(1, 51)]


async def seed():
    async with AsyncSessionLocal() as session:
        # Очищаем существующие данные (сначала зависимые таблицы)
        await session.execute(text("DELETE FROM announcements"))
        await session.execute(text("DELETE FROM products"))
        await session.execute(text("DELETE FROM company_officials"))
        await session.execute(text("DELETE FROM company_relations"))
        await session.execute(text("DELETE FROM chat_participants"))
        await session.execute(text("DELETE FROM messages"))
        await session.execute(text("DELETE FROM companies"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()

        # Создаем пользователей
        users = []
        for i in range(1, 101):
            user = User(
                email=f"user{i}@test.com",
                first_name=f"Имя{i}",
                last_name=f"Фамилия{i}",
                patronymic=f"Отчество{i}",
                phone=f"+7 900 000-{str(i).zfill(4)}",
                inn=f"{1000000000 + i}",
                position="Менеджер",
                hashed_password=bcrypt.hashpw("12345678".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=True
            )
            session.add(user)
            users.append(user)
        await session.flush()  # Получить id пользователей

        # Компании (по одной на пользователя)
        companies = []
        for i, user in enumerate(users, 1):
            country = random.choice(COUNTRIES)
            federal_district = random.choice(FEDERAL_DISTRICTS)
            region = random.choice(REGIONS)
            city = random.choice(CITIES)
            company = Company(
                name=f"Компания {i}",
                slug=f"company-{i}",
                logo=None,
                type="ООО",
                trade_activity=random.choice(list(TradeActivity)),
                business_type=random.choice(list(BusinessType)),
                activity_type=random.choice(["Производство", "Услуги", "Торговля"]),
                description=f"Описание компании {i}",
                country=country,
                federal_district=federal_district,
                region=region,
                city=city,
                full_name=f"ООО 'Компания {i}'",
                inn=f"{1000000000 + i}",
                ogrn=f"{1000000000000 + i}",
                kpp=f"{100000000 + i}",
                registration_date=datetime.now() - timedelta(days=random.randint(100, 5000)),
                legal_address=f"{city}, ул. Ленина, д.{i}",
                production_address=None,
                phone=f"+7 900 000-{str(i).zfill(4)}",
                email=f"company{i}@test.com",
                website=None,
                total_views=random.randint(0, 10000),
                monthly_views=random.randint(0, 1000),
                total_purchases=random.randint(0, 500),
                user_id=user.id,  # Каждый пользователь имеет одну компанию
                is_active=True
            )
            session.add(company)
            companies.append(company)
        await session.flush()  # Получить id компаний

        # Продукты
        for i in range(1, 301):
            company = random.choice(companies)
            product = Product(
                name=random.choice(PRODUCT_NAMES),
                slug=f"product-{i}",
                description=f"Описание продукта {i}",
                article=f"A{i:05}",
                type=ProductType.GOOD,
                price=random.uniform(100, 10000),
                images=[],
                characteristics=[{"key": "цвет", "value": random.choice(["красный", "синий", "зелёный"])}],
                is_hidden=False,
                is_deleted=False,
                unit_of_measurement="шт",
                company_id=company.id
            )
            session.add(product)

        # Услуги
        for i in range(1, 101):
            company = random.choice(companies)
            service = Product(
                name=random.choice(SERVICE_NAMES),
                slug=f"service-{i}",
                description=f"Описание услуги {i}",
                article=f"S{i:05}",
                type=ProductType.SERVICE,
                price=random.uniform(500, 20000),
                images=[],
                characteristics=[{"key": "срок", "value": f"{random.randint(1, 30)} дней"}],
                is_hidden=False,
                is_deleted=False,
                unit_of_measurement="усл",
                company_id=company.id
            )
            session.add(service)

        # Объявления
        announcement_categories = ["Покупка", "Продажа", "Обмен", "Аренда"]
        for i in range(1, 201):
            company = random.choice(companies)
            announcement = Announcement(
                title=f"Объявление {i}",
                content=f"Текст объявления {i}",
                category=random.choice(announcement_categories),
                images=[],
                published=True,
                company_id=company.id
            )
            session.add(announcement)

        await session.commit()
        print("Тестовые данные успешно добавлены!")


if __name__ == "__main__":
    asyncio.run(seed())
