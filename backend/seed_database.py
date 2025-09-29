#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных тестовыми данными
Создает реалистичные данные для компаний, продуктов, услуг и объявлений
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

import bcrypt
from sqlalchemy import text

from app.api.authentication.models.user import User
from app.api.company.models.announcement import Announcement
from app.api.company.models.company import Company, TradeActivity, BusinessType
from app.api.products.models.product import Product, ProductType
from app.core.config import settings
from app.db.base import AsyncSessionLocal

# Реальные данные для генерации
RUSSIAN_CITIES = [
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", 
    "Нижний Новгород", "Челябинск", "Самара", "Омск", "Ростов-на-Дону",
    "Уфа", "Красноярск", "Воронеж", "Пермь", "Волгоград", "Краснодар",
    "Саратов", "Тюмень", "Тольятти", "Ижевск", "Барнаул", "Ульяновск",
    "Иркутск", "Хабаровск", "Ярославль", "Владивосток", "Махачкала",
    "Томск", "Оренбург", "Кемерово", "Рязань", "Астрахань", "Пенза",
    "Липецк", "Тула", "Киров", "Чебоксары", "Калининград", "Брянск"
]

RUSSIAN_REGIONS = [
    "Московская область", "Ленинградская область", "Краснодарский край",
    "Свердловская область", "Республика Татарстан", "Нижегородская область",
    "Челябинская область", "Самарская область", "Омская область",
    "Ростовская область", "Республика Башкортостан", "Красноярский край",
    "Воронежская область", "Пермский край", "Волгоградская область",
    "Саратовская область", "Тюменская область", "Ульяновская область",
    "Иркутская область", "Хабаровский край", "Ярославская область",
    "Приморский край", "Республика Дагестан", "Томская область",
    "Оренбургская область", "Кемеровская область", "Рязанская область",
    "Астраханская область", "Пензенская область", "Липецкая область",
    "Тульская область", "Кировская область", "Чувашская Республика",
    "Калининградская область", "Брянская область"
]

FEDERAL_DISTRICTS = [
    "Центральный федеральный округ", "Северо-Западный федеральный округ",
    "Южный федеральный округ", "Приволжский федеральный округ",
    "Уральский федеральный округ", "Сибирский федеральный округ",
    "Дальневосточный федеральный округ", "Северо-Кавказский федеральный округ"
]

COMPANY_TYPES = ["ООО", "ИП", "АО", "ЗАО", "ОАО", "ПАО", "ТОО", "АООТ"]

BUSINESS_ACTIVITIES = [
    "Производство мебели", "Строительство", "IT-услуги", "Торговля",
    "Производство продуктов питания", "Логистика", "Консалтинг",
    "Производство одежды", "Автомобильные услуги", "Образование",
    "Медицинские услуги", "Финансовые услуги", "Недвижимость",
    "Производство электроники", "Сельское хозяйство", "Туризм",
    "Производство строительных материалов", "Реклама и маркетинг",
    "Производство химической продукции", "Энергетика"
]

PRODUCT_CATEGORIES = {
    "Товары": [
        "Мебель", "Электроника", "Одежда", "Продукты питания", "Строительные материалы",
        "Автомобили", "Книги", "Спортивные товары", "Косметика", "Инструменты",
        "Бытовая техника", "Игрушки", "Обувь", "Ювелирные изделия", "Сад и огород"
    ],
    "Услуги": [
        "IT-услуги", "Консалтинг", "Образование", "Медицинские услуги", "Юридические услуги",
        "Логистика", "Ремонт", "Дизайн", "Маркетинг", "Бухгалтерские услуги",
        "Строительство", "Автосервис", "Красота и здоровье", "Туризм", "Финансовые услуги"
    ]
}

