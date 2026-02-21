# Локальный запуск и проверка в браузере

## Деплой на прод (GitHub Actions)

При пуше в `master` запускается workflow **Deploy to production**: он подключается по SSH к серверу, подтягивает `origin/master` в `/root/buisnes_kufar` и выполняет `docker compose up -d --build`. Если деплой упал (например, из‑за сетевой ошибки при `docker pull`), можно:
- **Повторно запустить** workflow в GitHub: Actions → Deploy to production → Re-run all jobs.
- **Вручную на сервере:** `ssh root@77.222.47.33`, затем `cd /root/buisnes_kufar && git fetch origin && git reset --hard origin/master && docker compose up -d --build`.

### Если на сервере не тянется образ python:3.12-slim (Docker Hub)

Образ можно залить с локальной машины, где Docker Hub доступен:

```bash
# Локально
docker pull python:3.12-slim
docker save -o /tmp/python-3.12-slim.tar python:3.12-slim
scp /tmp/python-3.12-slim.tar root@77.222.47.33:/tmp/

# На сервере
ssh root@77.222.47.33
docker load -i /tmp/python-3.12-slim.tar
rm /tmp/python-3.12-slim.tar
cd /root/buisnes_kufar && docker compose up -d --build
```

### Продовая БД: колонки в companies

Если API компаний отдаёт 500 с ошибкой `column companies.current_account_number does not exist`, на проде нужно добавить колонки (пользователь БД в docker-compose — `postgres`):

```bash
docker compose exec -T db psql -U postgres -d buisnes_kufar -c "
ALTER TABLE companies ADD COLUMN IF NOT EXISTS current_account_number VARCHAR(50);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS bic VARCHAR(20);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS vat_rate NUMERIC(5,2);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS correspondent_bank_account VARCHAR(50);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS bank_name VARCHAR(255);
"
```

---

## Запуск

```bash
docker compose -f docker-compose.dev.yml up -d db rabbitmq minio backend frontend nginx
```

- **Сайт:** http://localhost:8080 (через nginx)
- **Frontend напрямую:** http://localhost:3012
- **Backend API:** http://localhost:8012
- **API Docs:** http://localhost:8080/docs

## Исправление для первой загрузки главной

В dev-БД в таблице `companies` не было колонок платёжных реквизитов (модель уже с полями, миграция не была применена). Добавлены вручную:

```sql
ALTER TABLE companies ADD COLUMN IF NOT EXISTS current_account_number VARCHAR(20);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS bic VARCHAR(9);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS vat_rate INTEGER;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS correspondent_bank_account VARCHAR(20);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS bank_name VARCHAR(255);
```

Команда для выполнения в контейнере БД:

```bash
docker compose -f docker-compose.dev.yml exec db psql -U postgres -d buisnes_kufar -c "
ALTER TABLE companies ADD COLUMN IF NOT EXISTS current_account_number VARCHAR(20);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS bic VARCHAR(9);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS vat_rate INTEGER;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS correspondent_bank_account VARCHAR(20);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS bank_name VARCHAR(255);
"
```

## Проверка страниц (соответствие ТЗ)

| Страница | HTTP | Примечание |
|----------|------|------------|
| `/` | 200 | Главная, блок компаний загружается |
| `/auth/login` | 200 | Вход |
| `/catalog/products` | 200 | Каталог товаров |
| `/catalog/services` | — | Каталог услуг (по ТЗ) |
| `/checkout` | 200 | Страница подтверждения заказа |
| `/profile/purchases` | 302 | Редирект на авторизацию (ожидаемо) |
| `/profile/sales` | 302 | Редирект на авторизацию |
| `/profile/documents` | 302 | Редирект на авторизацию |
| `/profile/editor` | 302 | Редактор заказа (по ТЗ) |
| `/docs` | 200 | Swagger API |

По анализу кода (CODE_QUALITY_ANALYSIS.md) и ТЗ реализовано до раздела «Счет (в разработке)»:

- Единицы измерения (ОКЕИ), справочник и API
- Страница подтверждения (checkout), закладки Товары/Услуги
- Редактор заказа с вкладками, «Заполнить данными», Печать, DOC/PDF
- Версионирование сделок, уведомление контрагента, Принять/Отклонить
- Должностные лица, платежные реквизиты компании, S3

### Авто-проверка продакшена по ТЗ

Скрипт проверяет страницы и публичные API (без авторизации):

```bash
bash scripts/test_production.sh
```

Проверяются: главная, вход, каталог товаров/услуг, checkout, профили (закупки/продажи/документы), редактор заказа, компании, Swagger, о нас; API: companies, announcements, products, locations.

---

Рекомендуется вручную проверить в браузере:

1. Главная — блок «Компании» и навигация.
2. Вход/регистрация и переход в личный кабинет.
3. Разделы «Закупки» / «Продажи» (вкладки Товары/Услуги), создание сделки, редактор документа.
