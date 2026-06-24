# Сверка с GitHub: что сделал Сергей и что не влито

Проверка: **23.06.2026**, ветки `origin/preprod`, `Sapach`, `features/document-layer`, `origin/dev`.

## Вывод

**Код Сергея по счёту и редактору уже в `preprod`.** Ветка `Sapach` **не опережает** `preprod` (0 уникальных коммитов). Наоборот, в `preprod` есть работа поверх Sapach: договор поставки, спецификации, alembic, DOC/PDF с бэкенда.

Пробелы из [аудита кода](code-audit.md) — это **недоделки относительно расширенного ТЗ**, а не «забыли влить ветку».

## Ветки

| Ветка | Относительно `preprod` | Содержание |
|-------|------------------------|------------|
| `Sapach` | **0 коммитов впереди** | Старая точка; Bill, EditorMenu, useDeals — уже в preprod |
| `preprod` | текущая база | Bill/, SupplyContract/, useDeals, DOC/PDF, supply contract |
| `features/document-layer` | **+3 коммита** | API документов ЛК (`/api/documents`), не вкладка «Счет» |
| `origin/dev` | **+2 коммита** (только docs) | Исходники ТЗ, оценка часов — без кода счёта |

## Коммиты Bill/редактор в `preprod`

Примеры (уже влиты): `Bill`, `BillMenu`, `bill-contract`, `bill-offer`, `Contract terms editor`, `fill bill number and date`, `versioning editor`, `Supply contract management`.

## Что не влито, но входит в этап 3 (70k)

**`features/document-layer`** — API документов ЛК (`/api/documents`). Не влит в `preprod`. Для этапа 3 («Создать счет», договоры) — **в scope 70k**: либо merge этой ветки, либо свой API; отдельной оплаты нет.

Решение — при реализации этапа 3, до начала диалога «Создать счет».

## Текущая ветка разработки

`feature/etap1-schet-dorabotki-sergeya` — от `preprod`, этап 1 из [etap-01](etap-01-dorabotki-sergeya.md).
