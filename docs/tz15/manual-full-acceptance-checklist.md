# TZ15 — мастер-чеклист приёмки (этапы 5–8)

**Статус ручной проверки:** ✅ готов к приёмке (15.07.2026, ветка `preprod`)

**Dev UI:** http://localhost:3014 · **API:** http://localhost:8014  
**Пароль:** `123456`

| Роль | Email |
|------|-------|
| Поставщик | `seller@gmail.com` |
| Покупатель | `buyer@gmail.com` |
| Перевозчик | `carrier@gmail.com` |
| Экспедитор | `forwarder@gmail.com` |

**Seed на новом ПК:** `bash scripts/seed_acceptance_users.sh` · аккаунты: [test-users.md](test-users.md)

Подробные пошаговые сценарии: [manual-etap-05-checklist.md](manual-etap-05-checklist.md) · [manual-etap-06-checklist.md](manual-etap-06-checklist.md) · [manual-etap-07-checklist.md](manual-etap-07-checklist.md) · [manual-etap-08-checklist.md](manual-etap-08-checklist.md)

---

## Этап 5 — роли и меню ✅

- [x] Меню: Продавцы, Перевозчики, Поиск транспорта; нет «Новости»
- [x] Торговая деятельность: 4 роли; нет «Род деятельности»
- [x] Перевозчик/Экспедитор: скрыты Продукция, Продажи, Закупки
- [x] Stub-разделы ЛК логистики открываются

## Этап 6 — контрагенты ✅

- [x] «Контрагенты», «Перевозчики», «Добавить контрагента»
- [x] «Посмотреть договоры» → Документы с фильтром
- [x] Документы — единая таблица + фильтры
- [x] `/profile/counterparties` → редирект на `/profile/partners`

## Этап 7 — данные заполнения ✅

- [x] `/profile` — вкладки «Данные компании» / «Данные заполнения»
- [x] CRUD адресов погрузки/приёма + default
- [x] Продукция: вес нетто/брутто, нет радио Товар/Услуга
- [x] «Заполнить данными» без блокировки по реквизитам (seller); buyer — disabled

## Этап 8 — таблица Продажи ✅

- [x] 7 колонок ТЗ_15 на «Товары»
- [x] «Создать документ» везде
- [x] Диалог замены счёта
- [x] Диалог договор/спека
- [x] Перевозка MVP + «Найти транспорт»
- [x] Закрывающие документы MVP

---

## Матрица: роль × раздел

| Раздел | seller | buyer | carrier | forwarder |
|--------|--------|-------|---------|-----------|
| Данные компании / заполнения | ✓ | ✓ | ✓ | ✓ |
| Продукция | ✓ | — | скрыто | скрыто |
| Продажи / Закупки | ✓ | ✓ | скрыто | скрыто |
| Контрагенты | ✓ | ✓ | ✓ | ✓ |
| Документы | ✓ | ✓ | ✓ | ✓ |
| Транспорт / Водители (stub) | — | — | ✓ | ✓ |

---

## MVP-ограничения (вне претензий)

- Полный бланк договора перевозки / УПД — stub в редакторе
- Биржа транспорта / матчинг грузов — stub «Поиск транспорта»
- Адреса fill пока не подставляются в шаблоны Bill/Order (только CRUD + UI)

---

## Автотесты (прогон)

```bash
docker compose -f docker-compose.dev.yml exec backend poetry run python -m pytest \
  tests/test_company_fill_addresses_api.py \
  tests/test_product_weights.py \
  tests/test_etap8_sales_columns_api.py \
  tests/test_company_contracts_api.py -v
docker compose -f docker-compose.dev.yml exec frontend npm run build
bash scripts/tz15_api_smoke.sh
```

---

## Деплой на сервер (preprod / prod)

1. **Pull** ветки `preprod`, пересобрать контейнеры.
2. **Миграции:** `docker compose exec backend poetry run alembic upgrade head` (не `stamp` при ошибке).
3. **Seed:** `docker compose exec backend poetry run python scripts/ensure_schet_test_users.py` (на prod — только если нужны тест-аккаунты).
4. **Frontend:** `npm run build` в образе или CI.
5. **Smoke:** `API_BASE=https://<host> bash scripts/tz15_api_smoke.sh`.
6. **Ручная приёмка:** пройти чек-листы этапов 5–8 от 4 ролей (см. таблицу выше).

### Результаты прогона (15.07.2026, preprod локально)

| Проверка | Результат |
|----------|-----------|
| Merge `feature/etap7-company-fill-product` → `preprod` | ✅ `ad9ca0f` + smoke script |
| pytest TZ15 (10 тестов) | ✅ passed |
| `npm run build` | ✅ |
| `scripts/tz15_api_smoke.sh` (11 эндпоинтов) | ✅ |
| Browser: seller / buyer / carrier | ✅ меню, продажи/закупки, контрагенты |
| `/profile/counterparties` | ✅ редирект → `/profile/partners` |

### Известные ограничения (не блокер деплоя)

- **MVP:** редактор договора перевозки / УПД — stub; «Поиск транспорта» — stub.
- **Fill-адреса** не подставляются в шаблоны Bill/Order (только CRUD).
- **Dependabot:** на GitHub ~63 уязвимости (1 critical) в зависимостях — просмотреть перед prod.
- **pytest** `test_purchases_units.py`, `test_checkout_api.py` — устаревший teardown/cleanup (не регрессия TZ15).
- **Меню ЛК:** краткая «вспышка» полного меню до загрузки `trade_activity` у перевозчика/экспедитора.
