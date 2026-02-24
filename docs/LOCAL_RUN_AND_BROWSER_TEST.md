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

### Продовая БД: orders (версионирование и refactor)

Если API `/api/v1/purchases/buyer/deals` или `seller/deals` отдаёт 500 с ошибкой про `orders.row_id` или `orders.version` или `orders.buyer_order_date`, на проде нужно довести схему до актуальной:

1. Колонки в **companies** (см. ниже).
2. В **orders**: колонка `version INTEGER NOT NULL DEFAULT 1`, колонка `row_id` (PK), колонки `buyer_order_date`, `seller_order_date`, `bill_number`, `bill_date`, `supply_contracts_number`, `supply_contracts_date`, `closing_documents`, `others_documents`; удалить `invoice_number`, `invoice_date`. Дочерние таблицы: `order_items`, `order_history`, `order_documents` — связь через `order_row_id` → `orders.row_id`. Полная последовательность в миграциях Alembic: `refactor_orders_fields`, `9f4e8d7c1a2b_add_deal_versioning_with_row_id`. При конфликтах (колонки уже есть) — пометить ревизии через `alembic stamp` и при необходимости выполнить шаги миграций вручную.

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

### WebSocket (Vite HMR) при доступе через localhost:8080

Если в консоли браузера видно `[vite] failed to connect to websocket`, проверьте:

- В `nuxt.config.ts` для dev задано `vite.server.hmr` с `clientPort: DEV_NGINX_PORT` (8080), чтобы клиент подключался к тому же порту.
- В контейнер frontend передаётся `DEV_NGINX_PORT=8080`.
- В `nginx/nginx.local.conf` для `location /` включены заголовки WebSocket: `Upgrade`, `Connection` (и `map $http_upgrade $connection_upgrade`).

После пересборки nginx (`docker compose -f docker-compose.dev.yml up -d --build nginx`) и перезапуска frontend HMR должен работать при открытии http://localhost:8080.

Для работы WebSocket HMR в nginx для `location ~ ^/(_nuxt|_ipx)` также включены заголовки `Upgrade` и `Connection` и таймауты.

### Логотипы в шапке (404 / 500)

Если в консоли были 500 на `/_ipx/_/images/logo.jpg` или `companyNameWhite.png`, в шапке переключены на обычный `<img>` (без NuxtImg), чтобы не вызывать `_ipx`. Положите файлы `logo.jpg` и `companyNameWhite.png` в `frontend/public/images/` — тогда они будут отдаваться по путям `/images/logo.jpg` и `/images/companyNameWhite.png`. См. `frontend/public/images/README.md`.

### Тестовый пользователь (локальная БД)

После поднятия dev-стека можно создать тестового пользователя для проверки сценариев под авторизацией:

```bash
docker compose -f docker-compose.dev.yml run --rm backend python scripts/create_test_user.py
```

- **Логин:** `test@localhost.dev`
- **Пароль:** `test123456`
- Вход: http://localhost:8080/auth/login
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
4. Редактор: «Заполнить данными» → выбор сделки → вкладка «Счет», кнопки «СЧЕТ на основании», печать/DOC/PDF.

---

## Готовность к проду (по ТЗ)

Чек-лист перед релизом:

| Проверка | Как проверить |
|----------|----------------|
| Страницы (главная, вход, каталоги, checkout, профили, редактор, компании, /docs, /about) | `bash scripts/test_production.sh` или вручную на tradesynergy.ru |
| Публичные API (companies, announcements, products, locations) | Входит в `test_production.sh` |
| Вход под пользователем, личный кабинет | Вручную: логин/пароль → профиль закупок/продаж/документов |
| Редактор заказа: заполнить данными, вкладка «Счет», номер и дата счёта | Вручную: профиль → редактор → «Заполнить данными» → Счет |
| Платежные реквизиты компании, единицы измерения (ОКЕИ) | Реализовано в API и формах; при 500 на проде — проверить миграции БД (см. разделы про companies/orders выше) |
| Версионирование сделок, уведомление контрагента, Принять/Отклонить | Реализовано в API и редакторе |

Локальная проверка с тестовым пользователем: после `python scripts/create_test_user.py` войти на http://localhost:8080/auth/login как `test@localhost.dev` / `test123456` и пройти сценарии выше.
