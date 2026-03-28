# Контекст: сделка (deal / order) и API

Используй этот документ, когда нужно менять логику сделок, эндпоинты `purchases`, типы ответа/запроса или UI счетов/договоров по сделке.

## Термины

| Термин | Значение |
|--------|----------|
| **Сделка / deal** | Бизнес-сущность с стабильным **`id`**. В БД — модель **`Order`** (`orders`). |
| **Версия** | Одна сделка может иметь несколько строк в `orders` с одним **`id`** и разным **`version`** (1..N). «Последняя версия» = максимальный `version` для данного `id`. |
| **`row_id`** | Технический PK строки в таблице `orders`; в API клиенту обычно не отдаётся. |
| **Покупатель / продавец** | Определяются полями `buyer_company_id`, `seller_company_id`; роль текущего пользователя в ответе — поле **`role`**: `buyer` \| `seller`. |

## Бэкенд: модель `Order`

- **Файл:** `backend/app/api/purchases/models/__init__.py`
- **Таблица:** `orders`

**Общие поля сделки:** `id`, `version`, `buyer_company_id`, `seller_company_id`, `buyer_order_number`, `seller_order_number`, `deal_type`, `status` (`Активная` / `Завершенная`), `comments`, суммы (`total_amount`, **`total_amount_excl_vat`** — сумма позиций qty×price **без НДС**; при `amount_with_vat_rate` итог с НДС: `total_amount` ≈ `total_amount_excl_vat` + `amount_vat_rate`), **`total_amount_word`** — сумма прописью на русском, синхронно с `total_amount`, только на сервере), `amount_vat_rate`, `amount_with_vat_rate`, `seller_vat_rate`, даты/номера основного договора (`contract_number`, `contract_date`), договора поставки (`supply_contracts_number`, `supply_contracts_date`), JSON `closing_documents`, `others_documents`, таймстемпы.

**Поля счёта (хранятся в `orders`, в JSON ответа собираются во вложенный объект `bill`):**

| Колонка в БД | Смысл |
|--------------|--------|
| `bill_number`, `bill_date` | Номер и дата счёта |
| `bill_officials` | JSON: должностные лица |
| `bill_reason` | Основание (`bill.reason`) |
| `payment_terms_contract`, `delivery_terms_contract` | Условия оплаты и поставки (блок «договор» в счёте) |
| `additional_info` | Доп. информация к счёту (общий блок) |
| `contract_terms_contract`, `contract_terms_text_contract` | Пресет и текст условий договора (`standard-delivery-supplier` \| `standard-delivery-buyer` \| `custom`) |
| `payment_terms_offer`, `contract_terms_offer`, `contract_terms_text_offer`, `additional_info_offer` | Аналогично для блока оферты |

**Позиции:** `OrderItem` (`order_items`), связь с заказом по `order_row_id`.

**Реквизиты банка в ответе API** приходят не из `Order`, а из связанных **`Company`** (`buyer_company` / `seller_company` в `DealResponse`): расчётный счёт, корсчёт, банк, БИК и т.д.

### Объект `bill` в API

Источник на бэке: **`BillInDealResponse`** (и **`BillUpdateInDeal`** для PATCH) в `backend/app/api/purchases/schemas/__init__.py`. Имена полей в JSON совпадают с колонками суффикса `_contract` / `_offer` (без отдельного префикса `bill_`, кроме логики «номер счёта»):

- `number` ← `bill_number`, `reason` ← `bill_reason`, `officials` ← `bill_officials`
- `payment_terms_contract`, `delivery_terms_contract`, `additional_info`, `contract_terms_contract`, `contract_terms_text_contract`
- `payment_terms_offer`, `contract_terms_offer`, `contract_terms_text_offer`, `additional_info_offer`

На фронте зеркало: **`BillResponse`** в `frontend/types/dealResponse.ts`. UI-состояние (`Deal.bill` в `dealState.ts`) использует camelCase; маппинг: **`frontend/utils/dealsMapper.ts`**.

## Префикс HTTP

Все маршруты ниже относительно:

- **`/api/v1/purchases`** — роутер подключается в `backend/app/api/v1/router.py` с `prefix="/purchases"`.
- Полный базовый путь: **`/api/v1/purchases`**.

Авторизация: **Bearer JWT** (как в остальном API), кроме случаев, где явно отключено в коде.

## Сводка API сделок

