# Аудит кода: что есть и чего не хватает (preprod)

Сверка с репозиторием на **23.06.2026**. Подробнее про Git — [git-status.md](git-status.md).

| Компонент | Статус | Комментарий |
|-----------|--------|-------------|
| `Bill/Bill.vue`, `Bill-Contract.vue`, `Bill-Offer.vue` | Частично | Общая таблица + переключение типа через `BillMenu`; бланки счёт-договор/оферта — каркас |
| `BillMenu.vue` | Частично | Тип документа, НДС, основание, срок оплаты, условия договора; дефолты и связь с бланком — не по ТЗ |
| Номер/дата счёта, `createBill`, `useDeals` | Есть | Из таблицы и из заказа («СЧЕТ на основании») |
| Сохранение payload счёта | Есть | Через `stores/deals` + API сделки |
| `CompanyPaymentsSection`, должностные лица | Частично | Платежные поля есть; **20% НДС** в списке отсутствует; индекс — проверить в форме компании |
| `SupplyContract/SupplyContract.vue` | Ок+ | Базовый договор + спецификации в `GoodsColumns` |
| Печать / DOC / PDF | Есть | `EditorMenu/index.vue` → бэкенд (docxtpl + Gotenberg), см. `docs/DOCX_TEMPLATES_BACKEND.md` |
| Диалог «Создать счет» с договорами | Нет | Сразу `createBill` в `GoodsColumns.vue` |
| «Заполнить данными» | Неверно | `InsertButtons.vue` — переход на **последнюю** сделку, не подстановка в **текущую** |
| Редактор шаблонов условий | Каркас | `BillContractTermsEditor.vue`; без бэкенда и seed-шаблонов |
| Фото/сканы | Нет | Заглушка `inDevelopment()` |
| Новый счёт «только номер и дата» | Нет | `fillBillData()` подтягивает всё из сделки при открытии |
| Верхняя таблица реквизитов счёта | Баг | В `Bill.vue` банковский блок привязан к `buyer`, должно быть к **seller** |

## Связанные файлы

| Назначение | Путь |
|------------|------|
| Бланк счёта | `frontend/components/templates/Bill/Bill.vue` (+ `Bill-Contract.vue`, `Bill-Offer.vue`) |
| Меню счёта | `frontend/components/EditorMenu/BillMenu.vue` |
| «Заполнить данными» | `frontend/components/EditorMenu/InsertButtons.vue` |
| Редактор, вкладки | `frontend/pages/profile/editor/index.vue` |
| Меню редактора | `frontend/components/EditorMenu/index.vue` |
| Таблица «Продажи» | `frontend/components/tables/GoodsColumns.vue` |
| Договор поставки | `frontend/components/templates/SupplyContract/SupplyContract.vue` |
| Сделки / счёт | `frontend/composables/useDeals.ts`, `frontend/stores/deals.ts` |
| DOC/PDF | `frontend/composables/useDocxGenerator.ts` |
| API сделок/счёта | `backend/app/api/purchases/router.py` |
| Платежные реквизиты | `frontend/components/company/CompanyPaymentsSection.vue` |
| Текст ТЗ (исходник) | `dev/WinRAR ZIP archive/Заявка Счет/ТЗ_Расширение.txt` |
