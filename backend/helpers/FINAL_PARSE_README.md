# Скрипт для парсинга городов с superresearch.ru

## Что делает скрипт:
1. ✅ Парсит города со страниц [superresearch.ru](https://superresearch.ru/?id=808) для всех регионов России
2. ✅ **Автоматически проверяет дубликаты** - не добавляет города, которые уже есть в БД
3. ✅ Использует регистронезависимое сравнение ("Москва" = "москва")
4. ✅ Показывает статистику: сколько найдено, сколько добавлено, сколько пропущено

## Защита от дубликатов (3 уровня):

### 1. При парсинге (строки 274-295)
```python
# Удаляет дубликаты сразу при извлечении
unique_cities = []
seen = set()
for city in cities:
    city_key = city_normalized.lower()
    if city_key not in seen:  # Проверка
        seen.add(city_key)
        unique_cities.append(city_normalized)
```

### 2. Перед добавлением в БД (строки 339-362)
```python
# Получаем существующие города
existing_city_names = {city[0].lower().strip() for city in existing_cities_result.all()}

# Проверяем каждый город
for city_name in cities:
    city_normalized = city_name.lower().strip()
    if city_normalized in existing_city_names:  # ❌ НЕ добавляем
        cities_skipped += 1
        continue  # Пропускаем
```

### 3. Регистронезависимое сравнение
Названия сравниваются в нижнем регистре для всех проверок.

## Как запустить:

### Вариант 1: Через локальный Python
```bash
cd backend
source new_venv/bin/activate
pip install beautifulsoup4 httpx lxml
python3 parse_cities_from_superresearch.py
```

### Вариант 2: Через Docker (нужно установить зависимости)
```bash
docker exec buisnes_kufar-backend-1 pip install beautifulsoup4 httpx
docker cp backend/parse_cities_from_superresearch.py buisnes_kufar-backend-1:/app/
docker exec buisnes_kufar-backend-1 python3 /app/parse_cities_from_superresearch.py
```

## Пример вывода для Марий Эл:
```
🌍 Обрабатываем: Республика Марий Эл
📍 Найдено уникальных городов на странице: 210
📋 Уже существует городов в БД: 1 (только Йошкар-Ола)
✅ Добавлено городов: 209
⏭️  Пропущено дубликатов/существующих: 1
```

## Проверка результатов:
```sql
-- Посмотреть все города Марий Эл
SELECT c.name, c.population 
FROM cities c
JOIN regions r ON c.region_id = r.id
WHERE r.name = 'Республика Марий Эл'
ORDER BY c.name;
```

## Что будет обработано:
- 85 регионов России
- Каждый регион парсится с superresearch.ru
- Только новые города добавляются
- Существующие пропускаются (защита от дубликатов)

