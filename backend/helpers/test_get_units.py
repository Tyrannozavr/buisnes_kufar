#!/usr/bin/env python3
"""
Тест получения единиц измерения через API
"""

import asyncio
import httpx
import json

async def test_get_units():
    """Тест получения единиц измерения"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("1. Получаем токен...")
        
        # Логин
        login_data = {
            "email": "buyer@test.com",
            "password": "testpassword123",
            "inn": "9876543210"
        }
        
        response = await client.post(f"{base_url}/api/v1/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Ошибка логина: {response.status_code}")
            print(f"Ответ: {response.text}")
            return
        
        token_data = response.json()
        token = token_data["access_token"]
        print("✅ Токен получен")
        
        # Получаем единицы измерения
        print(f"\n2. Получаем единицы измерения...")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(f"{base_url}/api/v1/purchases/units", headers=headers)
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки ответа: {response.headers}")
        
        if response.status_code == 200:
            units_data = response.json()
            print("✅ Единицы измерения получены:")
            print(f"Всего единиц: {len(units_data)}")
            
            # Показываем первые 5 единиц
            for i, unit in enumerate(units_data[:5]):
                print(f"{i+1}. {unit['name']} ({unit['symbol']}) - код: {unit['code']}")
            
            if len(units_data) > 5:
                print(f"... и еще {len(units_data) - 5} единиц")
        else:
            print(f"❌ Ошибка получения единиц измерения: {response.status_code}")
            print(f"Ответ: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_get_units())