PRODUCT_NAMES = {
    "Мебель": [
        "Диван угловой", "Кровать двуспальная", "Стол обеденный", "Стул офисный",
        "Шкаф-купе", "Тумба прикроватная", "Комод", "Кресло", "Стеллаж", "Пуф"
    ],
    "Электроника": [
        "Смартфон", "Ноутбук", "Планшет", "Телевизор", "Наушники",
        "Клавиатура", "Мышь", "Монитор", "Принтер", "Роутер"
    ],
    "Одежда": [
        "Платье", "Рубашка", "Джинсы", "Куртка", "Свитер",
        "Брюки", "Юбка", "Пальто", "Футболка", "Пиджак"
    ],
    "Продукты питания": [
        "Хлеб", "Молоко", "Мясо", "Овощи", "Фрукты",
        "Сыр", "Йогурт", "Крупа", "Масло", "Консервы"
    ],
    "IT-услуги": [
        "Разработка сайтов", "Мобильные приложения", "Системное администрирование",
        "Кибербезопасность", "Облачные решения", "Автоматизация бизнеса",
        "Техническая поддержка", "Консалтинг по IT", "Интеграция систем", "DevOps"
    ],
    "Консалтинг": [
        "Бизнес-консалтинг", "Управленческий консалтинг", "Финансовый консалтинг",
        "HR-консалтинг", "Маркетинговый консалтинг", "Стратегическое планирование",
        "Операционный консалтинг", "Консалтинг по продажам", "Консалтинг по закупкам"
    ],
    "Образование": [
        "Курсы программирования", "Языковые курсы", "Бизнес-образование",
        "Профессиональная переподготовка", "Подготовка к экзаменам", "Онлайн-обучение",
        "Корпоративное обучение", "Детские развивающие занятия", "Творческие курсы"
    ]
}

CHARACTERISTICS_TEMPLATES = {
    "Мебель": [
        {"key": "Материал", "value": ["Дерево", "МДФ", "ДСП", "Металл", "Стекло"]},
        {"key": "Цвет", "value": ["Белый", "Черный", "Коричневый", "Серый", "Бежевый"]},
        {"key": "Размер", "value": ["Маленький", "Средний", "Большой"]}
    ],
    "Электроника": [
        {"key": "Бренд", "value": ["Samsung", "Apple", "Xiaomi", "Huawei", "Sony"]},
        {"key": "Цвет", "value": ["Черный", "Белый", "Серый", "Золотой", "Серебряный"]},
        {"key": "Память", "value": ["64GB", "128GB", "256GB", "512GB", "1TB"]}
    ],
    "Одежда": [
        {"key": "Размер", "value": ["XS", "S", "M", "L", "XL", "XXL"]},
        {"key": "Цвет", "value": ["Черный", "Белый", "Красный", "Синий", "Зеленый"]},
        {"key": "Материал", "value": ["Хлопок", "Полиэстер", "Шерсть", "Лен", "Джинс"]}
    ],
    "IT-услуги": [
        {"key": "Срок выполнения", "value": ["1 неделя", "2 недели", "1 месяц", "2 месяца", "3 месяца"]},
        {"key": "Технологии", "value": ["Python", "JavaScript", "Java", "C#", "PHP"]},
        {"key": "Сложность", "value": ["Простая", "Средняя", "Сложная", "Экспертная"]}
    ]
}

FIRST_NAMES = [
    "Александр", "Алексей", "Андрей", "Антон", "Артем", "Борис", "Вадим", "Валентин",
    "Валерий", "Виктор", "Владимир", "Вячеслав", "Геннадий", "Георгий", "Дмитрий",
    "Евгений", "Иван", "Игорь", "Кирилл", "Константин", "Максим", "Михаил", "Николай",
    "Олег", "Павел", "Петр", "Роман", "Сергей", "Станислав", "Федор", "Юрий"
]

LAST_NAMES = [
    "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов", "Васильев",
    "Соколов", "Михайлов", "Новиков", "Федоров", "Морозов", "Волков", "Алексеев",
    "Лебедев", "Семенов", "Егоров", "Павлов", "Козлов", "Степанов", "Николаев",
    "Орлов", "Андреев", "Макаров", "Никитин", "Захаров", "Зайцев", "Соловьев"
]

