# Этап 1 — A. ЛК «Транспорт»

**Статус:** ✅  
**Ветка:** `feature/carrier-tz`  
**ТЗ:** [tz-requirements.md](tz-requirements.md) §A · `1_Страница_Транспорт.docx`  
**Ручной чек-лист:** [manual-step-by-step-acceptance.md](manual-step-by-step-acceptance.md) §A

## Scope

| Задача | Детали | Статус |
|--------|--------|--------|
| Поля ТС | Откуда/Куда, грузоподъёмность, объём, марка, номера, габариты п/п, дата, тип кузова, загрузка, ADR, догруз | ✅ |
| Справочники | `GET /api/v1/company/fleet-dictionaries` | ✅ |
| CRUD + confirm delete | UI `/profile/transport` | ✅ |
| Подсказки «?» | Откуда / Куда | ✅ |
| Тесты | `test_fleet_api.py` | ✅ |

## Приёмка

- [x] Полная карточка ТС сохраняется и отображается в списке
- [x] Справочники доступны в форме
- [x] Удаление с подтверждением
