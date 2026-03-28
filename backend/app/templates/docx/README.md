# Шаблоны DOCX (docxtpl)

Здесь лежат файлы `.docx` для серверной генерации документов по сделке.

## Имена файлов и эндпоинты

Файл на диске должен совпадать с константой в [docx_template_service.py](../../api/purchases/services/docx_template_service.py).

| Файл шаблона | Эндпоинт |
|--------------|----------|
| `order.docx` | `GET /api/v1/purchases/deals/{deal_id}/documents/order.docx` |
| `bill.docx` | `GET /api/v1/purchases/deals/{deal_id}/documents/bill.docx` |
| `bill_contract.docx` | `GET /api/v1/purchases/deals/{deal_id}/documents/bill-contract.docx` |
| `bill_offer.docx` | `GET /api/v1/purchases/deals/{deal_id}/documents/bill-offer.docx` |

Замени содержимое на макеты из ТЗ. Контекст собирается на бэкенде из сделки (`DealResponse`); в шаблоне используется **Jinja2** так же, как в docxtpl.

Подробности про API и поля: [docs/DOCX_TEMPLATES_BACKEND.md](../../../../docs/DOCX_TEMPLATES_BACKEND.md).

Термины сделки, версии, роль buyer/seller, объект `bill` в API: [docs/DEAL_AGENT_CONTEXT.md](../../../../docs/DEAL_AGENT_CONTEXT.md).

---

## Поля сделки, доступные в шаблоне (модель ответа API)

Контекст для docx строится из **`DealResponse`** на бэкенде (`build_deal_docx_context`: `model_dump(mode="json", by_alias=True)` + даты `*_fmt` + форматирование сумм). Имена в Jinja совпадают с **ключами JSON** от `GET /api/v1/purchases/deals/{deal_id}` (с алиасами для вложенных объектов). **Числовые суммы** в docx (`total_amount`, `total_amount_excl_vat`, `amount_vat_rate`, `item.price` / `item.quantity` / `item.amount`, алиас `total`) приводятся к строкам вида **`100,000.00`** (запятая между разрядами, два знака после точки), а не к сырому `float` из JSON.

### Верхний уровень

| Поле в шаблоне | Примечание |
|----------------|------------|
| `id` | ID сделки (бизнес-`id`, не строка в БД) |
| `version` | Версия заказа |
| `buyer_company_id`, `seller_company_id` | ID компаний |
| `buyer_order_number`, `seller_order_number` | Номера заказов у покупателя / продавца |
| `status` | Строка: `Активная` / `Завершенная` |
| `total_amount` | Сумма (в docx — строка `100,000.00`) |
| `total_amount_excl_vat` | Сумма позиций без НДС (в docx — строка `100,000.00`) |
| `total_amount_word` | Та же сумма прописью (рубли и копейки), из API |
| `total_word` | Дублирует `total_amount_word` (удобный алиас в шаблоне) |
| `amount_vat_rate` | Сумма НДС (в docx — строка `100,000.00`) |
| `amount_with_vat_rate` | Учёт НДС в `total_amount` (bool) |
| `comments` | Комментарий |
| `contract_date`, `bill_date`, `supply_contracts_date` | В ISO-строках из JSON (как в API) |
| `contract_date_fmt`, `bill_date_fmt`, `supply_contracts_date_fmt` | Те же даты строкой **ДД.ММ.ГГГГ** (удобно в печать) |
| `created_at`, `updated_at` | ISO в JSON |
| `created_at_fmt`, `updated_at_fmt` | **ДД.ММ.ГГГГ** |
| `role` | `buyer` или `seller` — роль текущей компании в ответе |
| `closing_documents`, `others_documents` | Списки (сейчас часто пустые) |
| `contract` | Список договоров: элементы `number`, `date` (`{% for c in contract %}`) |
| `supply_contracts` | Список договоров поставки: `number`, `date` |
| `bill` | Объект счёта или `null` — см. ниже |
| `items` | Позиции заказа — см. ниже |
| `buyer_company`, `seller_company` | Реквизиты компаний — см. ниже |

В шаблоне: `{{ contract_date_fmt }}`, `{{ total_amount }}`, `{% if bill %}…{% endif %}`.

### `buyer_company` / `seller_company` (алиасы как в JSON)

В дампе с **serialization_alias** используй ключи **как в ответе API** (не внутренние имена Python):

| В шаблоне | Смысл |
|-----------|--------|
| `buyer_company.company_id` | ID компании (не `id`) |
| `buyer_company.company_name` | Название |
| `buyer_company.owner_name` | ФИО владельца (не `name`) |
| `buyer_company.slug` | Slug |
| `buyer_company.inn`, `phone`, `email` | |
| `buyer_company.legal_address`, `production_address`, `index`, `kpp` | |
| `buyer_company.account_number` | Расчётный счёт |
| `buyer_company.correspondent_bank_account`, `bank_name`, `bic` | Банк |
| `buyer_company.vat_rate` | Ставка НДС |