POSITIONS = [
    "Генеральный директор", "Коммерческий директор", "Финансовый директор",
    "Директор по развитию", "Руководитель отдела продаж", "Менеджер по продажам",
    "Маркетолог", "Бухгалтер", "Юрист", "HR-менеджер", "IT-директор",
    "Руководитель производства", "Главный инженер", "Технолог"
]

ANNOUNCEMENT_CATEGORIES = [
    "Покупка", "Продажа", "Обмен", "Аренда", "Сотрудничество", "Поиск партнеров",
    "Тендеры", "Вакансии", "Новости компании", "Акции и скидки"
]

ANNOUNCEMENT_TITLES = [
    "Ищем поставщиков качественных материалов",
    "Продаем оборудование для производства",
    "Предлагаем услуги по логистике",
    "Ищем партнеров для совместных проектов",
    "Объявляем тендер на выполнение работ",
    "Вакансия: менеджер по продажам",
    "Скидка 20% на все товары до конца месяца",
    "Новое поступление товаров",
    "Аренда складских помещений",
    "Поиск инвесторов для развития бизнеса"
]

ANNOUNCEMENT_CONTENTS = [
    "Мы ищем надежных поставщиков для долгосрочного сотрудничества. Готовы рассмотреть различные варианты сотрудничества.",
    "Продаем современное оборудование в отличном состоянии. Все документы в порядке, возможна доставка.",
    "Предлагаем комплексные логистические услуги по всей России. Конкурентоспособные цены, надежная доставка.",
    "Ищем партнеров для реализации совместных проектов. Готовы к взаимовыгодному сотрудничеству.",
    "Объявляем открытый тендер на выполнение строительных работ. Условия участия уточняйте по телефону.",
    "В нашу команду требуется опытный менеджер по продажам. Официальное трудоустройство, достойная зарплата.",
    "Специальное предложение! Скидка 20% на весь ассортимент товаров. Акция действует до конца месяца.",
    "В нашем магазине новое поступление товаров от ведущих производителей. Приходите, выбирайте!",
    "Сдаем в аренду складские помещения различной площади. Удобное расположение, хорошие условия.",
    "Ищем инвесторов для развития перспективного бизнеса. Подробная презентация проекта по запросу."
]


