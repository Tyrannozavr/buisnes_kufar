# Расширенное ТЗ: раздел «Счет» (и договор поставки)

**Активная разработка:** этап 1 — [docs/schet/etap-01-dorabotki-sergeya.md](schet/etap-01-dorabotki-sergeya.md)  
**Ветка:** `feature/etap1-schet-dorabotki-sergeya` (от `preprod`)

---

## Scope

| Детально | Кратко |
|----------|--------|
| Закладка **«Счет»** — три типа: счёт на оплату, счёт-договор, счёт-оферта | **Договор поставки** — базовое ТЗ + экспорт |
| Инициатор — **поставщик** | Покупатель — просмотр / сканы без редактирования |

Исходник: `dev/WinRAR ZIP archive/Заявка Счет/ТЗ_Расширение.docx` (текст: `…/ТЗ_Расширение.txt`).

**Согласовано с клиентом: 70 000 ₽ = полный scope расширенного ТЗ** (счёт ×3, договор поставки, фото/сканы, экспорт, диалог «Создать счет»). Без доплат и «опциональных» вынесений.

---

## Git: Сергей доделал или не влили?

**Влито в `preprod`.** Ветка `Sapach` не содержит коммитов, которых нет в `preprod`. Bill, EditorMenu, useDeals, supply contract — уже в основной ветке.

**Не влито:** `features/document-layer` (+3 коммита, API документов ЛК) — отдельно от вкладки «Счет».

Подробно: [docs/schet/git-status.md](schet/git-status.md)  
Аудит кода vs ТЗ: [docs/schet/code-audit.md](schet/code-audit.md)

---

## Этапы реализации (70 000 ₽)

| Этап | Сумма | Документ | Статус |
|------|-------|----------|--------|
| 1 | **10 000 ₽** | [Доработки Сергея](schet/etap-01-dorabotki-sergeya.md) | 🔄 в работе |
| 2 | **20 000 ₽** | [Счет на оплату + экспорт](schet/etap-02-schet-na-oplatu.md) | ⏳ |
| 3 | **20 000 ₽** | [«Создать счет» + договор поставки](schet/etap-03-sozdanie-scheta-dogovor-postavki.md) | ⏳ |
| 4 | **20 000 ₽** | [Счет-договор + оферта + шаблоны](schet/etap-04-schet-dogovor-oferta.md) | ⏳ |

Стоимость и сроки: [docs/schet/payment-and-schedule.md](schet/payment-and-schedule.md)

---

## Справочные материалы

| Документ | Содержание |
|----------|------------|
| [tz-requirements.md](schet/tz-requirements.md) | Требования ТЗ §1–9 (кратко) |
| [code-audit.md](schet/code-audit.md) | Что есть в коде, пробелы, пути к файлам |
| [git-status.md](schet/git-status.md) | Сверка веток GitHub |
| [DOCX_TEMPLATES_BACKEND.md](DOCX_TEMPLATES_BACKEND.md) | DOC/PDF с бэкенда |

---

*При расхождении с `.docx` приоритет у исходного ТЗ и согласования с заказчиком.*