| Метод | Путь | Назначение |
|-------|------|------------|
| `POST` | `/deals` | Создать сделку. Тело: `DealCreate` (`seller_company_id`, `items`, …). Ответ: `DealResponse`. |
| `GET` | `/buyer/deals` | Список сделок для компании покупателя. Query: `skip`, `limit`. Ответ: `[BuyerDealResponse]` (кратко, без полных компаний). |
| `GET` | `/seller/deals` | Список для продавца. Ответ: `[SellerDealResponse]`. |
| `POST` | `/deals/by-ids` | Массово получить последние версии по `id`. Тело: `{ "ids": [1,2,3] }`. Ответ: `[DealResponse]`. |
| `GET` | `/deals/{deal_id}` | Последняя версия сделки по `deal_id`. Ответ: `DealResponse`. |
| `PUT` | `/deals/{deal_id}` | Обновить **последнюю версию** на месте (без новой версии). Тело: `DealUpdate`. Ответ: `DealResponse`. |
| `DELETE` | `/deals/{deal_id}` | Удалить **все версии** сделки с этим `id`. Ответ: `{ message, deal_id }`. |
| `POST` | `/deals/{deal_id}/versions` | Создать **новую версию** (копия + патч из тела). Тело: `DealUpdate`. Ответ: `DealResponse`. |
| `DELETE` | `/deals/{deal_id}/versions/last` | Удалить только последнюю версию. Ответ: `{ message, deal_id, deleted_version }`. |
| `POST` | `/deals/{deal_id}/bill` | Сгенерировать номер/дату счёта (опционально тело с `date`). |
| `POST` | `/deals/{deal_id}/contract` | Аналогично для договора. |
| `POST` | `/deals/{deal_id}/supply-contract` | Аналогично для договора поставки. |
| `POST` | `/checkout` | Создание заказа из корзины (checkout). Ответ: `DealResponse`. |
| `GET` | `/units` | Справочник единиц измерения. |
| `POST` | `/deals/{deal_id}/documents` | Загрузка файла (multipart, S3). |
| `GET` | `/deals/{deal_id}/documents` | Список документов. |
| `GET` | `/deals/{deal_id}/documents/{document_id}/download` | Скачивание. |
| `DELETE` | `/deals/{deal_id}/documents/{document_id}` | Удаление документа. |

Детали тел и схем: **`backend/app/api/purchases/schemas/__init__.py`** (`DealCreate`, `DealUpdate`, `DealResponse`, `CompanyInDealResponse`, `BuyerDealResponse`, `SellerDealResponse`, и т.д.). Swagger: **`/docs`** (OpenAPI **`/api/v1/openapi.json`**).

## Полный ответ сделки (`DealResponse`)

Источник правды на бэке: **Pydantic `DealResponse`** в `backend/app/api/purchases/schemas/__init__.py`.

На фронте зеркало: **`frontend/types/dealResponse.ts`** — `DealResponse`, `CompanyInDealResponse`, `ProductItemResponse`, `DealUpdate`, `BillResponse`.

Важно:

- В JSON поля компании часто с **aliases** (`company_id`, `owner_name`, `account_number`) — согласовано с Pydantic `serialization_alias`.
- Поле **`total_amount_word`** в `DealResponse` — пропись **`total_amount`** (рубли/копейки); в запросах создания/обновления не передаётся.
- Поле **`total_amount_excl_vat`** — на сервере хранится в `orders.total_amount_excl_vat`, в API отдаётся в `DealResponse` / списках сделок; сумма строк заказа без НДС (не передаётся клиентом в теле создания/обновления, пересчитывается при изменении позиций или сумм).
- Для списков покупателя/продавца используются **урезанные** типы `BuyerDealResponse` / `SellerDealResponse` — там **нет** вложенных `buyer_company`/`seller_company` с банками.

## Фронтенд: где смотреть код

| Назначение | Файл |
|------------|------|
| URL константы | `frontend/constants/urls.ts` |
| Вызовы API | `frontend/api/purchases.ts` (`usePurchasesApi`) |
| Типы API | `frontend/types/dealResponse.ts` |
| Состояние UI сделки (человекочитаемые имена полей) | `frontend/types/dealState.ts` (`Deal`, `Company`, `Bill`) |
| Маппинг API ↔ состояние | `frontend/utils/dealsMapper.ts` (`responseToDeal`, `createBodyForUpdate`) |
| Кэш / поиск сделок | `frontend/composables/useDeals.ts`, `frontend/stores/deals.ts` |

## Миграции Alembic

- Скрипты: **`backend/alembic/versions/`**.
- В некоторых окружениях колонка **`alembic_version.version_num`** имеет длину **32 символа**; **`revision`** в файле миграции не должен её превышать (иначе `alembic upgrade` упадёт на записи версии).

## Ключевые правила для изменений

1. **Создание новой версии** (`POST .../versions`) и **правка последней** (`PUT .../deals/{id}`) — разные сценарии; не путать с бизнес-логикой «одна версия».
2. **`deal_id` в URL** — это **бизнес-**`id` сделки, не `row_id`.
3. Правки в **схеме ответа** нужно синхронизировать: Pydantic в `schemas/__init__.py` + TypeScript в `dealResponse.ts` + при необходимости `dealsMapper.ts` и `dealState.ts` + колонки `Order` + миграция Alembic.
4. Примеры в Swagger для отдельных роутов могут быть **переопределены** в `backend/app/api/purchases/router.py` (константы `responses` / `_DEAL_RESPONSE_EXAMPLE`); при добавлении полей в ответ проверяй и их.

## Связанные файлы бэкенда

- Роуты: `backend/app/api/purchases/router.py`
- Сервис: `backend/app/api/purchases/services/__init__.py` (`DealService`)
- Репозиторий: `backend/app/api/purchases/repositories/__init__.py`
- Модели SQLAlchemy: `backend/app/api/purchases/models/__init__.py`

---

*Документ для агентов/разработчиков; при смене API обновляйте этот файл вместе с кодом.*
