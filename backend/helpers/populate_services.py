#!/usr/bin/env python3
"""
Скрипт для создания только тестовых сервисов
"""

import asyncio
import asyncpg
import os
import random
from typing import List, Dict, Any
import logging
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Тестовые данные для сервисов
SERVICES_DATA = [
    # IT-услуги
    {"name": "Разработка веб-сайтов", "category": "IT-услуги", "description": "Создание современных веб-сайтов и веб-приложений", "price_range": (50000, 500000)},
    {"name": "Разработка мобильных приложений", "category": "IT-услуги", "description": "Создание iOS и Android приложений", "price_range": (100000, 1000000)},
    {"name": "Системное администрирование", "category": "IT-услуги", "description": "Настройка и поддержка IT-инфраструктуры", "price_range": (30000, 150000)},
    {"name": "Кибербезопасность", "category": "IT-услуги", "description": "Аудит безопасности и защита данных", "price_range": (80000, 300000)},
    {"name": "Облачные решения", "category": "IT-услуги", "description": "Миграция в облако и облачная инфраструктура", "price_range": (50000, 200000)},
    
    # Консалтинг
    {"name": "Бизнес-консалтинг", "category": "Консалтинг", "description": "Стратегическое планирование и оптимизация бизнес-процессов", "price_range": (100000, 500000)},
    {"name": "Финансовый консалтинг", "category": "Консалтинг", "description": "Финансовое планирование и инвестиционные стратегии", "price_range": (80000, 400000)},
    {"name": "HR-консалтинг", "category": "Консалтинг", "description": "Управление персоналом и организационное развитие", "price_range": (50000, 200000)},
    {"name": "Маркетинговый консалтинг", "category": "Консалтинг", "description": "Стратегии маркетинга и продвижения", "price_range": (60000, 300000)},
    {"name": "Управленческий консалтинг", "category": "Консалтинг", "description": "Оптимизация управления и повышение эффективности", "price_range": (70000, 350000)},
    
    # Образование
    {"name": "Корпоративное обучение", "category": "Образование", "description": "Обучение сотрудников и повышение квалификации", "price_range": (20000, 100000)},
    {"name": "Онлайн-курсы", "category": "Образование", "description": "Разработка и проведение онлайн-обучения", "price_range": (30000, 150000)},
    {"name": "Языковые курсы", "category": "Образование", "description": "Обучение иностранным языкам", "price_range": (15000, 80000)},
    {"name": "Профессиональная переподготовка", "category": "Образование", "description": "Получение новых профессиональных навыков", "price_range": (40000, 200000)},
    {"name": "IT-обучение", "category": "Образование", "description": "Обучение программированию и IT-технологиям", "price_range": (25000, 120000)},
    
    # Медицинские услуги
    {"name": "Медицинские консультации", "category": "Медицинские услуги", "description": "Консультации врачей различных специальностей", "price_range": (2000, 10000)},
    {"name": "Диагностические услуги", "category": "Медицинские услуги", "description": "Лабораторная и инструментальная диагностика", "price_range": (5000, 50000)},
    {"name": "Стоматологические услуги", "category": "Медицинские услуги", "description": "Лечение и протезирование зубов", "price_range": (3000, 100000)},
    {"name": "Косметологические услуги", "category": "Медицинские услуги", "description": "Эстетическая медицина и косметология", "price_range": (5000, 200000)},
    {"name": "Реабилитационные услуги", "category": "Медицинские услуги", "description": "Восстановительное лечение и реабилитация", "price_range": (10000, 100000)},
    
    # Юридические услуги
    {"name": "Юридические консультации", "category": "Юридические услуги", "description": "Консультации по правовым вопросам", "price_range": (5000, 50000)},
    {"name": "Представительство в суде", "category": "Юридические услуги", "description": "Ведение дел в судебных инстанциях", "price_range": (30000, 200000)},
    {"name": "Корпоративное право", "category": "Юридические услуги", "description": "Правовое сопровождение бизнеса", "price_range": (20000, 150000)},
    {"name": "Налоговое планирование", "category": "Юридические услуги", "description": "Оптимизация налогообложения", "price_range": (15000, 100000)},
    {"name": "Регистрация бизнеса", "category": "Юридические услуги", "description": "Создание и регистрация компаний", "price_range": (10000, 50000)},
    
    # Логистика
    {"name": "Грузоперевозки", "category": "Логистика", "description": "Транспортировка грузов по России и СНГ", "price_range": (20000, 200000)},
    {"name": "Складские услуги", "category": "Логистика", "description": "Хранение и обработка товаров", "price_range": (10000, 100000)},
    {"name": "Таможенное оформление", "category": "Логистика", "description": "Оформление таможенных документов", "price_range": (5000, 50000)},
    {"name": "Курьерские услуги", "category": "Логистика", "description": "Доставка документов и посылок", "price_range": (1000, 10000)},
    {"name": "Логистическое планирование", "category": "Логистика", "description": "Оптимизация цепочек поставок", "price_range": (30000, 150000)},
    
    # Ремонт и обслуживание
    {"name": "Ремонт компьютеров", "category": "Ремонт", "description": "Диагностика и ремонт компьютерной техники", "price_range": (2000, 20000)},
    {"name": "Ремонт бытовой техники", "category": "Ремонт", "description": "Восстановление бытовых приборов", "price_range": (3000, 30000)},
    {"name": "Автосервис", "category": "Ремонт", "description": "Техническое обслуживание автомобилей", "price_range": (5000, 100000)},
    {"name": "Ремонт мебели", "category": "Ремонт", "description": "Восстановление и реставрация мебели", "price_range": (2000, 50000)},
    {"name": "Ремонт одежды", "category": "Ремонт", "description": "Пошив и ремонт одежды", "price_range": (1000, 15000)},
    
    # Дизайн
    {"name": "Графический дизайн", "category": "Дизайн", "description": "Создание логотипов, брендинг, полиграфия", "price_range": (10000, 100000)},
    {"name": "Веб-дизайн", "category": "Дизайн", "description": "Дизайн веб-сайтов и интерфейсов", "price_range": (15000, 150000)},
    {"name": "Интерьерный дизайн", "category": "Дизайн", "description": "Проектирование интерьеров", "price_range": (30000, 300000)},
    {"name": "Ландшафтный дизайн", "category": "Дизайн", "description": "Проектирование садов и парков", "price_range": (20000, 200000)},
    {"name": "Дизайн одежды", "category": "Дизайн", "description": "Создание коллекций одежды", "price_range": (25000, 250000)},
    
    # Маркетинг
    {"name": "SMM-продвижение", "category": "Маркетинг", "description": "Продвижение в социальных сетях", "price_range": (20000, 100000)},
    {"name": "Контекстная реклама", "category": "Маркетинг", "description": "Настройка и ведение рекламных кампаний", "price_range": (15000, 150000)},
    {"name": "SEO-оптимизация", "category": "Маркетинг", "description": "Продвижение сайтов в поисковых системах", "price_range": (25000, 200000)},
    {"name": "Email-маркетинг", "category": "Маркетинг", "description": "Email-рассылки и автоматизация", "price_range": (10000, 80000)},
    {"name": "Аналитика и отчетность", "category": "Маркетинг", "description": "Анализ эффективности маркетинга", "price_range": (15000, 100000)},
    
    # Бухгалтерские услуги
    {"name": "Ведение бухгалтерии", "category": "Бухгалтерские услуги", "description": "Полное ведение учета и отчетности", "price_range": (15000, 100000)},
    {"name": "Налоговая отчетность", "category": "Бухгалтерские услуги", "description": "Подготовка и сдача налоговых деклараций", "price_range": (5000, 50000)},
    {"name": "Аудиторские услуги", "category": "Бухгалтерские услуги", "description": "Проведение аудита и консультации", "price_range": (30000, 200000)},
    {"name": "Зарплатное обслуживание", "category": "Бухгалтерские услуги", "description": "Расчет и выплата заработной платы", "price_range": (10000, 80000)},
    {"name": "Консультации по налогам", "category": "Бухгалтерские услуги", "description": "Налоговое планирование и оптимизация", "price_range": (8000, 60000)},
    
    # Строительство
    {"name": "Строительство домов", "category": "Строительство", "description": "Возведение жилых домов под ключ", "price_range": (2000000, 20000000)},
    {"name": "Ремонт квартир", "category": "Строительство", "description": "Комплексный ремонт жилых помещений", "price_range": (100000, 2000000)},
    {"name": "Отделочные работы", "category": "Строительство", "description": "Внутренняя отделка помещений", "price_range": (50000, 1000000)},
    {"name": "Электромонтажные работы", "category": "Строительство", "description": "Установка и подключение электрооборудования", "price_range": (20000, 300000)},
    {"name": "Сантехнические работы", "category": "Строительство", "description": "Установка и ремонт сантехники", "price_range": (15000, 200000)},
    
    # Красота и здоровье
    {"name": "Парикмахерские услуги", "category": "Красота и здоровье", "description": "Стрижки, окрашивание, укладки", "price_range": (1000, 10000)},
    {"name": "Маникюр и педикюр", "category": "Красота и здоровье", "description": "Уход за ногтями рук и ног", "price_range": (2000, 15000)},
    {"name": "Массаж", "category": "Красота и здоровье", "description": "Лечебный и расслабляющий массаж", "price_range": (3000, 20000)},
    {"name": "Солярий", "category": "Красота и здоровье", "description": "Искусственный загар", "price_range": (500, 5000)},
    {"name": "Фитнес-тренировки", "category": "Красота и здоровье", "description": "Персональные тренировки", "price_range": (2000, 15000)},
    
    # Туризм
    {"name": "Организация туров", "category": "Туризм", "description": "Планирование и организация путешествий", "price_range": (10000, 200000)},
    {"name": "Бронирование отелей", "category": "Туризм", "description": "Поиск и бронирование размещения", "price_range": (5000, 100000)},
    {"name": "Авиабилеты", "category": "Туризм", "description": "Поиск и бронирование авиаперелетов", "price_range": (3000, 150000)},
    {"name": "Экскурсионные услуги", "category": "Туризм", "description": "Проведение экскурсий и туров", "price_range": (2000, 50000)},
    {"name": "Визовая поддержка", "category": "Туризм", "description": "Помощь в получении виз", "price_range": (5000, 50000)},
    
    # Финансовые услуги
    {"name": "Кредитование", "category": "Финансовые услуги", "description": "Выдача кредитов физическим и юридическим лицам", "price_range": (100000, 50000000)},
    {"name": "Страхование", "category": "Финансовые услуги", "description": "Страхование имущества и жизни", "price_range": (5000, 500000)},
    {"name": "Инвестиционные услуги", "category": "Финансовые услуги", "description": "Управление инвестициями и портфелями", "price_range": (50000, 1000000)},
    {"name": "Лизинг", "category": "Финансовые услуги", "description": "Лизинговые услуги для бизнеса", "price_range": (100000, 10000000)},
    {"name": "Факторинг", "category": "Финансовые услуги", "description": "Финансирование дебиторской задолженности", "price_range": (50000, 5000000)},
]


