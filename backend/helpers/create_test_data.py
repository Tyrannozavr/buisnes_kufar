#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных в базе данных
Создает компании, пользователей, товары, услуги, объявления и должностных лиц
"""

import asyncio
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import AsyncSessionLocal
from app.api.company.models.company import Company, BusinessType, TradeActivity
from app.api.authentication.models.user import User, UserRole
from app.api.company.models.official import CompanyOfficial
from app.api.products.models.product import Product, ProductType
from app.api.company.models.announcement import Announcement
from app.api.common.models.country import Country
from app.api.common.models.federal_district import FederalDistrict
from app.api.common.models.region import Region
from app.api.common.models.city import City


# Тестовые данные
COMPANY_NAMES = [
    "ООО ТехноСтрой", "ИП Иванов А.В.", "ООО МегаПроект", "АО СтройИнвест", "ООО АльфаСтрой",
    "ИП Петров С.И.", "ООО БетонМир", "АО МеталлСервис", "ООО ЭлектроМонтаж", "ИП Сидоров М.А.",
    "ООО СантехПро", "АО КровляСтрой", "ООО ОтделкаПлюс", "ИП Козлов В.П.", "ООО ФасадМастер",
    "АО ИнженерСтрой", "ООО ГеоСтрой", "ИП Морозов Д.С.", "ООО ЛандшафтПро", "АО ДорогиСтрой",
    "ООО МостыСтрой", "ИП Волков А.Н.", "ООО ТуннелиСтрой", "АО АэропортыСтрой", "ООО ПортыСтрой",
    "ИП Орлов И.В.", "ООО ЖелезнодорогиСтрой", "АО ЭнергоСтрой", "ООО ВодоСтрой", "ИП Соколов П.М.",
    "ООО ГазоСтрой", "АО ТеплоСтрой", "ООО ХолодСтрой", "ИП Лебедев К.А.", "ООО ВентиляцияПро",
    "АО КондиционерыСтрой", "ООО ЛифтыСтрой", "ИП Соловьев Р.О.", "ООО ЭскалаторыСтрой", "АО АвтоматикаСтрой",
    "ООО БезопасностьСтрой", "ИП Павлов Е.Т.", "ООО ОхранаСтрой", "АО ПожарнаяСтрой", "ООО ВидеоСтрой",
    "ИП Федоров У.И.", "ООО СвязьСтрой", "АО ИнтернетСтрой", "ООО ТелефонияСтрой", "ИП Медведев Я.Р."
]

BUSINESS_TYPES = [
    BusinessType.GOODS,
    BusinessType.SERVICES,
    BusinessType.BOTH
]

TRADE_ACTIVITIES = [
    TradeActivity.SELLER,
    TradeActivity.SELLER,
    TradeActivity.SELLER
]

ACTIVITY_TYPES = [
    "Строительство жилых домов", "Строительство коммерческих зданий", "Ремонт квартир",
    "Отделочные работы", "Сантехнические работы", "Электромонтажные работы",
    "Кровельные работы", "Фасадные работы", "Ландшафтный дизайн", "Дорожное строительство",
    "Мостостроение", "Туннелестроение", "Аэропортостроение", "Портостроение",
    "Железнодорожное строительство", "Энергетическое строительство", "Водное строительство",
    "Газовое строительство", "Тепловое строительство", "Холодильное строительство",
    "Вентиляционные системы", "Кондиционирование", "Лифтовое оборудование",
    "Эскалаторное оборудование", "Автоматизация", "Системы безопасности",
    "Охранные системы", "Пожарная безопасность", "Видеонаблюдение",
    "Телекоммуникации", "Интернет-провайдинг", "Телефония"
]

PRODUCT_NAMES = [
    "Бетон М300", "Арматура А500С", "Кирпич керамический", "Блоки газобетонные", "Утеплитель минеральная вата",
    "Гипсокартон", "Профиль металлический", "Саморезы по металлу", "Дюбели", "Анкеры",
    "Краска водоэмульсионная", "Шпаклевка", "Грунтовка", "Обои", "Ламинат",
    "Паркет", "Линолеум", "Керамическая плитка", "Мозаика", "Керамогранит",
    "Сантехника", "Смесители", "Трубы полипропиленовые", "Трубы металлопластиковые", "Радиаторы отопления",
    "Кабель ВВГ", "Провод ПВС", "Автоматы защиты", "Розетки", "Выключатели",
    "Светильники", "Люстры", "Лампы LED", "Проводка", "Щиты распределительные",
    "Кровельный материал", "Гидроизоляция", "Пароизоляция", "Мембрана", "Пленка",
    "Фасадные панели", "Сайдинг", "Штукатурка", "Краска фасадная", "Утеплитель фасадный"
]

SERVICE_NAMES = [
    "Проектирование зданий", "Архитектурное проектирование", "Инженерное проектирование", "Дизайн интерьеров",
    "Строительство домов", "Ремонт квартир", "Отделочные работы", "Сантехнические работы",
    "Электромонтажные работы", "Кровельные работы", "Фасадные работы", "Ландшафтные работы",
    "Демонтажные работы", "Земляные работы", "Фундаментные работы", "Кладочные работы",
    "Бетонные работы", "Монтажные работы", "Пусконаладочные работы", "Гарантийное обслуживание",
    "Консультации по строительству", "Технический надзор", "Экспертиза зданий", "Оценка недвижимости",
    "Управление проектами", "Снабжение материалами", "Доставка материалов", "Складские услуги",
    "Аренда строительной техники", "Аренда инструмента", "Утилизация отходов", "Уборка территории"
]

ANNOUNCEMENT_TITLES = [
    "Строительство домов под ключ", "Ремонт квартир любой сложности", "Отделочные работы", "Сантехнические услуги",
    "Электромонтажные работы", "Кровельные работы", "Фасадные работы", "Ландшафтный дизайн",
    "Проектирование зданий", "Архитектурные услуги", "Инженерные системы", "Дизайн интерьеров",
    "Демонтажные работы", "Земляные работы", "Фундаментные работы", "Кладочные работы",
    "Бетонные работы", "Монтажные работы", "Пусконаладочные работы", "Гарантийное обслуживание",
    "Консультации по строительству", "Технический надзор", "Экспертиза зданий", "Оценка недвижимости",
    "Управление проектами", "Снабжение материалами", "Доставка материалов", "Складские услуги",
    "Аренда строительной техники", "Аренда инструмента", "Утилизация отходов", "Уборка территории"
]

ANNOUNCEMENT_CATEGORIES = [
    "Строительство", "Ремонт", "Отделка", "Сантехника", "Электрика", "Кровля", "Фасад", "Ландшафт",
    "Проектирование", "Архитектура", "Инженерия", "Дизайн", "Демонтаж", "Земляные работы", "Фундамент",
    "Кладка", "Бетон", "Монтаж", "Пусконаладка", "Обслуживание", "Консультации", "Надзор", "Экспертиза",
    "Оценка", "Управление", "Снабжение", "Доставка", "Склад", "Аренда", "Утилизация", "Уборка"
]

POSITIONS = [
    "Генеральный директор", "Финансовый директор", "Главный бухгалтер", "Коммерческий директор",
    "Технический директор", "Руководитель отдела продаж", "Руководитель отдела закупок",
    "Руководитель производства", "Главный инженер", "Проект-менеджер", "Архитектор",
    "Инженер-проектировщик", "Мастер строительных работ", "Прораб", "Начальник участка"
]

FIRST_NAMES = [
    "Александр", "Алексей", "Андрей", "Антон", "Артем", "Борис", "Вадим", "Валентин", "Валерий",
    "Виктор", "Виталий", "Владимир", "Владислав", "Геннадий", "Георгий", "Дмитрий", "Евгений",
    "Игорь", "Иван", "Кирилл", "Константин", "Леонид", "Максим", "Михаил", "Николай", "Олег",
    "Павел", "Петр", "Роман", "Сергей", "Станислав", "Степан", "Федор", "Юрий", "Яков"
]

LAST_NAMES = [
    "Иванов", "Петров", "Сидоров", "Козлов", "Морозов", "Волков", "Орлов", "Соколов", "Лебедев",
    "Соловьев", "Павлов", "Федоров", "Медведев", "Смирнов", "Кузнецов", "Попов", "Васильев",
    "Соколов", "Михайлов", "Новиков", "Федоров", "Морозов", "Петров", "Волков", "Алексеев",
    "Лебедев", "Семенов", "Егоров", "Павлов", "Козлов", "Степанов", "Николаев", "Орлов", "Андреев"
]

PATRONYMICS = [
    "Александрович", "Алексеевич", "Андреевич", "Антонович", "Артемович", "Борисович", "Вадимович",
    "Валентинович", "Валерьевич", "Викторович", "Витальевич", "Владимирович", "Владиславович",
    "Геннадьевич", "Георгиевич", "Дмитриевич", "Евгеньевич", "Игоревич", "Иванович", "Кириллович",
    "Константинович", "Леонидович", "Максимович", "Михайлович", "Николаевич", "Олегович", "Павлович",
    "Петрович", "Романович", "Сергеевич", "Станиславович", "Степанович", "Федорович", "Юрьевич", "Яковлевич"
]

UNITS_OF_MEASUREMENT = [
    "шт", "м", "м²", "м³", "кг", "т", "л", "мл", "кВт", "кВт·ч", "бар", "атм", "°C", "°F"
]


def generate_slug(name: str) -> str:
    """Генерирует slug из названия"""
    slug = name.lower()
    slug = slug.replace(" ", "-")
    slug = slug.replace("ооо", "")
    slug = slug.replace("ао", "")
    slug = slug.replace("ип", "")
    slug = slug.replace(".", "")
    slug = slug.replace(",", "")
    slug = slug.replace("(", "")
    slug = slug.replace(")", "")
    slug = slug.replace("'", "")
    slug = slug.replace('"', "")
    # Удаляем множественные дефисы
    while "--" in slug:
        slug = slug.replace("--", "-")
    # Удаляем дефисы в начале и конце
    slug = slug.strip("-")
    return slug


def generate_inn() -> str:
    """Генерирует случайный ИНН"""
    return str(random.randint(1000000000, 9999999999))


def generate_ogrn() -> str:
    """Генерирует случайный ОГРН"""
    return str(random.randint(1000000000000, 9999999999999))


def generate_kpp() -> str:
    """Генерирует случайный КПП"""
    return str(random.randint(100000000, 999999999))


def generate_unique_inn(existing_inns: set) -> str:
    """Генерирует уникальный ИНН"""
    while True:
        inn = generate_inn()
        if inn not in existing_inns:
            existing_inns.add(inn)
            return inn


def generate_unique_ogrn(existing_ogrns: set) -> str:
    """Генерирует уникальный ОГРН"""
    while True:
        ogrn = generate_ogrn()
        if ogrn not in existing_ogrns:
            existing_ogrns.add(ogrn)
            return ogrn


def generate_phone() -> str:
    """Генерирует случайный номер телефона"""
    return f"+7{random.randint(9000000000, 9999999999)}"


def generate_email(name: str) -> str:
    """Генерирует email на основе названия компании"""
    slug = generate_slug(name)
    domains = ["gmail.com", "yandex.ru", "mail.ru", "company.ru", "business.ru"]
    domain = random.choice(domains)
    return f"{slug}@{domain}"


def generate_price() -> float:
    """Генерирует случайную цену"""
    return round(random.uniform(100, 100000), 2)


def generate_random_date(start_date: datetime, end_date: datetime) -> datetime:
    """Генерирует случайную дату в диапазоне"""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)


async def get_random_location_data(session: AsyncSession) -> Dict[str, Any]:
    """Получает случайные данные о местоположении"""
    # Получаем случайную страну (Россия)
    country_result = await session.execute(
        select(Country).where(Country.code == "RU", Country.is_active == True)
    )
    country = country_result.scalar_one()
    
    # Получаем случайный федеральный округ
    fd_result = await session.execute(
        select(FederalDistrict).where(FederalDistrict.country_id == country.id, FederalDistrict.is_active == True)
    )
    federal_districts = fd_result.scalars().all()
    federal_district = random.choice(federal_districts)
    
    # Получаем случайный регион в этом федеральном округе
    region_result = await session.execute(
        select(Region).where(Region.federal_district_id == federal_district.id, Region.is_active == True)
    )
    regions = region_result.scalars().all()
    region = random.choice(regions)
    
    # Получаем случайный город в этом регионе
    city_result = await session.execute(
        select(City).where(City.region_id == region.id, City.is_active == True)
    )
    cities = city_result.scalars().all()
    
    # Если в регионе нет городов, берем первый город из базы
    if not cities:
        city_result = await session.execute(
            select(City).where(City.is_active == True).limit(1)
        )
        city = city_result.scalar_one()
        # Обновляем регион и федеральный округ для этого города
        region_result = await session.execute(
            select(Region).where(Region.id == city.region_id)
        )
        region = region_result.scalar_one()
        fd_result = await session.execute(
            select(FederalDistrict).where(FederalDistrict.id == region.federal_district_id)
        )
        federal_district = fd_result.scalar_one()
    else:
        city = random.choice(cities)
    
    return {
        "country": country.name,
        "federal_district": federal_district.name,
        "region": region.name,
        "city": city.name,
        "country_id": country.id,
        "federal_district_id": federal_district.id,
        "region_id": region.id,
        "city_id": city.id
    }


async def create_companies(session: AsyncSession, count: int = 50) -> List[Company]:
    """Создает тестовые компании"""
    companies = []
    existing_inns = set()
    existing_ogrns = set()
    
    print(f"Создание {count} компаний...")
    
    for i in range(count):
        name = random.choice(COMPANY_NAMES)
        if name in [c.name for c in companies]:
            name = f"{name} {i+1}"
        
        # Генерируем уникальный slug
        base_slug = generate_slug(name)
        slug = base_slug
        counter = 1
        while slug in [c.slug for c in companies]:
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        location_data = await get_random_location_data(session)
        
        company = Company(
            name=name,
            slug=slug,
            type=random.choice(["ООО", "АО", "ИП"]),
            trade_activity=random.choice(TRADE_ACTIVITIES),
            business_type=random.choice(BUSINESS_TYPES),
            activity_type=random.choice(ACTIVITY_TYPES),
            description=f"Компания {name} специализируется на {random.choice(ACTIVITY_TYPES).lower()}. "
                       f"Мы предоставляем качественные услуги и товары для строительной отрасли.",
            
            # Location (старые поля)
            country=location_data["country"],
            federal_district=location_data["federal_district"],
            region=location_data["region"],
            city=location_data["city"],
            
            # Location (новые FK поля)
            country_id=location_data["country_id"],
            federal_district_id=location_data["federal_district_id"],
            region_id=location_data["region_id"],
            city_id=location_data["city_id"],
            
            # Legal information
            full_name=f"{name} - полное юридическое наименование",
            inn=generate_unique_inn(existing_inns),
            ogrn=generate_unique_ogrn(existing_ogrns),
            kpp=generate_kpp(),
            registration_date=generate_random_date(
                datetime(2020, 1, 1), 
                datetime(2024, 12, 31)
            ),
            legal_address=f"г. {location_data['city']}, ул. Строительная, д. {random.randint(1, 100)}",
            production_address=f"г. {location_data['city']}, ул. Промышленная, д. {random.randint(1, 100)}",
            
            # Contact information
            phone=generate_phone(),
            email=generate_email(name),
            website=f"https://{generate_slug(name)}.ru",
            
            # Statistics
            total_views=random.randint(0, 10000),
            monthly_views=random.randint(0, 1000),
            total_purchases=random.randint(0, 500),
            
            # Status
            is_active=True
        )
        
        session.add(company)
        companies.append(company)
        
        if (i + 1) % 10 == 0:
            print(f"Создано {i + 1} компаний...")
    
    await session.commit()
    print(f"✅ Создано {len(companies)} компаний")
    return companies


async def create_users(session: AsyncSession, companies: List[Company]) -> List[User]:
    """Создает пользователей для компаний"""
    users = []
    existing_emails = set()
    
    print(f"Создание пользователей для {len(companies)} компаний...")
    
    for i, company in enumerate(companies):
        # Создаем владельца компании
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        patronymic = random.choice(PATRONYMICS)
        
        # Генерируем уникальный email
        base_email = generate_email(f"{first_name}.{last_name}")
        email = base_email
        counter = 1
        while email in existing_emails:
            email = f"{first_name.lower()}{last_name.lower()}{counter}@gmail.com"
            counter += 1
        existing_emails.add(email)
        
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            phone=generate_phone(),
            position="Владелец",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8Kz2",  # password: "password"
            is_active=True,
            company_id=company.id,
            role=UserRole.OWNER
        )
        
        session.add(user)
        users.append(user)
        
        # Создаем дополнительного сотрудника для некоторых компаний
        if random.random() < 0.7:  # 70% компаний имеют дополнительного сотрудника
            first_name2 = random.choice(FIRST_NAMES)
            last_name2 = random.choice(LAST_NAMES)
            patronymic2 = random.choice(PATRONYMICS)
            
            # Генерируем уникальный email для второго пользователя
            base_email2 = generate_email(f"{first_name2}.{last_name2}")
            email2 = base_email2
            counter2 = 1
            while email2 in existing_emails:
                email2 = f"{first_name2.lower()}{last_name2.lower()}{counter2}@gmail.com"
                counter2 += 1
            existing_emails.add(email2)
            
            user2 = User(
                email=email2,
                first_name=first_name2,
                last_name=last_name2,
                patronymic=patronymic2,
                phone=generate_phone(),
                position=random.choice(POSITIONS),
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8Kz2",
                is_active=True,
                company_id=company.id,
                role=UserRole.ADMIN
            )
            
            session.add(user2)
            users.append(user2)
        
        if (i + 1) % 10 == 0:
            print(f"Создано пользователей для {i + 1} компаний...")
    
    await session.commit()
    print(f"✅ Создано {len(users)} пользователей")
    return users


async def create_officials(session: AsyncSession, companies: List[Company]) -> List[CompanyOfficial]:
    """Создает должностных лиц для компаний"""
    officials = []
    
    print(f"Создание должностных лиц для {len(companies)} компаний...")
    
    for i, company in enumerate(companies):
        # Создаем 1-3 должностных лица для каждой компании
        num_officials = random.randint(1, 3)
        
        for j in range(num_officials):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            patronymic = random.choice(PATRONYMICS)
            
            official = CompanyOfficial(
                position=random.choice(POSITIONS),
                full_name=f"{last_name} {first_name} {patronymic}",
                company_id=company.id
            )
            
            session.add(official)
            officials.append(official)
        
        if (i + 1) % 10 == 0:
            print(f"Создано должностных лиц для {i + 1} компаний...")
    
    await session.commit()
    print(f"✅ Создано {len(officials)} должностных лиц")
    return officials


async def create_products(session: AsyncSession, companies: List[Company]) -> List[Product]:
    """Создает товары и услуги для компаний"""
    products = []
    existing_slugs = set()
    
    print(f"Создание товаров и услуг для {len(companies)} компаний...")
    
    for i, company in enumerate(companies):
        # Создаем 2-8 товаров/услуг для каждой компании
        num_products = random.randint(2, 8)
        
        for j in range(num_products):
            is_service = random.random() < 0.4  # 40% услуг, 60% товаров
            
            if is_service:
                name = random.choice(SERVICE_NAMES)
                product_type = ProductType.SERVICE
                unit = "час"
            else:
                name = random.choice(PRODUCT_NAMES)
                product_type = ProductType.GOOD
                unit = random.choice(UNITS_OF_MEASUREMENT)
            
            # Добавляем уникальность к названию
            unique_name = f"{name} {company.name}"
            
            # Генерируем уникальный slug
            base_slug = generate_slug(unique_name)
            slug = base_slug
            counter = 1
            while slug in existing_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
            existing_slugs.add(slug)
            
            product = Product(
                name=unique_name,
                slug=slug,
                description=f"Качественный {name.lower()} от компании {company.name}. "
                           f"Мы гарантируем высокое качество и надежность нашей продукции.",
                article=f"ART-{random.randint(100000, 999999)}",
                type=product_type,
                price=generate_price(),
                images=[],  # Пока без изображений
                characteristics=[
                    {"name": "Материал", "value": random.choice(["Сталь", "Пластик", "Дерево", "Бетон", "Кирпич"])},
                    {"name": "Цвет", "value": random.choice(["Белый", "Серый", "Коричневый", "Черный", "Красный"])},
                    {"name": "Размер", "value": f"{random.randint(10, 1000)}x{random.randint(10, 1000)} мм"},
                    {"name": "Вес", "value": f"{random.randint(1, 100)} кг"},
                ],
                is_hidden=False,
                is_deleted=False,
                unit_of_measurement=unit,
                company_id=company.id
            )
            
            session.add(product)
            products.append(product)
        
        if (i + 1) % 10 == 0:
            print(f"Создано товаров/услуг для {i + 1} компаний...")
    
    await session.commit()
    print(f"✅ Создано {len(products)} товаров и услуг")
    return products


async def create_announcements(session: AsyncSession, companies: List[Company]) -> List[Announcement]:
    """Создает объявления для компаний"""
    announcements = []
    existing_slugs = set()
    
    print(f"Создание объявлений для {len(companies)} компаний...")
    
    for i, company in enumerate(companies):
        # Создаем 1-5 объявлений для каждой компании
        num_announcements = random.randint(1, 5)
        
        for j in range(num_announcements):
            title = random.choice(ANNOUNCEMENT_TITLES)
            category = random.choice(ANNOUNCEMENT_CATEGORIES)
            
            # Добавляем уникальность к заголовку
            unique_title = f"{title} - {company.name}"
            
            # Генерируем уникальный slug
            base_slug = generate_slug(unique_title)
            slug = base_slug
            counter = 1
            while slug in existing_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
            existing_slugs.add(slug)
            
            announcement = Announcement(
                title=unique_title,
                content=f"""
