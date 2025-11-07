#!/usr/bin/env python3
"""
Скрипт для скачивания всех списков городов с superresearch.ru/?id=808
и сохранения их в файлы формата "название области.txt"
"""

import asyncio
import re
from pathlib import Path
from typing import List, Dict
import httpx
from bs4 import BeautifulSoup


# Устанавливаем выходную директорию
OUTPUT_DIR = Path("data_cities")
OUTPUT_DIR.mkdir(exist_ok=True)


async def fetch_page(url: str, max_retries: int = 3) -> str:
    """Загружает страницу с повторными попытками"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"  ⚠️  Попытка {attempt + 1}/{max_retries} не удалась для {url}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                raise
    return ""


def parse_region_links(html: str) -> Dict[str, str]:
    """
    Извлекает ссылки на регионы с главной страницы superresearch.ru/?id=808
    
    Returns:
        Dict с ключом "название региона" и значением "полный URL"
    """
    soup = BeautifulSoup(html, 'html.parser')
    regions = {}
    
    # Ищем ссылки вида "города X в алфавитном порядке"
    for link in soup.find_all('a', href=True):
        text = link.get_text(strip=True)
        href = link.get('href', '')
        
        # Проверяем паттерн "города X в алфавитном порядке"
        if 'города' in text.lower() and 'в алфавитном порядке' in text.lower():
            # Извлекаем название региона из текста ссылки
            # Пример: "города Республики Марий Эл в алфавитном порядке"
            match = re.search(r'города\s+(.+?)\s+в\s+алфавитном\s+порядке', text, re.IGNORECASE)
            if match:
                region_name = match.group(1).strip()
                
                # Формируем полный URL
                if href.startswith('?'):
                    full_url = f"https://superresearch.ru{href}"
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = f"https://superresearch.ru/{href}"
                
                regions[region_name] = full_url
    
    return regions


def parse_cities_from_html(html: str) -> List[str]:
    """
    Извлекает список городов из HTML страницы
    
    Returns:
        List[str]: Список названий городов
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Получаем весь текст страницы
    full_text = soup.get_text()
    
    # Ищем паттерн "Города X в алфавитном порядке:"
    pattern = r'города\s+.*?\s+в\s+алфавитном\s+порядке:'
    match = re.search(pattern, full_text, re.IGNORECASE)
    
    cities = []
    
    if match:
        # Берем текст после маркера
        start_pos = match.end()
        text_after_marker = full_text[start_pos:]
        
        # Разбиваем по строкам
        lines = text_after_marker.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Пропускаем пустые строки
            if not line:
                continue
            
            # Проверяем, похоже ли на название города
            # Имя собственное: начинается с заглавной буквы
            if len(line) > 2 and len(line) < 60 and line[0].isupper():
                # Пропускаем служебную информацию
                if not any(skip in line for skip in ['©', 'Тел.', 'Россия', 'ул.', 'д.', 'п.', '+7', 'главная', 'RAI']):
                    cities.append(line)
                    
                    # Останавливаемся когда встречаем маркеры конца списка
                    if any(marker in line for marker in ['©', 'Тел.', 'Created by', 'Powered by']):
                        break
    
    # Очищаем от дубликатов и фильтруем
    unique_cities = []
    seen = set()
    
    for city in cities:
        # Нормализуем: убираем лишние пробелы и символы
        city_normalized = ' '.join(city.split())
        city_normalized = city_normalized.strip()
        
        # Проверяем, что это не слишком короткое или длинное слово
        if 2 < len(city_normalized) < 50:
            # Проверяем, что содержит хотя бы одну букву
            if any(c.isalpha() for c in city_normalized):
                # Для сравнения используем lower()
                city_key = city_normalized.lower()
                
                # Проверяем дубликаты (регистронезависимо)
                if city_key not in seen:
                    seen.add(city_key)
                    unique_cities.append(city_normalized)
    
    return unique_cities


async def fetch_and_save_region(region_name: str, url: str):
    """Загружает страницу региона и сохраняет список городов в файл"""
    print(f"  📍 Загружаем: {region_name}")
    
    try:
        html = await fetch_page(url)
        cities = parse_cities_from_html(html)
        
        if cities:
            # Создаем безопасное имя файла
            safe_filename = re.sub(r'[^\w\s-]', '', region_name)
            safe_filename = re.sub(r'\s+', '_', safe_filename)
            filepath = OUTPUT_DIR / f"{safe_filename}.txt"
            
            # Сохраняем города в файл
            with open(filepath, 'w', encoding='utf-8') as f:
                for city in cities:
                    f.write(f"{city}\n")
            
            print(f"    ✅ Сохранено {len(cities)} городов в {filepath}")
        else:
            print(f"    ⚠️  Города не найдены для {region_name}")
            
    except Exception as e:
        print(f"    ❌ Ошибка для {region_name}: {e}")


async def main():
    """Основная функция"""
    print("🚀 Начинаем загрузку всех регионов с superresearch.ru...\n")
    
    # 1. Загружаем главную страницу
    main_url = "https://superresearch.ru/?id=808"
    print(f"📥 Загружаем главную страницу: {main_url}")
    
    try:
        main_html = await fetch_page(main_url)
        print("✅ Главная страница загружена\n")
    except Exception as e:
        print(f"❌ Ошибка загрузки главной страницы: {e}")
        return
    
    # 2. Извлекаем ссылки на регионы
    print("🔍 Извлекаем ссылки на регионы...")
    regions = parse_region_links(main_html)
    print(f"✅ Найдено регионов: {len(regions)}\n")
    
    if not regions:
        print("❌ Регионы не найдены на странице!")
        return
    
    # 3. Выводим список найденных регионов
    print("📋 Найденные регионы:")
    for i, region_name in enumerate(regions.keys(), 1):
        print(f"  {i}. {region_name}")
    
    print(f"\n{'='*60}")
    print(f"🌍 Начинаем загрузку городов для каждого региона...")
    print(f"{'='*60}\n")
    
    # 4. Загружаем города для каждого региона (максимум 2-3 параллельных запросов)
    semaphore = asyncio.Semaphore(2)  # Ограничиваем до 2 одновременных запросов
    
    async def fetch_with_limit(region_name: str, url: str):
        async with semaphore:
            await fetch_and_save_region(region_name, url)
    
    tasks = [
        fetch_with_limit(region_name, url)
        for region_name, url in regions.items()
    ]
    
    await asyncio.gather(*tasks)
    
    # 5. Итоги
    saved_files = list(OUTPUT_DIR.glob("*.txt"))
    print(f"\n{'='*60}")
    print(f"🎉 ЗАВЕРШЕНО!")
    print(f"{'='*60}")
    print(f"📊 Всего сохранено файлов: {len(saved_files)}")
    print(f"📁 Файлы сохранены в: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    asyncio.run(main())

