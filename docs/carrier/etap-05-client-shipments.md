# Этап 5 — E. Перевозки клиента

**Статус:** ✅ код · ✅ приёмка 2026-08-12  
**Ветка:** `feature/carrier-tz`  
**ТЗ:** [tz-requirements.md](tz-requirements.md) §E  
**Ручной чек-лист:** [manual-step-by-step-acceptance.md](manual-step-by-step-acceptance.md) §E

## Scope

| Задача | Детали | Статус |
|--------|--------|--------|
| Таблица | номер `00000`, дата, перевозчик, договор-stub, груз, транспорт, заказ | ✅ |
| Груз | PATCH cargo, edit только клиент | ✅ |
| 1:1 заказ | PATCH deal → активный Order | ✅ |
| UI | `/profile/shipments` | ✅ |

## Приёмка

- [x] Нумерация и груз
- [x] Договор перевозки — заглушка (вне scope)
