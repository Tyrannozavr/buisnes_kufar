# Локальный запуск и проверка в браузере

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

Рекомендуется вручную проверить в браузере:

1. Главная — блок «Компании» и навигация.
2. Вход/регистрация и переход в личный кабинет.
3. Разделы «Закупки» / «Продажи» (вкладки Товары/Услуги), создание сделки, редактор документа.
