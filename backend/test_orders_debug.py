"""
Подробный тест для отладки API заказов
"""
import asyncio
import httpx
import traceback

async def test_create_order_debug():
    """Тестирование создания заказа с подробным выводом"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Получаем токен
        print("1. Получаем токен...")
        login_data = {
            "email": "buyer@test.com",
            "password": "testpassword123",
            "inn": "9876543210"
        }
        
        response = await client.post(f"{base_url}/api/v1/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Ошибка авторизации: {response.status_code}")
            print(response.text)
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Токен получен")
        
        # Тестируем создание заказа
        print("\n2. Создаем заказ...")
        order_data = {
            "seller_company_id": 11,
            "deal_type": "Товары",
            "items": [
                {
                    "product_name": "Тестовый товар API",
                    "product_article": "API001",
                    "quantity": 5,
                    "unit_of_measurement": "шт",
                    "price": 200.00,
                    "position": 1
                }
            ],
            "comments": "Тестовый заказ через API"
        }
        
        print(f"Данные заказа: {order_data}")
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/purchases/deals", 
                json=order_data, 
                headers=headers,
                timeout=30.0
            )
            
            print(f"Статус ответа: {response.status_code}")
            print(f"Заголовки ответа: {response.headers}")
            print(f"Тело ответа: {response.text}")
            
            if response.status_code == 200:
                order = response.json()
                print(f"✅ Заказ создан: ID {order['id']}")
            else:
                print(f"❌ Ошибка создания заказа: {response.status_code}")
        except Exception as e:
            print(f"❌ Исключение при создании заказа: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create_order_debug())
