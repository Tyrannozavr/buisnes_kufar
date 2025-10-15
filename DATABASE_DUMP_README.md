# Дампы базы данных для тестирования

Этот каталог содержит дампы базы данных `buisnes_kufar` с тестовыми данными.

## Файлы

- `database_dump.sql` - Полный дамп базы данных (схема + данные)
- `database_dump.sql.gz` - Сжатый полный дамп базы данных
- `database_data_only.sql` - Дамп только данных (без схемы)

## Содержимое базы данных

База содержит следующие тестовые данные:
- 👥 **50 пользователей** (включая пользователя с ИНН 1212121212)
- 🏢 **50 компаний** с полными реквизитами
- 📦 **144 товара** различных категорий
- 🔧 **46 услуг** (IT, консалтинг, образование)
- 📢 **200 объявлений** различных типов

## Тестовый пользователь

- **ИНН:** 1212121212
- **Пароль:** Dmiv2895
- **Email:** user1212121212@example.com
- **Имя:** Тестовый Пользователь Администраторович

## Восстановление базы данных

### Вариант 1: Полное восстановление (схема + данные)

```bash
# Остановить контейнеры
docker-compose -f docker-compose.full-local.yml down

# Удалить существующую базу данных (опционально)
docker volume rm buisnes_kufar_postgres_data

# Запустить только базу данных
docker-compose -f docker-compose.full-local.yml up -d db

# Восстановить базу данных
docker-compose -f docker-compose.full-local.yml exec -T db psql -U postgres < database_dump.sql

# Или для сжатого файла
gunzip -c database_dump.sql.gz | docker-compose -f docker-compose.full-local.yml exec -T db psql -U postgres
```

### Вариант 2: Только данные (если схема уже существует)

```bash
# Восстановить только данные
docker-compose -f docker-compose.full-local.yml exec -T db psql -U postgres -d buisnes_kufar < database_data_only.sql
```

### Вариант 3: Через Docker контейнер

```bash
# Скопировать дамп в контейнер
docker cp database_dump.sql buisnes_kufar-db-1:/tmp/database_dump.sql

# Восстановить из контейнера
docker-compose -f docker-compose.full-local.yml exec db psql -U postgres < /tmp/database_dump.sql
```

## Проверка восстановления

После восстановления проверьте, что данные загружены:

```bash
# Подключиться к базе данных
docker-compose -f docker-compose.full-local.yml exec db psql -U postgres -d buisnes_kufar

# Проверить количество записей
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'companies', COUNT(*) FROM companies
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'announcements', COUNT(*) FROM announcements;

# Проверить тестового пользователя
SELECT first_name, last_name, inn, email FROM users WHERE inn = '1212121212';
```

## Создание нового дампа

Для создания нового дампа с обновленными данными:

```bash
# Полный дамп
docker-compose -f docker-compose.full-local.yml exec db pg_dump -U postgres -d buisnes_kufar --clean --create --if-exists > database_dump.sql

# Сжатый дамп
docker-compose -f docker-compose.full-local.yml exec db pg_dump -U postgres -d buisnes_kufar --clean --create --if-exists | gzip > database_dump.sql.gz

# Только данные
docker-compose -f docker-compose.full-local.yml exec db pg_dump -U postgres -d buisnes_kufar --data-only --inserts > database_data_only.sql
```

## Примечания

- Дампы созданы с PostgreSQL версии 15.13
- Все данные в кодировке UTF-8
- Включены все таблицы, индексы, ограничения и данные
- Тестовый пользователь готов для входа в систему
