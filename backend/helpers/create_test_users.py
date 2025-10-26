#!/usr/bin/env python3
import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import AsyncSessionLocal
from app.api.authentication.models.user import User
from app.api.company.models.company import Company
from app.api.authentication.models.roles_positions import UserRole
from app.api.company.repositories.company_repository import CompanyRepository
from sqlalchemy import text
from datetime import datetime

async def create_user_with_password():
    """Создаем пользователя с паролем напрямую"""
    async with AsyncSessionLocal() as db:
        try:
            # Создаем компанию через репозиторий
            company_repo = CompanyRepository(db)
            
            # Создаем slug для компании
            company_slug = await company_repo.create_company_slug("Тестовая компания ООО")
            
            company = Company(
                name="Тестовая компания ООО",
                slug=company_slug,
                type="ООО",
                trade_activity="BOTH",
                business_type="BOTH",
                activity_type="Торговля строительными материалами",
                description="Компания занимается продажей строительных материалов",
                country="Россия",
                federal_district="Центральный",
                region="Московская область",
                city="Москва",
                full_name="Общество с ограниченной ответственностью Тестовая компания",
                inn="1234567890",
                ogrn="1234567890123",
                kpp="123456789",
                registration_date=datetime(2020, 1, 1),
                legal_address="г. Москва, ул. Тестовая, д. 1",
                phone="+7 (495) 123-45-67",
                email="info@testcompany.ru",
                website="https://testcompany.ru",
                is_active=True
            )
            
            db.add(company)
            await db.flush()  # Получаем ID компании
            
            print(f"Создана компания: {company.name} (ID: {company.id}, slug: {company.slug})")
            
            # Создаем владельца компании с паролем
            # Используем простой хеш для пароля "password123"
            password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4VZJjKzKq2"
            
            owner = User(
                email="owner@testcompany.ru",
                first_name="Иван",
                last_name="Иванов",
                patronymic="Иванович",
                phone="79991234567",
                position="Генеральный директор",
                hashed_password=password_hash,
                is_active=True,
                company_id=company.id,
                role=UserRole.OWNER
            )
            
            db.add(owner)
            await db.flush()
            
            print(f"Создан владелец: {owner.email} (ID: {owner.id})")
            
            # Создаем сотрудника с паролем
            employee = User(
                email="employee@testcompany.ru",
                first_name="Петр",
                last_name="Петров",
                patronymic="Петрович",
                phone="79991234568",
                position="Менеджер по продажам",
                hashed_password=password_hash,
                is_active=True,
                company_id=company.id,
                role=UserRole.USER
            )
            
            db.add(employee)
            await db.flush()
            
            print(f"Создан сотрудник: {employee.email} (ID: {employee.id})")
            
            await db.commit()
            
            print("\nТестовые данные созданы успешно!")
            print(f"Компания: {company.name} (ИНН: {company.inn})")
            print(f"Владелец: {owner.email} (роль: {owner.role})")
            print(f"Сотрудник: {employee.email} (роль: {employee.role})")
            print(f"Пароль для всех пользователей: password123")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(create_user_with_password())