Для продавца — те же поля с префиксом `seller_company.` (например `{{ seller_company.inn }}`).

### `bill` (счёт)

Если счёт не заполнен, `bill` может быть `null` — оборачивай блок в `{% if bill %}…{% endif %}`.

| В шаблоне | Смысл |
|-----------|--------|
| `bill.number` | Номер счёта |
| `bill.reason` | Основание |
| `bill.payment_terms_contract`, `bill.delivery_terms_contract` | Условия оплаты и поставки |
| `bill.additional_info` | Доп. информация |
| `bill.contract_terms_contract` | Пресет: `standard-delivery-supplier` / `standard-delivery-buyer` / `custom` |
| `bill.contract_terms_text_contract` | Текст условий договора |
| `bill.payment_terms_offer`, `bill.contract_terms_offer`, `bill.contract_terms_text_offer`, `bill.additional_info_offer` | Блок оферты |
| `bill.officials` | Список должностных лиц |

Элемент `bill.officials`: `id`, `full_name`, `position` — в цикле `{% for o in bill.officials %}{{ o.full_name }}{% endfor %}`.

### `items` (позиции заказа)

В цикле `{% for item in items %}`:

| В шаблоне | Смысл |
|-----------|--------|
| `item.id`, `item.order_id` | Идентификаторы |
| `item.product_name`, `product_slug`, `product_description`, `product_article` | Товар |
| `item.logo_url` | URL логотипа |
| `item.quantity`, `unit_of_measurement`, `price`, `amount` | Количество, единица, цена, сумма строки (в docx `quantity` / `price` / `amount` — строки `100,000.00`) |
| `item.position` | Порядок в заказе |
| `item.created_at`, `item.updated_at` | ISO-строки |

### Договоры в массивах `contract` и `supply_contracts`

В цикле `{% for c in contract %}` или `{% for sc in supply_contracts %}`: `{{ c.number }}`, `{{ c.date }}` (дата в ISO-строке из JSON).

### Замечание про термины из [DEAL_AGENT_CONTEXT.md](../../../../docs/DEAL_AGENT_CONTEXT.md)

В документе для агентов описаны также поля модели **`Order`** в БД (например `deal_type`, колонки счёта). В шаблон DOCX попадает только то, что **есть в `DealResponse`** после сериализации. Если нужного поля нет в таблицах выше — его нужно сначала добавить в ответ API и в `build_deal_docx_context`, иначе в Jinja переменной не будет.

---

## Синтаксис Jinja2 в Word (docxtpl)

### Переменные и выражения

- **Вывод значения** — двойные фигурные скобки (пробелы вокруг выражения допустимы):

	```text
	{{ id }}
	{{ total_amount }}
	{{ buyer_company.company_name }}
	{{ bill.number }}
	```

- **Вложенные объекты** — через точку, как в Python: `buyer_company.inn`, `seller_company.legal_address`, `bill.payment_terms_contract`.

- **Элементы списка** — например позиции заказа: в **таблице** используй цикл с префиксом строки `{%tr for item in items %}` … `{%tr endfor %}` (см. ниже «Циклы и таблицы»). В **обычном тексте** достаточно `{% for item in items %}`. Поля: `{{ item.product_name }}`, `{{ item.quantity }}`, `{{ item.price }}` и т.д. (имена как в JSON сделки).

- **Фильтры** (по необходимости):

	```text
	{{ name|default('—') }}
	{{ value|round(2) }}
	```

	Список фильтров — как в Jinja2; для отсутствующих полей удобен `default`.

### Условия

```text
{% if bill %}
	Счёт № {{ bill.number }}
{% endif %}

{% if buyer_company %}
	{{ buyer_company.company_name }}
{% else %}
	—
{% endif %}
```

Если попытаться вывести переменную или поле, которого нет в переданном контексте для Jinja2/docxtpl, то вместо значения будет выведено пустое место (ничего). Ошибки не будет — поле просто не подставится. Тем не менее, если попытаться обратиться к несуществующему вложенному полю без проверки на наличие родителя (например, `{{ bill.number }}` когда `bill` отсутствует), то Jinja выдаст ошибку при генерации документа. Поэтому для вложенных полей всегда проверяй наличие объекта-родителя с помощью условия (`{% if bill %}{{ bill.number }}{% endif %}`): если `bill` не передан, генерация пройдёт без ошибок и без вывода значения.

### Циклы и таблицы

