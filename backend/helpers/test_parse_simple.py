#!/usr/bin/env python3
"""Простой тест парсера для Марий Эл"""

import asyncio
import httpx
from bs4 import BeautifulSoup


async def test():
    url = "https://superresearch.ru/?id=858"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        full_text = soup.get_text()
        
        # Ищем паттерн
        import re
        pattern = r'Города\s+.*?\s+в\s+алфавитном\s+порядке:'
        match = re.search(pattern, full_text)
        
        if match:
            print(f"✅ Паттерн найден на позиции: {match.start()}-{match.end()}")
            
            start_pos = match.end()
            text_after = full_text[start_pos:start_pos+2000]
            
            print("\n" + "="*60)
            print("ТЕКСТ ПОСЛЕ МАРКЕРА (первые 2000 символов):")
            print("="*60)
            print(text_after)
            
            # Извлекаем города
            lines = text_after.split('\n')
            cities = []
            for line in lines:
                line = line.strip()
                if line and len(line) > 2 and len(line) < 60 and line[0].isupper():
                    if not any(skip in line for skip in ['©', 'Тел.', 'Россия', 'ул.', 'д.', 'п.', '+7']):
                        cities.append(line)
                        if '©' in line or 'Тел.' in line:
                            break
            
            print("\n" + "="*60)
            print(f"ИЗВЛЕЧЕНО ГОРОДОВ: {len(cities)}")
            print("="*60)
            for i, city in enumerate(cities[:20]):
                print(f"{i+1}. {city}")
        else:
            print("❌ Паттерн не найден")


if __name__ == "__main__":
    asyncio.run(test())

