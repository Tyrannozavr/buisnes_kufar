# ТЗ_15 — «Изменения сайта» (роли, контрагенты, перевозки, таблицы Продаж)

## Оригинал ТЗ

| Что | Ссылка / путь |
|-----|----------------|
| **Файл в репозитории** | [ТЗ_Изменения.docx](./ТЗ_Изменения.docx) |
| Текст (извлечённый) | [TZ_15.txt](./TZ_15.txt) |
| Исходник у разработчика | `/home/dmiv/Загрузки/ ТЗ_Изменения (2).docx` (тот же SHA-256; алиас `ТЗ_15.07`) |

**Не путать** с [../schet/](../schet/) — там закрыт другой пакет 70k (`ТЗ_Расширение`, счёт).

**Ориентир объёма:** ~**80 000 ₽** = 4 этапа по **20k** (как этапы 2–4 счёта).  
Тяжёлая логистика «как продукт» (матчинг рейсов, полный поиск) — **MVP-заглушки** в этапах 5/8; полный движок — вне этого пакета.

## Этапы

| Этап | Сумма | Тема | Статус |
|------|-------|------|--------|
| **5** | 20k | Роли · меню · Перевозчик/Экспедитор · Поиск транспорта (stub) | ✅ [etap-05](etap-05-roles-nav-carriers.md) |
| **6** | 20k | Контрагенты · Перевозчики · «Добавить контрагента» · Документы | ✅ [etap-06](etap-06-counterparties.md) |
| **7** | 20k | Данные заполнения (адреса) · вес товара · «Заполнить данными» без проверок | ✅ [etap-07](etap-07-company-fill-product.md) |
| **8** | 20k | Таблица «Продажи» по ТЗ_15 · диалоги «Создать документ» · перевозка MVP | ✅ [etap-08](etap-08-sales-table-dialogs.md) |

**Пакет TZ15 (5–8) закрыт.** Мастер-чеклист: [manual-full-acceptance-checklist.md](manual-full-acceptance-checklist.md) ✅

## Новый ПК — seed для приёмки

```bash
docker compose -f docker-compose.dev.yml up -d
bash scripts/seed_acceptance_users.sh
```

Создаёт `seller` / `buyer` / `carrier` / `forwarder` (+ сделки, договоры). Пароль: `123456`. Подробнее: [test-users.md](test-users.md).

## Справочники

- [tz-requirements.md](tz-requirements.md) — карта пунктов ТЗ → этап
- [manual-etap-05-checklist.md](manual-etap-05-checklist.md) — ручная приёмка этапа 5
- [manual-etap-06-checklist.md](manual-etap-06-checklist.md) — ручная приёмка этапа 6
- [manual-etap-07-checklist.md](manual-etap-07-checklist.md) — ручная приёмка этапа 7
- [manual-etap-08-checklist.md](manual-etap-08-checklist.md) — ручная приёмка этапа 8
- [manual-full-acceptance-checklist.md](manual-full-acceptance-checklist.md) — мастер-чеклист TZ15
- Аккаунты: [test-users.md](test-users.md) · [../schet/test-users.md](../schet/test-users.md)

## Порядок работы

1. Реализовать **один** подпункт `§N.M` (как в правиле этапов счёта).
2. Dev-стек → миграции → тесты → seed → обновление `etap-0N` + чек-листа.
3. Не мержить в `preprod` / `master` без явной просьбы.
