# API форм документов редактора (для фронтенда / Сергей)

Эндпоинты для сохранения и загрузки JSON-форм документов по сделке (заказ, счёт, договор и т.д.). Одна запись на пару «сделка + тип документа».

## Базовый URL

- Префикс: **`/api/v1/purchases`**
- Все запросы требуют авторизации (Bearer token).

Пример базового URL бэкенда: `http://localhost:8012` (или ваш `DEV_BACKEND_PORT`).

---

## Типы документов (`document_type`)

Допустимые значения (вкладки редактора):  
`order`, `bill`, `supply_contract`, `act`, `invoice`, `contract`, `others`.

При необходимости список можно расширить на бэкенде в `app.api.documents.service` и `schemas.DOCUMENT_TYPES`.

---

## GET — загрузить форму документа

**Запрос:**  
`GET /api/v1/purchases/{deal_id}/documents/{document_type}`

**Пример curl:**

```bash
# Подставьте свой TOKEN и deal_id (id сделки = orders.id)
curl -s -X GET "http://localhost:8012/api/v1/purchases/1/documents/order" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Ответ 200:**

```json
{
  "deal_id": 1,
  "document_type": "order",
  "payload": { "items": [], "comment": "" },
  "updated_at": "2026-01-31T12:00:00",
  "updated_by_company_id": 5
}
```

- Если записи ещё нет — вернётся `payload: {}`, `updated_by_company_id: null`.
- **Для диалога «Контрагент изменил данные»**: если `updated_by_company_id !== company_id` текущего пользователя и `updated_at` новее, чем последний раз видел пользователь — показать кнопку «Обновить данные?».

**Ошибки:** 404 (сделка не найдена или нет доступа), 400 (неверный `document_type`).

---

## PUT — сохранить форму документа

**Запрос:**  
`PUT /api/v1/purchases/{deal_id}/documents/{document_type}`  
Тело: JSON `{ "payload": { ... } }` — произвольный объект формы.

**Пример curl:**

```bash
curl -s -X PUT "http://localhost:8012/api/v1/purchases/1/documents/order" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"payload":{"items":[{"name":"Товар 1","qty":2}],"comment":"Тест"}}'
```

**Ответ 200:** тот же формат, что и GET (с обновлёнными `payload`, `updated_at`, `updated_by_company_id` = company текущего пользователя).

**Ошибки:** 404 (сделка не найдена или нет доступа), 400 (неверный `document_type`).

---

## Кратко для фронта (Сергей)

1. **При открытии вкладки редактора** (по ссылке из Продаж/Закупок): делайте **GET** с `deal_id` и `document_type` (order, bill, …). Подставляйте данные в форму из `payload`.
2. **Кнопка «Сохранить документ»**: делайте **PUT** с тем же `deal_id` и `document_type`, в теле — `{ "payload": <данные формы> }`.
3. **Диалог «Контрагент изменил?»**: храните на клиенте `lastSeenUpdatedAt`; если в ответе GET `updated_by_company_id !== ваша company_id` и `updated_at > lastSeenUpdatedAt` — показать «Данные обновлены контрагентом. Обновить?».
4. Структура `payload` — на ваше усмотрение (заказ, счёт, договор и т.д.); бэкенд хранит JSON как есть.

---

## Запуск тестов и проверка API

- **Юнит-тесты** (репозиторий + сервис): требуют запущенную БД. Из корня backend:  
  `python -m pytest tests/test_documents_repository.py tests/test_documents_service.py -v`
- **Миграция** таблицы `deal_document_forms`:  
  `alembic upgrade head`
- **Проверка через curl**: после логина возьмите `access_token` и подставьте в примеры выше; убедитесь, что `deal_id` принадлежит сделке, где ваша компания — покупатель или продавец.
- **Скрипт** из корня репо:  
  `./scripts/test_documents_api.sh http://localhost:8012 "YOUR_ACCESS_TOKEN" 1`

## Проверка в браузере

После интеграции на фронте: открыть редактор по ссылке из Закупок/Продаж (с `deal_id` в маршруте или query), открыть вкладку «Заказ» — форма должна подгрузиться GET; нажать «Сохранить изменения» — отправить PUT и обновить данные. При изменении контрагентом — показывать «Обновить данные?» по `updated_by_company_id` и `updated_at`.