- **Обычный список в тексте:**

	```text
	{# Пример синтаксиса if / else в Jinja2: #}
	{% set total = 0 %}
	{% for item in items %}
	{{ loop.index }}. {{ item.product_name }} — {{ item.quantity }} {{ item.unit_of_measurement }}
	{% set total = total + item.amount %}
	{% if loop.last %}
	Сумма по позициям: {{ total }}
	{% else %}
	{# Здесь можно вставить альтернативный текст, если не последняя итерация #}
	{% endif %}
	{% endfor %}
	```

- **`loop`** — служебный объект, доступный только *внутри* блока цикла (`{% for … %}` или `{%tr for … %}` в таблице): `loop.index` (нумерация с 1), `loop.first`, `loop.last` и др.  
	- ❗ Переменные `loop.index`, `loop.last` и т.п. *невидимы вне цикла* — их можно использовать только между открытием и закрытием соответствующего цикла.

- **Таблица позиций заказа (шапка + повторяющиеся строки):** в docxtpl обычный `{% for item in items %}…{% endfor %}`, разнесённый по ячейкам, **не привязан к строке `<w:tr>` в XML** — при рендере все элементы `items` часто оказываются **в одной строке таблицы** (ячейки уезжают вправо). Нужны **теги уровня строки таблицы**: `{%tr for item in items %}` и **`{%tr endfor %}`** (см. [расширения docxtpl](https://docxtpl.readthedocs.io/en/latest/#extensions)). Пиши **`{%tr`** слитно (без пробела между `{%` и `tr`), затем пробел и тело тега: `{%tr for item in items %}`.

- **Как должна выглядеть таблица в Word:** одна строка — **шапка** (№, Товар, Кол-во, Ед., Цена, Сумма). Следующая строка — **единственная строка-шаблон** для данных: **все в одной строке таблицы** — в **первой ячейке** только `{%tr for item in items %}`, в **последней ячейке** только `{%tr endfor %}`, **между ними** по одной ячейке на каждое поле (`{{ loop.index }}`, `{{ item.product_name }}`, `{{ item.quantity }}`, `{{ item.unit_of_measurement }}`, `{{ item.price }}`, `{{ item.amount }}`). Для шести полей между тегами цикла нужно **восемь ячеек** в этой строке (открытие + 6 полей + закрытие). Если визуально нужна таблица из **шести** колонок под шапку, добавь **две узкие колонки** по краям под теги или объедини ячейки шапки так, чтобы число ячеек в строке данных совпадало с шапкой.

	Пример содержимого **одной** строки данных (8 ячеек):

	| `{%tr for item in items %}` | `{{ loop.index }}` | `{{ item.product_name }}` | `{{ item.quantity }}` | `{{ item.unit_of_measurement }}` | `{{ item.price }}` | `{{ item.amount }}` | `{%tr endfor %}` |

	Итого: **ровно одна строка таблицы** содержит и теги цикла, и все поля позиции. Строка дублируется для каждого `item`.

- **Неправильно:** три строки подряд — (1) только `{%tr for item in items %}`, (2) только данные, (3) только `{%tr endfor %}`. Так цикл разорван по разным `<w:tr>`, docxtpl не собирает одну повторяемую строку; возможны ошибки при генерации или пустые/лишние строки.

- **Закрытие цикла:** только `{%tr endfor %}`, не `{% endfor %}` — иначе Jinja сообщает о несовпадающем блоке.

- Вложенные таблицы, картинки, `RichText` — см. [документацию docxtpl](https://docxtpl.readthedocs.io/).

### Даты

В контексте уже есть:

- ISO-строки из `model_dump` для полей вроде `contract_date`, `created_at`;
- и отдельно строки **`contract_date_fmt`**, **`bill_date_fmt`**, **`supply_contracts_date_fmt`**, **`created_at_fmt`**, **`updated_at_fmt`** в формате **ДД.ММ.ГГГГ** (удобно вставлять без фильтров).

Пример:

```text
Дата: {{ bill_date_fmt }}
Договор от: {{ contract_date_fmt }}
```

### Комментарии (не попадут в итоговый документ)

```text
{# это комментарий для автора шаблона #}
```

### Пробелы и переносы

- Теги `{% ... %}` и `{{ ... }}` можно ставить в отдельных абзацах или в одной строке с текстом — лишние переносы иногда дают пустые строки; при необходимости подправь вручную после первой генерации.

---

## Ограничения Microsoft Word

- Строка плейсхолдера **`{{ ... }}` или `{% ... %}` не должна быть разбита Word на несколько «кусков» (runs) с разным форматированием — иначе docxtpl не найдёт шаблон. Набирай плейсхолдер **одним вводом**, без копипасты из разных стилей.
- После правок сохраняй `.docx` и проверяй скачивание с бэка.

---
