"""
Простой тест для проверки API заказов
"""
import asyncio
import httpx

async def test_orders_api():
    """Тестирование API заказов"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Получаем токен
        login_data = {
            "email": "buyer@test.com",
            "password": "testpassword123",
            "inn": "9876543210"
        }
        
        response = await client.post(f"{base_url}/api/v1/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"Ошибка авторизации: {response.status_code}")
            print(response.text)
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Тестируем единицы измерения
        response = await client.get(f"{base_url}/api/v1/purchases/units", headers=headers)
        if response.status_code == 200:
            units = response.json()
            print(f"✅ Единицы измерения: {len(units)} записей")
        else:
            print(f"❌ Ошибка единиц измерения: {response.status_code}")
        
        # Тестируем создание заказа
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
        
        response = await client.post(f"{base_url}/api/v1/purchases/deals", json=order_data, headers=headers)
        if response.status_code == 200:
            order = response.json()
            print(f"✅ Заказ создан: ID {order['id']}")
        else:
            print(f"❌ Ошибка создания заказа: {response.status_code}")
            print(response.text)
        
        # Тестируем получение заказов покупателя
        response = await client.get(f"{base_url}/api/v1/purchases/buyer/deals", headers=headers)
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ Заказы покупателя: {len(orders)} записей")
        else:
            print(f"❌ Ошибка получения заказов: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(test_orders_api())
