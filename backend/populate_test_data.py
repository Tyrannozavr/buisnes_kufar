#!/usr/bin/env python3
"""
Скрипт для создания тестовых сервисов и компаний
"""

import asyncio
import asyncpg
import os
import random
from typing import List, Dict, Any
import logging
from datetime import datetime

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

# Тестовые компании
COMPANIES_DATA = [
    # IT-компании
    {"name": "ТехноСофт", "type": "ООО", "activity": "IT-услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Разработка программного обеспечения и IT-консалтинг"},
    {"name": "ВебСтудия Про", "type": "ООО", "activity": "IT-услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Создание веб-сайтов и мобильных приложений"},
    {"name": "КиберГарант", "type": "ООО", "activity": "IT-услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Информационная безопасность и защита данных"},
    {"name": "ОблакоТех", "type": "ООО", "activity": "IT-услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Облачные решения и миграция данных"},
    {"name": "ДевЛаб", "type": "ИП", "activity": "IT-услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Разработка мобильных приложений и веб-сервисов"},
    
    # Консалтинговые компании
    {"name": "БизнесКонсалт", "type": "ООО", "activity": "Консалтинг", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Стратегический консалтинг и управленческое консультирование"},
    {"name": "ФинансЭксперт", "type": "ООО", "activity": "Консалтинг", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Финансовое планирование и инвестиционные стратегии"},
    {"name": "HR-Партнер", "type": "ООО", "activity": "Консалтинг", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Управление персоналом и HR-консалтинг"},
    {"name": "МаркетПромо", "type": "ООО", "activity": "Консалтинг", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Маркетинговые стратегии и продвижение"},
    {"name": "Оптимизация+", "type": "ИП", "activity": "Консалтинг", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Оптимизация бизнес-процессов и повышение эффективности"},
    
    # Образовательные компании
    {"name": "Академия Профи", "type": "ООО", "activity": "Образование", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Корпоративное обучение и профессиональная переподготовка"},
    {"name": "ОнлайнШкола", "type": "ООО", "activity": "Образование", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Онлайн-курсы и дистанционное обучение"},
    {"name": "ЛингваЦентр", "type": "ООО", "activity": "Образование", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Языковые курсы и обучение иностранным языкам"},
    {"name": "IT-Академия", "type": "ООО", "activity": "Образование", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Обучение программированию и IT-технологиям"},
    {"name": "СкиллХаус", "type": "ИП", "activity": "Образование", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Развитие профессиональных навыков и компетенций"},
    
    # Медицинские компании
    {"name": "МедКонсалт", "type": "ООО", "activity": "Медицинские услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Медицинские консультации и диагностические услуги"},
    {"name": "СтоматКлиник", "type": "ООО", "activity": "Медицинские услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Стоматологические услуги и лечение зубов"},
    {"name": "Красота+", "type": "ООО", "activity": "Медицинские услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Косметологические услуги и эстетическая медицина"},
    {"name": "РеабилитЦентр", "type": "ООО", "activity": "Медицинские услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Восстановительное лечение и реабилитация"},
    {"name": "ДиагностикПро", "type": "ИП", "activity": "Медицинские услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Лабораторная и инструментальная диагностика"},
    
    # Юридические компании
    {"name": "ПравоГарант", "type": "ООО", "activity": "Юридические услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Юридические консультации и представительство в суде"},
    {"name": "КорпПраво", "type": "ООО", "activity": "Юридические услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Корпоративное право и правовое сопровождение бизнеса"},
    {"name": "НалогОптима", "type": "ООО", "activity": "Юридические услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Налоговое планирование и оптимизация"},
    {"name": "РегистрБизнес", "type": "ООО", "activity": "Юридические услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Регистрация бизнеса и корпоративные услуги"},
    {"name": "ЮрКонсалт", "type": "ИП", "activity": "Юридические услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Юридические консультации по всем вопросам"},
    
    # Логистические компании
    {"name": "ТрансЛогик", "type": "ООО", "activity": "Логистика", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Грузоперевозки и логистические услуги"},
    {"name": "СкладПро", "type": "ООО", "activity": "Логистика", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Складские услуги и обработка грузов"},
    {"name": "Таможня+", "type": "ООО", "activity": "Логистика", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Таможенное оформление и сопровождение"},
    {"name": "КурьерЭкспресс", "type": "ООО", "activity": "Логистика", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Курьерские услуги и доставка"},
    {"name": "ЛогистОптима", "type": "ИП", "activity": "Логистика", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Логистическое планирование и оптимизация"},
    
    # Ремонтные компании
    {"name": "КомпьютерМастер", "type": "ООО", "activity": "Ремонт", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Ремонт компьютеров и компьютерной техники"},
    {"name": "БытТехСервис", "type": "ООО", "activity": "Ремонт", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Ремонт бытовой техники и электроники"},
    {"name": "АвтоСервис+", "type": "ООО", "activity": "Ремонт", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Техническое обслуживание и ремонт автомобилей"},
    {"name": "МебельМастер", "type": "ООО", "activity": "Ремонт", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Ремонт и реставрация мебели"},
    {"name": "АтельеШитье", "type": "ИП", "activity": "Ремонт", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Пошив и ремонт одежды"},
    
    # Дизайнерские компании
    {"name": "ДизайнСтудия", "type": "ООО", "activity": "Дизайн", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Графический дизайн и брендинг"},
    {"name": "ВебДизайнПро", "type": "ООО", "activity": "Дизайн", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Веб-дизайн и UI/UX разработка"},
    {"name": "ИнтерьерСтудия", "type": "ООО", "activity": "Дизайн", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Интерьерный дизайн и проектирование"},
    {"name": "ЛандшафтПро", "type": "ООО", "activity": "Дизайн", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Ландшафтный дизайн и озеленение"},
    {"name": "МодаДизайн", "type": "ИП", "activity": "Дизайн", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Дизайн одежды и создание коллекций"},
    
    # Маркетинговые компании
    {"name": "МаркетПромо", "type": "ООО", "activity": "Маркетинг", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "SMM-продвижение и социальные сети"},
    {"name": "КонтекстПро", "type": "ООО", "activity": "Маркетинг", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Контекстная реклама и Google Ads"},
    {"name": "SEOМастер", "type": "ООО", "activity": "Маркетинг", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "SEO-оптимизация и продвижение сайтов"},
    {"name": "EmailМаркет", "type": "ООО", "activity": "Маркетинг", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Email-маркетинг и автоматизация"},
    {"name": "АналитикаПро", "type": "ИП", "activity": "Маркетинг", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Аналитика и отчетность по маркетингу"},
    
    # Бухгалтерские компании
    {"name": "БухУчет+", "type": "ООО", "activity": "Бухгалтерские услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Ведение бухгалтерии и учет"},
    {"name": "НалогОтчет", "type": "ООО", "activity": "Бухгалтерские услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Налоговая отчетность и декларации"},
    {"name": "АудитПро", "type": "ООО", "activity": "Бухгалтерские услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Аудиторские услуги и консультации"},
    {"name": "ЗарплатаСервис", "type": "ООО", "activity": "Бухгалтерские услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Зарплатное обслуживание и расчеты"},
    {"name": "НалогКонсалт", "type": "ИП", "activity": "Бухгалтерские услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Консультации по налогам и оптимизация"},
    
    # Строительные компании
    {"name": "СтройДом", "type": "ООО", "activity": "Строительство", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Строительство домов под ключ"},
    {"name": "РемонтКвартир", "type": "ООО", "activity": "Строительство", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Комплексный ремонт квартир"},
    {"name": "ОтделкаПро", "type": "ООО", "activity": "Строительство", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Отделочные работы и дизайн"},
    {"name": "ЭлектроМонтаж", "type": "ООО", "activity": "Строительство", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Электромонтажные работы"},
    {"name": "СантехПро", "type": "ИП", "activity": "Строительство", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Сантехнические работы и установка"},
    
    # Красота и здоровье
    {"name": "СалонКрасоты", "type": "ООО", "activity": "Красота и здоровье", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Парикмахерские услуги и маникюр"},
    {"name": "МаникюрСтудия", "type": "ООО", "activity": "Красота и здоровье", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Маникюр, педикюр и уход за ногтями"},
    {"name": "МассажЦентр", "type": "ООО", "activity": "Красота и здоровье", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Лечебный и расслабляющий массаж"},
    {"name": "СолярийСтудия", "type": "ООО", "activity": "Красота и здоровье", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Искусственный загар и солярий"},
    {"name": "ФитнесТренер", "type": "ИП", "activity": "Красота и здоровье", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Персональные тренировки и фитнес"},
    
    # Туристические компании
    {"name": "ТурАгентство", "type": "ООО", "activity": "Туризм", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Организация туров и путешествий"},
    {"name": "ОтельБронинг", "type": "ООО", "activity": "Туризм", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Бронирование отелей и размещения"},
    {"name": "АвиаБилеты", "type": "ООО", "activity": "Туризм", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Поиск и бронирование авиабилетов"},
    {"name": "ЭкскурсииПро", "type": "ООО", "activity": "Туризм", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Экскурсионные услуги и туры"},
    {"name": "ВизыСервис", "type": "ИП", "activity": "Туризм", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Визовая поддержка и документы"},
    
    # Финансовые компании
    {"name": "КредитБанк", "type": "ООО", "activity": "Финансовые услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Кредитование физических и юридических лиц"},
    {"name": "Страхование+", "type": "ООО", "activity": "Финансовые услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Страхование имущества и жизни"},
    {"name": "ИнвестПро", "type": "ООО", "activity": "Финансовые услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Инвестиционные услуги и управление"},
    {"name": "ЛизингСервис", "type": "ООО", "activity": "Финансовые услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Лизинговые услуги для бизнеса"},
    {"name": "ФакторингПро", "type": "ИП", "activity": "Финансовые услуги", "business_type": "SERVICES", "trade_activity": "SELLER", "description": "Факторинг и финансирование"},
]


class TestDataPopulator:
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
    
    async def get_random_city(self):
        """Получение случайного города"""
        result = await self.connection.fetchrow("""
            SELECT id, name, region_id, federal_district_id, country_id 
            FROM cities 
            WHERE is_active = true 
            ORDER BY RANDOM() 
            LIMIT 1
        """)
        return result
    
    async def get_random_region(self):
        """Получение случайного региона"""
        result = await self.connection.fetchrow("""
            SELECT id, name, federal_district_id, country_id 
            FROM regions 
            WHERE is_active = true 
            ORDER BY RANDOM() 
            LIMIT 1
        """)
        return result
    
    async def get_random_federal_district(self):
        """Получение случайного федерального округа"""
        result = await self.connection.fetchrow("""
            SELECT id, name, country_id 
            FROM federal_districts 
            WHERE is_active = true 
            ORDER BY RANDOM() 
            LIMIT 1
        """)
        return result
    
    async def create_test_companies(self):
        """Создание тестовых компаний"""
        logger.info("Создание тестовых компаний...")
        
        created_companies = []
        
        for i, company_data in enumerate(COMPANIES_DATA):
            # Получаем случайные локации
            city = await self.get_random_city()
            region = await self.get_random_region()
            federal_district = await self.get_random_federal_district()
            
            # Генерируем slug
            slug = f"{company_data['name'].lower().replace(' ', '-').replace('+', 'plus')}-{i+1}"
            
            # Создаем компанию
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
                company_data['name'],
                slug,
                company_data['type'],
                company_data['trade_activity'],
                company_data['business_type'],
                company_data['activity'],
                company_data['description'],
                "Российская Федерация",
                federal_district['name'],
                region['name'],
                city['name'],
                1,  # country_id для России
                federal_district['id'],
                region['id'],
                city['id'],
                f"{company_data['type']} \"{company_data['name']}\"",  # full_name
                f"{random.randint(1000000000, 9999999999)}",  # inn
                f"{random.randint(1000000000000, 9999999999999)}",  # ogrn
                f"{random.randint(100000000, 999999999)}",  # kpp
                datetime.now(),  # registration_date
                f"{city['name']}, ул. Примерная, д. {random.randint(1, 100)}",  # legal_address
                f"{city['name']}, ул. Производственная, д. {random.randint(1, 100)}",  # production_address
                f"+7 ({random.randint(900, 999)}) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",  # phone
                f"info@{slug}.ru",  # email
                f"https://{slug}.ru",  # website
                0,  # total_views
                0,  # monthly_views
                0,  # total_purchases
                1,  # user_id (предполагаем, что есть пользователь с ID 1)
                True
            )
            
            created_companies.append({
                'id': company_id,
                'name': company_data['name'],
                'activity': company_data['activity']
            })
            
            logger.info(f"Создана компания: {company_data['name']} (ID: {company_id})")
        
        logger.info(f"Создано {len(created_companies)} компаний")
        return created_companies
    
    async def create_test_services(self, companies):
        """Создание тестовых сервисов"""
        logger.info("Создание тестовых сервисов...")
        
        created_services = []
        service_id = 1
        
        for service_data in SERVICES_DATA:
            # Находим компании, которые занимаются этой категорией услуг
            suitable_companies = [c for c in companies if c['activity'] == service_data['category']]
            
            if not suitable_companies:
                # Если нет подходящих компаний, берем случайную
                suitable_companies = [random.choice(companies)]
            
            # Создаем 1-3 варианта каждой услуги
            for _ in range(random.randint(1, 3)):
                company = random.choice(suitable_companies)
                
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
                    characteristics,
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
            
            # Создаем компании
            companies = await self.create_test_companies()
            
            # Создаем сервисы
            services = await self.create_test_services(companies)
            
            logger.info("Тестовые данные успешно созданы!")
            logger.info(f"Всего создано: {len(companies)} компаний, {len(services)} сервисов")
            
        except Exception as e:
            logger.error(f"Ошибка при создании тестовых данных: {e}")
            raise
        finally:
            await self.disconnect()


async def main():
    """Основная функция"""
    populator = TestDataPopulator()
    await populator.populate_all()


if __name__ == "__main__":
    asyncio.run(main())