class DatabaseSeeder:
    def __init__(self):
        self.session = None
        self.users = []
        self.companies = []
        self.products = []
        self.services = []
        self.announcements = []

    async def seed(self):
        """Основной метод для заполнения базы данных"""
        async with AsyncSessionLocal() as session:
            self.session = session
            
            print("🧹 Очистка существующих данных...")
            await self._clear_database()
            
            print("👥 Создание пользователей...")
            await self._create_users()
            
            print("🏢 Создание компаний...")
            await self._create_companies()
            
            print("📦 Создание товаров...")
            await self._create_products()
            
            print("🔧 Создание услуг...")
            await self._create_services()
            
            print("📢 Создание объявлений...")
            await self._create_announcements()
            
            await session.commit()
            print("✅ Тестовые данные успешно добавлены!")
            self._print_statistics()

    async def _clear_database(self):
        """Очистка базы данных от существующих данных"""
        # Удаляем в правильном порядке (сначала зависимые таблицы)
        tables = [
            "announcements", "products", "company_officials", 
            "company_relations", "chat_participants", "messages", 
            "companies", "users"
        ]
        
        for table in tables:
            await self.session.execute(text(f"DELETE FROM {table}"))
        
        await self.session.commit()

    async def _create_users(self):
        """Создание пользователей"""
        for i in range(1, 51):  # 50 пользователей
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
            
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                patronymic=random.choice(FIRST_NAMES) + "ович" if random.choice([True, False]) else None,
                phone=f"+7 9{random.randint(10, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
                inn=f"{random.randint(1000000000, 9999999999)}",
                position=random.choice(POSITIONS),
                hashed_password=bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=True
            )
            self.session.add(user)
            self.users.append(user)
        
        await self.session.flush()

    async def _create_companies(self):
        """Создание компаний"""
        for i, user in enumerate(self.users, 1):
            city = random.choice(RUSSIAN_CITIES)
            region = random.choice(RUSSIAN_REGIONS)
            federal_district = random.choice(FEDERAL_DISTRICTS)
            activity = random.choice(BUSINESS_ACTIVITIES)
            
            # Генерируем уникальные ИНН и ОГРН
            inn = f"{random.randint(1000000000, 9999999999)}"
            ogrn = f"{random.randint(1000000000000, 9999999999999)}"
            kpp = f"{random.randint(100000000, 999999999)}"
            
            company = Company(
                name=f"{activity} '{random.choice(['Альфа', 'Бета', 'Гамма', 'Дельта', 'Омега', 'Сигма'])}'",
                slug=f"company-{i}-{random.randint(1000, 9999)}",
                logo=None,
                type=random.choice(COMPANY_TYPES),
                trade_activity=random.choice(list(TradeActivity)),
                business_type=random.choice(list(BusinessType)),
                activity_type=activity,
                description=f"Мы специализируемся на {activity.lower()}. Наша компания работает на рынке уже {random.randint(1, 20)} лет и зарекомендовала себя как надежный партнер.",
                country="Россия",
                federal_district=federal_district,
                region=region,
                city=city,
                full_name=f"{random.choice(COMPANY_TYPES)} '{activity} {random.choice(['Альфа', 'Бета', 'Гамма', 'Дельта', 'Омега', 'Сигма'])}'",
                inn=inn,
                ogrn=ogrn,
                kpp=kpp,
                registration_date=datetime.now() - timedelta(days=random.randint(100, 5000)),
                legal_address=f"{city}, ул. {random.choice(['Ленина', 'Пушкина', 'Гагарина', 'Мира', 'Советская'])} {random.randint(1, 200)}",
                production_address=f"{city}, пр. {random.choice(['Промышленный', 'Заводской', 'Технический'])} {random.randint(1, 50)}" if random.choice([True, False]) else None,
                phone=f"+7 9{random.randint(10, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
                email=f"info@company{i}.ru",
                website=f"www.company{i}.ru" if random.choice([True, False]) else None,
                total_views=random.randint(0, 10000),
                monthly_views=random.randint(0, 1000),
                total_purchases=random.randint(0, 500),
                user_id=user.id,
                is_active=True
            )
            self.session.add(company)
            self.companies.append(company)
        
        await self.session.flush()

    async def _create_products(self):
        """Создание товаров"""
        product_id = 1
        for category, products in PRODUCT_NAMES.items():
            if category in ["Мебель", "Электроника", "Одежда", "Продукты питания"]:
                for product_name in products:
                    for _ in range(random.randint(2, 5)):  # 2-5 вариантов каждого товара
                        company = random.choice(self.companies)
                        characteristics = self._generate_characteristics(category)
                        
                        product = Product(
                            name=f"{product_name} {random.choice(['Премиум', 'Стандарт', 'Эконом', 'Люкс'])}",
                            slug=f"product-{product_id}",
                            description=f"Качественный {product_name.lower()}. {self._generate_product_description(product_name)}",
                            article=f"P{product_id:06}",
                            type=ProductType.GOOD,
                            price=round(random.uniform(100, 50000), 2),
                            images=[],
                            characteristics=characteristics,
                            is_hidden=False,
                            is_deleted=False,
                            unit_of_measurement=random.choice(["шт", "кг", "м", "л", "упак"]),
                            company_id=company.id
                        )
                        self.session.add(product)
                        self.products.append(product)
                        product_id += 1

    async def _create_services(self):
        """Создание услуг"""
        service_id = 1
        for category, services in PRODUCT_NAMES.items():
            if category in ["IT-услуги", "Консалтинг", "Образование"]:
                for service_name in services:
                    for _ in range(random.randint(1, 3)):  # 1-3 варианта каждой услуги
                        company = random.choice(self.companies)
                        characteristics = self._generate_characteristics(category)
                        
                        service = Product(
                            name=f"{service_name} {random.choice(['Профессиональный', 'Экспертный', 'Базовый', 'Премиум'])}",
                            slug=f"service-{service_id}",
                            description=f"Профессиональные услуги: {service_name.lower()}. {self._generate_service_description(service_name)}",
                            article=f"S{service_id:06}",
                            type=ProductType.SERVICE,
                            price=round(random.uniform(1000, 100000), 2),
                            images=[],
                            characteristics=characteristics,
                            is_hidden=False,
                            is_deleted=False,
                            unit_of_measurement=random.choice(["час", "день", "месяц", "проект", "усл"]),
                            company_id=company.id
                        )
                        self.session.add(service)
                        self.services.append(service)
                        service_id += 1

    async def _create_announcements(self):
        """Создание объявлений"""
        for i in range(1, 201):  # 200 объявлений
            company = random.choice(self.companies)
            category = random.choice(ANNOUNCEMENT_CATEGORIES)
            title = random.choice(ANNOUNCEMENT_TITLES)
            content = random.choice(ANNOUNCEMENT_CONTENTS)
            
            announcement = Announcement(
                title=f"{title} #{i}",
                content=f"{content} Подробности уточняйте по телефону: {company.phone}",
                category=category,
                images=[],
                published=random.choice([True, True, True, False]),  # 75% опубликованных
                company_id=company.id
            )
            self.session.add(announcement)
            self.announcements.append(announcement)

    def _generate_characteristics(self, category: str) -> List[Dict[str, str]]:
        """Генерация характеристик для товара/услуги"""
        if category not in CHARACTERISTICS_TEMPLATES:
            return []
        
        characteristics = []
        for template in CHARACTERISTICS_TEMPLATES[category]:
            if isinstance(template["value"], list):
                value = random.choice(template["value"])
            else:
                value = template["value"]
            characteristics.append({"key": template["key"], "value": value})
        
        return characteristics

    def _generate_product_description(self, product_name: str) -> str:
        """Генерация описания товара"""
        descriptions = [
            "Изготовлен из качественных материалов с соблюдением всех стандартов.",
            "Современный дизайн и отличное качество исполнения.",
            "Подходит для использования в домашних и офисных условиях.",
            "Долговечный и надежный товар от проверенного производителя.",
            "Экологически чистые материалы, безопасные для здоровья."
        ]
        return random.choice(descriptions)

    def _generate_service_description(self, service_name: str) -> str:
        """Генерация описания услуги"""
        descriptions = [
            "Выполняем работы любой сложности с гарантией качества.",
            "Опытные специалисты с многолетним стажем работы.",
            "Индивидуальный подход к каждому клиенту.",
            "Современные технологии и методы работы.",
            "Полное сопровождение проекта от начала до конца."
        ]
        return random.choice(descriptions)

    def _print_statistics(self):
        """Вывод статистики созданных данных"""
        print("\n📊 Статистика созданных данных:")
        print(f"👥 Пользователей: {len(self.users)}")
        print(f"🏢 Компаний: {len(self.companies)}")
        print(f"📦 Товаров: {len(self.products)}")
        print(f"🔧 Услуг: {len(self.services)}")
        print(f"📢 Объявлений: {len(self.announcements)}")
        print(f"📈 Всего продуктов: {len(self.products) + len(self.services)}")


async def main():
    """Главная функция"""
    print("🚀 Запуск скрипта заполнения базы данных тестовыми данными...")
    seeder = DatabaseSeeder()
    await seeder.seed()
    print("🎉 Готово!")


if __name__ == "__main__":
    asyncio.run(main())
