# Этап 4 — D. Заявки перевозчика

**Статус:** ✅ код · ✅ приёмка 2026-08-12  
**Ветка:** `feature/carrier-tz`  
**ТЗ:** [tz-requirements.md](tz-requirements.md) §D  
**Ручной чек-лист:** [manual-step-by-step-acceptance.md](manual-step-by-step-acceptance.md) §D

## Scope

| Задача | Детали | Статус |
|--------|--------|--------|
| Лента заявок | `GET /api/v1/transport/requests`, highlight, sort | ✅ |
| TTL 14 суток | Celery beat + `purge_expired_requests` | ✅ |
| Принять | shipment + контрагенты + чат | ✅ |
| UI | `/profile/shipment-requests` | ✅ |

## Приёмка

- [x] Активная заявка подсвечена
- [x] Accept создаёт перевозку и связи