<h3>О компании {company.name}</h3>
<p>Мы специализируемся на {company.activity_type.lower()} и предлагаем качественные услуги в области {category.lower()}.</p>

<h4>Наши услуги:</h4>
<ul>
    <li>{title}</li>
    <li>Консультации по строительству</li>
    <li>Проектирование</li>
    <li>Монтажные работы</li>
    <li>Гарантийное обслуживание</li>
</ul>

<h4>Почему выбирают нас:</h4>
<ul>
    <li>Опыт работы более {random.randint(3, 15)} лет</li>
    <li>Квалифицированные специалисты</li>
    <li>Современное оборудование</li>
    <li>Гарантия качества</li>
    <li>Доступные цены</li>
</ul>

<h4>Контакты:</h4>
<p>Телефон: {company.phone}</p>
<p>Email: {company.email}</p>
<p>Адрес: {company.legal_address}</p>

<p>Звоните нам прямо сейчас! Мы готовы обсудить ваш проект и предложить оптимальное решение.</p>
                """.strip(),
                category=category,
                images=[],  # Пока без изображений
                published=True,
                company_id=company.id
            )
            
            session.add(announcement)
            announcements.append(announcement)
        
        if (i + 1) % 10 == 0:
            print(f"Создано объявлений для {i + 1} компаний...")
    
    await session.commit()
    print(f"✅ Создано {len(announcements)} объявлений")
    return announcements


async def main():
    """Основная функция для создания всех тестовых данных"""
    print("🚀 Начинаем создание тестовых данных...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Создаем компании
            companies = await create_companies(session, count=50)
            
            # Создаем пользователей
            users = await create_users(session, companies)
            
            # Создаем должностных лиц
            officials = await create_officials(session, companies)
            
            # Создаем товары и услуги
            products = await create_products(session, companies)
            
            # Создаем объявления
            announcements = await create_announcements(session, companies)
            
            print("\n🎉 Все тестовые данные успешно созданы!")
            print(f"📊 Статистика:")
            print(f"   • Компаний: {len(companies)}")
            print(f"   • Пользователей: {len(users)}")
            print(f"   • Должностных лиц: {len(officials)}")
            print(f"   • Товаров и услуг: {len(products)}")
            print(f"   • Объявлений: {len(announcements)}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании тестовых данных: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())