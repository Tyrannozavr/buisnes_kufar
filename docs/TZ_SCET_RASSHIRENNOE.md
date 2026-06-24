# Расширенное ТЗ: полный scope 70 000 ₽

**Активная разработка:** этап 1 — [docs/schet/etap-01-dorabotki-sergeya.md](schet/etap-01-dorabotki-sergeya.md)  
**Ветка:** `feature/etap1-schet-dorabotki-sergeya` (от `preprod`)

---

## Scope

**70 000 ₽ = весь `ТЗ_Расширение.txt` клиента** — от ОКЕИ и checkout до трёх типов счёта, договора поставки, фото/сканов и таблиц «Услуги». Без доплат и без пунктов «снаружи».

Исходник: `dev/WinRAR ZIP archive/Заявка Счет/ТЗ_Расширение.docx` (текст: `…/ТЗ_Расширение.txt`).

| Роль | Поведение |
|------|-----------|
| **Поставщик** | Создаёт и редактирует документы |
| **Покупатель** | Просмотр бланка или сканов без редактирования |

---

## Git: Сергей доделал или не влили?

**Влито в `preprod`.** Ветка `Sapach` не опережает `preprod`. Bill, EditorMenu, useDeals, supply contract — уже в основной ветке.

**`features/document-layer`** — не влит; если нужен для этапа 3 (договоры), **входит в 70k**, merge по решению при реализации.

Подробно: [docs/schet/git-status.md](schet/git-status.md) · [code-audit.md](schet/code-audit.md)

---

## Этапы (70 000 ₽ = 10 + 20 + 20 + 20)

| Этап | Сумма | Содержание | Документ | Статус |
|------|-------|------------|----------|--------|
| **1** | **10 000 ₽** | Доработки Сергея: ЛК, баги счёта, «Заполнить данными», дефолты | [etap-01](schet/etap-01-dorabotki-sergeya.md) | ✅ |
| **2** | **20 000 ₽** | ОКЕИ, checkout, «Товары», «Заказ», счёт на оплату, фото/сканы | [etap-02](schet/etap-02-schet-na-oplatu.md) | ⏳ |
| **3** | **20 000 ₽** | «Создать счет», договор поставки, синхронизация заказа, фото/сканы | [etap-03](schet/etap-03-sozdanie-scheta-dogovor-postavki.md) | ⏳ |
| **4** | **20 000 ₽** | Счёт-договор, оферта, шаблоны, «Услуги», фото/сканы | [etap-04](schet/etap-04-schet-dogovor-oferta.md) | ⏳ |

Стоимость, сроки и таблица «что где»: [payment-and-schedule.md](schet/payment-and-schedule.md)

---

## Справочные материалы

| Документ | Содержание |
|----------|------------|
| [tz-requirements.md](schet/tz-requirements.md) | Полная карта ТЗ → этапы 1–4 |
| [code-audit.md](schet/code-audit.md) | Что есть в коде, пробелы |
| [git-status.md](schet/git-status.md) | Сверка веток GitHub |
| [DOCX_TEMPLATES_BACKEND.md](DOCX_TEMPLATES_BACKEND.md) | DOC/PDF с бэкенда |

---

*При расхождении с `.docx` приоритет у исходного ТЗ и согласования с заказчиком.*
