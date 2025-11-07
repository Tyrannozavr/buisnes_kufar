#!/usr/bin/env python3
"""
Тестовый скрипт для проверки парсинга страницы Марий Эл
"""

import asyncio
import httpx
from bs4 import BeautifulSoup


async def test_parse_mari():
    url = "https://superresearch.ru/?id=858"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        print(f"Статус: {response.status_code}")
        print(f"Размер: {len(response.text)} байт\n")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Сохраняем HTML для анализа
        with open('/tmp/mari_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print("HTML сохранен в /tmp/mari_page.html")
        
        # Ищем все таблицы
        tables = soup.find_all('table')
        print(f"\nНайдено таблиц: {len(tables)}")
        
        # Ищем текст со страницы
        content = soup.get_text()
        print(f"\nДлина текста: {len(content)} символов")
        
        # Выводим первые 5000 символов
        print("\n" + "="*60)
        print("ПЕРВЫЕ 5000 СИМВОЛОВ:")
        print("="*60)
        print(content[:5000])
        
        # Ищем паттерны с городами
        print("\n" + "="*60)
        print("ГОРОДА (поиск по паттернам):")
        print("="*60)
        
        # Ищем все элементы, которые могут быть городами
        possible_cities = []
        for element in soup.find_all(['a', 'td', 'span', 'div']):
            text = element.get_text(strip=True)
            if text and len(text) > 2 and len(text) < 100:
                # Проверяем, похоже ли на название города
                if text[0].isupper() and not text.isupper():
                    possible_cities.append(text)
        
        print(f"Найдено возможных городов: {len(possible_cities)}")
        for i, city in enumerate(possible_cities[:50]):
            print(f"{i+1}. {city}")


if __name__ == "__main__":
    asyncio.run(test_parse_mari())