class ServicesPopulator:
    def __init__(self):
        self.connection = None
        
    async def connect(self):
        """Подключение к базе данных"""
        database_url = os.getenv("SQLALCHEMY_DATABASE_URL", "postgresql://postgres:postgres@localhost/postgres")
        self.connection = await asyncpg.connect(database_url)
        logger.info("Подключение к базе данных установлено")
        
    async def disconnect(self):
        """Отключение от базы данных"""
        if self.connection:
            await self.connection.close()
            logger.info("Соединение с базой данных закрыто")
    
    async def get_companies_by_activity(self, activity):
        """Получение компаний по виду деятельности"""
        result = await self.connection.fetch("""
            SELECT id, name, activity_type 
            FROM companies 
            WHERE activity_type = $1 AND is_active = true
        """, activity)
        return result
    
    async def create_test_services(self):
        """Создание тестовых сервисов"""
        logger.info("Создание тестовых сервисов...")
        
        created_services = []
        service_id = 1
        
        for service_data in SERVICES_DATA:
            # Находим компании, которые занимаются этой категорией услуг
            companies = await self.get_companies_by_activity(service_data['category'])
            
            if not companies:
                logger.warning(f"Нет компаний для категории: {service_data['category']}")
                continue
            
            # Создаем 1-3 варианта каждой услуги
            for _ in range(random.randint(1, 3)):
                company = random.choice(companies)
                
                # Генерируем характеристики
                characteristics = {
                    "Срок выполнения": f"{random.randint(1, 30)} дней",
                    "Гарантия": f"{random.randint(6, 24)} месяцев",
                    "Поддержка": "24/7" if random.choice([True, False]) else "Рабочие дни",
                    "Опыт": f"{random.randint(2, 15)} лет"
                }
                
                # Генерируем цену
                price_min, price_max = service_data['price_range']
                price = round(random.uniform(price_min, price_max), 2)
                
                # Генерируем артикул
                article = f"S{service_id:06}"
                
                # Создаем сервис
                product_id = await self.connection.fetchval("""
                    INSERT INTO products (
                        name, slug, description, article, type, price, images, characteristics,
                        is_hidden, is_deleted, unit_of_measurement, company_id, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW(), NOW())
                    RETURNING id
                """,
                    f"{service_data['name']} {random.choice(['Профессиональный', 'Экспертный', 'Базовый', 'Премиум'])}",
                    f"service-{service_id}",
                    f"{service_data['description']}. Качественное выполнение работ с гарантией результата.",
                    article,
                    "SERVICE",
                    price,
                    "[]",  # images
                    json.dumps(characteristics),  # characteristics
                    False,  # is_hidden
                    False,  # is_deleted
                    random.choice(["час", "день", "месяц", "проект", "усл"]),
                    company['id']
                )
                
                created_services.append({
                    'id': product_id,
                    'name': service_data['name'],
                    'company_id': company['id'],
                    'price': price
                })
                
                logger.info(f"Создан сервис: {service_data['name']} для компании {company['name']} (ID: {product_id})")
                service_id += 1
        
        logger.info(f"Создано {len(created_services)} сервисов")
        return created_services
    
    async def populate_all(self):
        """Заполнение всех тестовых данных"""
        try:
            await self.connect()
            
            # Создаем сервисы
            services = await self.create_test_services()
            
            logger.info("Тестовые сервисы успешно созданы!")
            logger.info(f"Всего создано: {len(services)} сервисов")
            
        except Exception as e:
            logger.error(f"Ошибка при создании тестовых сервисов: {e}")
            raise
        finally:
            await self.disconnect()


async def main():
    """Основная функция"""
    populator = ServicesPopulator()
    await populator.populate_all()


if __name__ == "__main__":
    asyncio.run(main())
