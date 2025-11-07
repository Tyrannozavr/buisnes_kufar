#!/usr/bin/env python3
import asyncio
import sys
import os
import requests
import json

async def complete_registration():
    """Завершаем регистрацию через API"""
    
    # Данные для завершения регистрации
    token = "hkLf5eXwz7bSvga5fT4kyaKGG0O2TCo2Cf1_4lq0A78"
    
    # Шаг 2: Завершение регистрации с паролем и данными компании
    step2_data = {
        "token": token,
        "password": "password123",
        "company_name": "Тестовая компания ООО",
        "company_type": "ООО",
        "inn": "1234567890",
        "ogrn": "1234567890123",
        "kpp": "123456789",
        "legal_address": "г. Москва, ул. Тестовая, д. 1",
        "phone": "+7 (495) 123-45-67",
        "email": "info@testcompany.ru",
        "website": "https://testcompany.ru",
        "activity_type": "Торговля строительными материалами",
        "description": "Компания занимается продажей строительных материалов",
        "country": "Россия",
        "federal_district": "Центральный",
        "region": "Московская область",
        "city": "Москва",
        "trade_activity": "BOTH",
        "business_type": "BOTH"
    }
    
    try:
        # Отправляем запрос на завершение регистрации
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register/step2",
            json=step2_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Регистрация завершена успешно!")
            data = response.json()
            print(f"Пользователь: {data.get('user', {}).get('email')}")
            print(f"Компания: {data.get('company', {}).get('name')}")
        else:
            print("❌ Ошибка при завершении регистрации")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(complete_registration())
