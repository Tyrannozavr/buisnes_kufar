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
- Ключевые поля: `id`, `version`, `buyer_company_id`, `seller_company_id`, `buyer_order_number`, `seller_order_number`, `status` (`Активная` / `Завершенная`), суммы (`total_amount`, `amount_vat_rate`, `amount_with_vat_rate`), комментарии, даты/номера договора, счёта, договора поставки, JSON для закрывающих/прочих документов, поля счёта (`bill_*`, `payment_terms`, `additional_info`, `bill_officials`), `seller_vat_rate`.
- **Позиции:** `OrderItem` (`order_items`), связь с заказом по `order_row_id`.
- **Реквизиты банка в ответе API** приходят не из `Order`, а из связанных **`Company`** (`buyer_company` / `seller_company` в `DealResponse`): расчётный счёт, корсчёт, банк, БИК и т.д.

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
- Для списков покупателя/продавца используются **урезанные** типы `BuyerDealResponse` / `SellerDealResponse` — там **нет** вложенных `buyer_company`/`seller_company` с банками.

## Фронтенд: где смотреть код

| Назначение | Файл |
|------------|------|
| URL константы | `frontend/constants/urls.ts` |
| Вызовы API | `frontend/api/purchases.ts` (`usePurchasesApi`) |
| Типы API | `frontend/types/dealResponse.ts` |
| Состояние UI сделки (человекочитаемые имена полей) | `frontend/types/dealState.ts` (`Deal`, `Company`) |
| Маппинг API ↔ состояние | `frontend/utils/dealsMapper.ts` (`responseToDeal`, `createBodyForUpdate`) |
| Кэш / поиск сделок | `frontend/composables/useDeals.ts` (если есть) |

## Ключевые правила для изменений

1. **Создание новой версии** (`POST .../versions`) и **правка последней** (`PUT .../deals/{id}`) — разные сценарии; не путать с бизнес-логикой «одна версия».
2. **`deal_id` в URL** — это **бизнес-**`id` сделки, не `row_id`.
3. Правки в **схеме ответа** нужно синхронизировать: Pydantic в `schemas/__init__.py` + TypeScript в `dealResponse.ts` + при необходимости `dealsMapper.ts` и `dealState.ts`.
4. Примеры в Swagger для отдельных роутов могут быть **переопределены** в `backend/app/api/purchases/router.py` (константы `responses` / `_DEAL_RESPONSE_EXAMPLE`); при добавлении полей в ответ проверяй и их.

## Связанные файлы бэкенда

- Роуты: `backend/app/api/purchases/router.py`
- Сервис: `backend/app/api/purchases/services/__init__.py` (`DealService`)
- Репозиторий: `backend/app/api/purchases/repositories/__init__.py`
- Модели SQLAlchemy: `backend/app/api/purchases/models/__init__.py`

---

*Документ сгенерирован для агентов/разработчиков; при смене API обновляйте этот файл вместе с кодом.*
