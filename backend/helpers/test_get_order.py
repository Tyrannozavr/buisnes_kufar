#!/usr/bin/env python3
"""
Тест получения заказа через API
"""

import asyncio
import httpx
import json

async def test_get_order():
    """Тест получения заказа"""
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
        
        # Получаем заказ
        print(f"\n2. Получаем заказ ID 21...")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(f"{base_url}/api/v1/purchases/deals/21", headers=headers)
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки ответа: {response.headers}")
        
        if response.status_code == 200:
            order_data = response.json()
            print("✅ Заказ получен:")
            print(f"ID: {order_data['id']}")
            print(f"Номер покупателя: {order_data['buyer_order_number']}")
            print(f"Номер продавца: {order_data['seller_order_number']}")
            print(f"Статус: {order_data['status']}")
            print(f"Тип сделки: {order_data['deal_type']}")
            print(f"Общая сумма: {order_data['total_amount']}")
            print(f"Комментарии: {order_data['comments']}")
            print(f"Позиций: {len(order_data['items'])}")
            print(f"Компания покупателя: {order_data['buyer_company']['name']}")
            print(f"Компания продавца: {order_data['seller_company']['name']}")
        else:
            print(f"❌ Ошибка получения заказа: {response.status_code}")
            print(f"Ответ: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_get_order())
