# Команды для восстановления базы данных на сервере

## 1. Копирование дампа на сервер

Скопируйте файл `backup_20251026_143805.sql` на ваш сервер:

```bash
# С локальной машины (выполните эту команду на вашем компьютере)
scp backup_20251026_143805.sql user@your-server-ip:/path/to/backup/
```

Или если у вас сервер на той же машине:
```bash
sudo cp backup_20251026_143805.sql /path/to/backup/
```

## 2. Восстановление базы данных на сервере

После копирования файла на сервер, выполните следующие команды на сервере:

```bash
# Подключитесь к контейнеру базы данных
docker exec -i buisnes_kufar-db-1 psql -U postgres -d buisnes_kufar < backup_20251026_143805.sql
```

Или если база данных находится на хост-машине:
```bash
# Подключитесь к базе данных и восстановите дамп
psql -U postgres -d buisnes_kufar < backup_20251026_143805.sql
```

## 3. Альтернативный способ (через docker cp)

Если база данных находится в Docker контейнере:

```bash
# 1. Скопируйте файл в контейнер
docker cp backup_20251026_143805.sql buisnes_kufar-db-1:/tmp/backup.sql

# 2. Восстановите базу данных
docker exec -i buisnes_kufar-db-1 psql -U postgres -d buisnes_kufar < /tmp/backup.sql
```

## 4. Создание резервной копии перед восстановлением

⚠️ **ВАЖНО**: Перед восстановлением новой базы данных, создайте резервную копию существующей:

```bash
# На сервере
docker exec buisnes_kufar-db-1 pg_dump -U postgres buisnes_kufar > backup_before_restore_$(date +%Y%m%d_%H%M%S).sql
```

## 5. Полное восстановление (удаление и создание новой базы)

Если нужно полностью пересоздать базу данных:

```bash
# 1. Удалить существующую базу
docker exec -i buisnes_kufar-db-1 psql -U postgres -c "DROP DATABASE IF EXISTS buisnes_kufar;"

# 2. Создать новую базу
docker exec -i buisnes_kufar-db-1 psql -U postgres -c "CREATE DATABASE buisnes_kufar;"

# 3. Восстановить дамп
docker exec -i buisnes_kufar-db-1 psql -U postgres -d buisnes_kufar < backup_20251026_143805.sql
```
