#!/usr/bin/env python3
"""
Скрипт для исправления существующих чатов с неправильными участниками
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.api.chats.models.chat_participant import ChatParticipant
from app.api.chats.models.chat import Chat
from app.api.company.models.company import Company
from app.api.authentication.models import User

async def fix_existing_chats():
    """Исправляет существующие чаты с неправильными участниками"""
    
    async with AsyncSessionLocal() as db:
        # Получаем все чаты
        result = await db.execute(select(Chat))
        chats = result.scalars().all()
        
        print(f"Найдено чатов: {len(chats)}")
        
        for chat in chats:
            print(f"\nПроверяем чат ID: {chat.id}")
            
            # Получаем участников чата
            result = await db.execute(
                select(ChatParticipant).where(ChatParticipant.chat_id == chat.id)
            )
            participants = result.scalars().all()
            
            if len(participants) != 2:
                print(f"  ⚠️  Чат имеет {len(participants)} участников (ожидается 2)")
                continue
            
            # Проверяем, есть ли дублирующиеся user_id
            user_ids = [p.user_id for p in participants]
            if len(set(user_ids)) == 1:
                print(f"  ❌ Найдена проблема: оба участника имеют user_id {user_ids[0]}")
                
                # Получаем компании участников
                company_ids = [p.company_id for p in participants]
                
                # Получаем информацию о компаниях
                result = await db.execute(
                    select(Company).where(Company.id.in_(company_ids))
                )
                companies = result.scalars().all()
                
                # Создаем словарь компаний
                companies_dict = {c.id: c for c in companies}
                
                # Исправляем второго участника
                for participant in participants:
                    company = companies_dict.get(participant.company_id)
                    if company and participant.user_id != company.user_id:
                        print(f"  🔧 Исправляем участника {participant.id}: user_id {participant.user_id} -> {company.user_id}")
                        participant.user_id = company.user_id
                
                await db.commit()
                print(f"  ✅ Чат исправлен")
            else:
                print(f"  ✅ Чат в порядке: участники имеют разные user_id {user_ids}")

async def show_chat_participants():
    """Показывает всех участников чатов"""
    
    async with AsyncSessionLocal() as db:
        # Получаем все участники чатов с информацией о компаниях и пользователях
        result = await db.execute(
            select(ChatParticipant, Company, User)
            .join(Company, ChatParticipant.company_id == Company.id)
            .join(User, ChatParticipant.user_id == User.id)
            .order_by(ChatParticipant.chat_id, ChatParticipant.id)
        )
        
        participants_data = result.all()
        
        print("Участники чатов:")
        print("-" * 80)
        
        current_chat = None
        for participant, company, user in participants_data:
            if current_chat != participant.chat_id:
                current_chat = participant.chat_id
                print(f"\nЧат ID: {participant.chat_id}")
                print("-" * 40)
            
            print(f"  Участник ID: {participant.id}")
            print(f"    Компания: {company.name} (ID: {company.id})")
            print(f"    Пользователь: {user.first_name} {user.last_name} (ID: {user.id})")
            print(f"    Владелец компании: {company.user_id == user.id}")
            print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        asyncio.run(show_chat_participants())
    else:
        print("Исправление существующих чатов...")
        asyncio.run(fix_existing_chats())
        print("\nПроверка участников чатов после исправления:")
        asyncio.run(show_chat_participants()) 