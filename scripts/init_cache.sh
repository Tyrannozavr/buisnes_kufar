#!/bin/bash

echo "🔄 Инициализация кэша активных городов..."

# Ждем готовности базы данных
echo "⏳ Ожидание готовности базы данных..."
sleep 5

# Проверяем подключение к базе данных
until pg_isready -h db -U postgres; do
  echo "⏳ База данных еще не готова, ждем..."
  sleep 2
done

echo "✅ База данных готова"

# Заполняем кэш активных городов
echo "🔄 Заполняем кэш активных городов..."

psql -h db -U postgres -d postgres << 'EOF'
-- Очищаем старый кэш
DELETE FROM active_cities_cache;

-- Заполняем кэш компаний
INSERT INTO active_cities_cache (cache_type, active_city_ids, total_cities, total_companies, total_products, last_updated, is_active)
SELECT 
    'companies' as cache_type,
    to_json(ARRAY_AGG(DISTINCT c.city_id)) as active_city_ids,
    COUNT(DISTINCT c.city_id) as total_cities,
    COUNT(DISTINCT c.id) as total_companies,
    0 as total_products,
    NOW() as last_updated,
    true as is_active
FROM companies c
WHERE c.is_active = true
    AND c.city_id IS NOT NULL
    AND c.city IS NOT NULL
    AND c.city != '';

-- Заполняем кэш продуктов
INSERT INTO active_cities_cache (cache_type, active_city_ids, total_cities, total_companies, total_products, last_updated, is_active)
SELECT 
    'products' as cache_type,
    to_json(ARRAY_AGG(DISTINCT c.city_id)) as active_city_ids,
    COUNT(DISTINCT c.city_id) as total_cities,
    COUNT(DISTINCT c.id) as total_companies,
    COUNT(DISTINCT p.id) as total_products,
    NOW() as last_updated,
    true as is_active
FROM products p
JOIN companies c ON p.company_id = c.id
WHERE p.type = 'GOOD' 
    AND p.is_deleted = false 
    AND p.is_hidden = false
    AND c.is_active = true
    AND c.city_id IS NOT NULL
    AND c.city IS NOT NULL
    AND c.city != '';

-- Показываем результат
SELECT 
    cache_type,
    total_cities,
    total_companies,
    total_products,
    last_updated
FROM active_cities_cache 
ORDER BY cache_type;
EOF

echo "✅ Кэш активных городов заполнен!"

# Проверяем статус кэша
echo "📊 Статистика кэша:"
psql -h db -U postgres -d postgres -c "
SELECT 
    cache_type,
    total_cities,
    total_companies,
    total_products,
    last_updated
FROM active_cities_cache 
ORDER BY cache_type;
"

echo "🎉 Инициализация кэша завершена!"
