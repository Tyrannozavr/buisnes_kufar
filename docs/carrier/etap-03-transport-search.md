# Этап 3 — C. Поиск транспорта

**Статус:** ✅  
**Ветка:** `feature/carrier-tz`  
**ТЗ:** [tz-requirements.md](tz-requirements.md) §C  
**Ручной чек-лист:** [manual-step-by-step-acceptance.md](manual-step-by-step-acceptance.md) §C

## Scope

| Задача | Детали | Статус |
|--------|--------|--------|
| API матчинга ТС | `POST /api/v1/transport/search` | ✅ |
| Автозаявки | 1 перевозчик → 1 заявка, N matched vehicles | ✅ |
| UI | `/transport-search` фильтры + карточки + контакты/избранное/заявка | ✅ |
| Активация | `POST .../vehicles/{id}/send-request` | ✅ |
| Тесты | `test_carrier_transport_flow.py` | ✅ |

## Приёмка

- [x] Поиск по ТС, не по компаниям
- [x] Пассивные заявки + активный отклик
