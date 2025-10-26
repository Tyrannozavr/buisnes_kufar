#!/usr/bin/env python3
"""
Тестовый скрипт для проверки создания продукта с изображениями
"""

import asyncio
import os
import tempfile
import httpx
from pathlib import Path

async def test_create_product_with_images():
    """Тестирует создание продукта с изображениями"""
    print("🧪 Тестирование создания продукта с изображениями")
    
    # Создаем временное изображение для тестирования
    def create_test_image():
        """Создает временное тестовое изображение"""
        # Простой PNG файл (1x1 пиксель, прозрачный)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x00\x00\x02\x00\x01\xe5\x27\xde\xfc\x00\x00\x00\x00IEND\xaeB`\x82'
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_file.write(png_data)
        temp_file.close()
        return temp_file.name

    # Создаем тестовое изображение
    test_image_path = create_test_image()
    print(f"✅ Тестовое изображение создано: {test_image_path}")
    
    try:
        # Тестируем API эндпоинт
        async with httpx.AsyncClient() as client:
            # Подготавливаем FormData
            files = {
                'name': (None, 'Тестовый продукт'),
                'description': (None, 'Описание тестового продукта'),
                'article': (None, 'TEST-001'),
                'type': (None, 'Товар'),
                'price': (None, '1000.0'),
                'unit_of_measurement': (None, 'шт'),
                'is_hidden': (None, 'false'),
                'characteristics': (None, '[]'),
                'files': (open(test_image_path, 'rb'), 'test.png', 'image/png')
            }
            
            # Отправляем запрос
            response = await client.post(
                'http://localhost:8000/api/v1/products/with-images',
                files=files,
                timeout=30.0
            )
            
            print(f"📡 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Продукт успешно создан с изображениями!")
                product_data = response.json()
                print(f"📦 ID продукта: {product_data.get('id')}")
                print(f"📦 Название: {product_data.get('name')}")
                print(f"📦 Изображения: {product_data.get('images')}")
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"📄 Ответ: {response.text}")
                
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {str(e)}")
    
    finally:
        # Очистка
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)
            print(f"🧹 Тестовый файл удален: {test_image_path}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(test_create_product_with_images()) 