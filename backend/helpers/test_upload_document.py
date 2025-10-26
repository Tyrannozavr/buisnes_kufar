#!/usr/bin/env python3
"""
Тест загрузки документов к заказу через API
"""

import asyncio
import httpx
import json

async def test_upload_document():
    """Тест загрузки документа к заказу"""
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
        
        # Загружаем документ
        print(f"\n2. Загружаем документ к заказу ID 21...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Создаем тестовый файл
        test_content = "Тестовый документ для заказа"
        files = {
            "file": ("test_document.txt", test_content, "text/plain")
        }
        
        data = {
            "document_type": "invoice",
            "document_number": "INV-001",
            "description": "Тестовый счет-фактура"
        }
        
        response = await client.post(
            f"{base_url}/api/v1/purchases/deals/21/documents",
            headers=headers,
            files=files,
            data=data
        )
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки ответа: {response.headers}")
        
        if response.status_code == 200:
            document_data = response.json()
            print("✅ Документ загружен:")
            print(f"Ответ: {document_data}")
        else:
            print(f"❌ Ошибка загрузки документа: {response.status_code}")
            print(f"Ответ: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_upload_document())
