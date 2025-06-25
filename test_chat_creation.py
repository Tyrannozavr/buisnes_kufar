#!/usr/bin/env python3
"""
Тест для проверки логики создания чатов
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Импорты для тестирования
from app.api.chats.services.chat_service import ChatService
from app.api.chats.schemas.chat import ChatCreate
from app.api.authentication.models import User
from app.api.company.models.company import Company

# Настройка подключения к базе данных (замените на ваши параметры)
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

async def test_chat_creation():
    """Тестирует создание чата с правильными участниками"""
    
    # Создаем подключение к базе данных
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Создаем тестовых пользователей
        user1 = User(
            email="user1@test.com",
            first_name="User",
            last_name="One",
            hashed_password="hashed_password"
        )
        user2 = User(
            email="user2@test.com", 
            first_name="User",
            last_name="Two",
            hashed_password="hashed_password"
        )
        
        db.add(user1)
        db.add(user2)
        await db.commit()
        await db.refresh(user1)
        await db.refresh(user2)
        
        # Создаем тестовые компании
        company1 = Company(
            name="Company One",
            slug="company-one",
            user_id=user1.id,
            type="ООО",
            trade_activity="SELLER",
            business_type="GOODS",
            activity_type="Производство",
            country="Россия",
            federal_district="Центральный",
            region="Московская область",
            city="Москва",
            full_name="ООО Компания Один",
            inn="1234567890",
            ogrn="1234567890123",
            kpp="123456789",
            registration_date="2020-01-01",
            legal_address="г. Москва, ул. Тестовая, 1",
            phone="+7-999-123-45-67",
            email="info@company1.com"
        )
        
        company2 = Company(
            name="Company Two",
            slug="company-two", 
            user_id=user2.id,
            type="ООО",
            trade_activity="BUYER",
            business_type="SERVICES",
            activity_type="Услуги",
            country="Россия",
            federal_district="Северо-Западный",
            region="Ленинградская область", 
            city="Санкт-Петербург",
            full_name="ООО Компания Два",
            inn="0987654321",
            ogrn="3210987654321",
            kpp="987654321",
            registration_date="2020-01-01",
            legal_address="г. Санкт-Петербург, ул. Тестовая, 2",
            phone="+7-999-765-43-21",
            email="info@company2.com"
        )
        
        db.add(company1)
        db.add(company2)
        await db.commit()
        await db.refresh(company1)
        await db.refresh(company2)
        
        # Создаем чат-сервис
        chat_service = ChatService(db)
        
        # Создаем чат от имени user1 к company2
        chat_data = ChatCreate(participant_company_id=company2.id)
        chat = await chat_service.create_chat(user1.id, company1.id, chat_data)
        
        print(f"Создан чат ID: {chat.id}")
        print("Участники чата:")
        for participant in chat.participants:
            print(f"  - Компания: {participant.company_name} (ID: {participant.company_id})")
            print(f"    Пользователь: {participant.user_name} (ID: {participant.user_id})")
            print(f"    Владелец компании: {participant.company_id == company1.id and participant.user_id == user1.id or participant.company_id == company2.id and participant.user_id == user2.id}")
            print()
        
        # Проверяем, что участники разные
        user_ids = [p.user_id for p in chat.participants]
        if len(set(user_ids)) == 2:
            print("✅ ТЕСТ ПРОЙДЕН: Участники чата имеют разные user_id")
        else:
            print("❌ ТЕСТ ПРОВАЛЕН: Участники чата имеют одинаковые user_id")
            print(f"user_ids: {user_ids}")
        
        # Проверяем, что user_id соответствуют владельцам компаний
        for participant in chat.participants:
            if participant.company_id == company1.id and participant.user_id != user1.id:
                print(f"❌ ОШИБКА: Компания {company1.name} должна принадлежать пользователю {user1.id}, но участник имеет user_id {participant.user_id}")
            elif participant.company_id == company2.id and participant.user_id != user2.id:
                print(f"❌ ОШИБКА: Компания {company2.name} должна принадлежать пользователю {user2.id}, но участник имеет user_id {participant.user_id}")
            else:
                print(f"✅ Правильно: Компания {participant.company_name} принадлежит пользователю {participant.user_id}")

if __name__ == "__main__":
    asyncio.run(test_chat_creation()) 