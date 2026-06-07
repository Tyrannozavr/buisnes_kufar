# Боевой чеклист: отдельные договоры и спецификации

Этот чеклист рассчитан на внедрение в текущем проекте:
- договор поставки хранится отдельной сущностью;
- спецификация хранится отдельно и ссылается на договор;
- заказ (`Order`) хранит ссылки на договор/спецификацию, а не саму бизнес-сущность договора.

---

## 0) Подготовка и страховка

- [x] Создать отдельную git-ветку.
- [x] Зафиксировать состояние миграций: `alembic current`, `alembic heads`.
- [x] Сделать бэкап локальной БД.
- [x] Собрать список мест, где используются `supply_contract_*` в `Order`:
	- `models`
	- `schemas`
	- `repositories`
	- `services`
	- фронтовые мапперы/типы.

Почему это важно: если что-то пойдет не так, быстро откатитесь и не потеряете данные.

---

## 1) Зафиксировать бизнес-правила до кода

- [x] На одну пару компаний может быть только 1 активный договор или несколько?
Один
- [x] Что считается "договор действует": только `status=active` или еще проверка срока?
Если у него есть номер договора и дата
- [x] Можно ли создавать спецификацию без договора?
нет
- [x] Номер договора уникален глобально или в рамках пары компаний?
в рамках пары компаний
- [x] Номер спецификации уникален в рамках договора?
да
- [x] Можно ли создавать заказ без спецификации?
да

Почему это важно: от ответов зависят индексы, ограничения и валидация.

---

## 2) Проектирование таблиц

- [x] Таблица `supply_contract` (договоры):
	- `id`
	- `buyer_company_id`
	- `seller_company_id`
	- `number`
	- `date`,
	- specifications
	- `terms_text`
	- `officials_json`
- [x] Таблица `supply_contract_specification` (спецификации):
	- `id`
	- `supply_contract_id`
	- `spec_number`, `spec_date`
	- `spec_text`
- [x] Таблица `specification_item` (позиции спецификации):
	- `id`
	- `specification_id`
	- `name`, `article`
	- `quantity`, `units`, `price`, `amount`
	- `position`.
- [x] В `orders` добавить nullable ссылки:
	- `supply_contract_id`
	- `supply_spec_id`.

Комментарий: nullable на старте нужен для безболезненной миграции.

---

## 3) SQLAlchemy модели

Файлы:
- `backend/app/api/purchases/models/__init__.py`
- `backend/app/db/base.py` (регистрация моделей в metadata)

Чек:
- [x] Добавлены модели `SupplyContract`, `SupplyContractSpecification`, `SpecificationItem`.
- [x] Добавлены relationships:
	- `SupplyContract -> specifications`
	- `SupplyContractSpecification -> spec_items`
- [x] Добавлены FK-поля и relationships в `Order`.
- [x] Продуманы `ondelete` (`SET NULL`/`CASCADE`) под вашу бизнес-логику.

---

## 4) Alembic миграция

- [x] Создана миграция с новыми таблицами (`d5802d7ceb54`, `a7c3e1f92b04`).
- [x] В `orders` добавлены `supply_contract_id`, `supply_spec_id`.
- [x] Добавлены FK и индексы:
	- unique `(seller_company_id, buyer_company_id, number)` на `supply_contract`
	- unique `(supply_contract_id, spec_number)` на `supply_contract_specification`
	- индекс `(buyer, seller, status)` — **не нужен** (нет поля `status`, действует по номеру+дате)
- [ ] Проверены вручную `upgrade()` и `downgrade()`.
- [x] Миграция прогнана на БД с данными (head = `a7c3e1f92b04`).

Комментарий: автоген Alembic часто надо вручную подправлять.

---

## 5) Pydantic схемы

Файл:
- `backend/app/api/purchases/schemas/__init__.py`

Чек:
- [x] Добавлены:
	- `SupplyContractCreate` / `SupplyContractUpdate` / `SupplyContractResponse`
	- `SpecificationCreate` / `SpecificationUpdate` / `SpecificationResponse`
	- `SpecificationItem`
	- `SupplyContractExistsResponse`
- [x] Валидация `buyer != seller` в `SupplyContractCreate` (`@model_validator`)
- [x] Схемы согласованы с endpoint'ами (id в path, не дублировать company ids в Update)
- [x] Проверить/выровнять `SpecificationResponse.supply_contract_id` (тип и имя поля для API)
- [x] `quantity >= 0`, `price >= 0`, `amount >= 0` в `SpecificationItem` (есть)
- [x] (опционально) validator `amount == quantity * price`

---

## 6) Repository слой

> **Если ты впервые на бэке** — прочитай блок «Для новичка» ниже целиком, потом возвращайся к чеклисту методов.

Файл:
- `backend/app/api/purchases/repositories/supply_contract.py`

Класс: `SupplyContractRepository(session: AsyncSession)`

Образец для подражания (тот же стиль кода):
- `backend/app/api/purchases/repositories/__init__.py` → класс `DealRepository`

---

### Для новичка: что такое Repository и зачем он нужен

**Repository (репозиторий)** — слой, который **единственный** в твоём модуле ходит в базу данных за договорами поставки.

Представь цепочку запроса от браузера до PostgreSQL:

```
Клиент (JSON)
  → Router (URL, HTTP-код ответа)
    → Service (бизнес-правила: «один договор на пару», ошибка 409)
      → Repository (SQL: SELECT / INSERT / UPDATE)
        → PostgreSQL
```

**Repository не знает про HTTP.** Он не возвращает `404` и не знает про FastAPI.  
Он говорит простым языком: «вот объект из БД» или «ничего не нашёл» (`None`).

**Service не пишет SQL.** Он вызывает методы репозитория и решает, что ответить клиенту.

---

### Словарь терминов (минимум)

| Термин | Простыми словами |
|--------|------------------|
| **ORM** | Python-класс (`SupplyContract`), который соответствует строке в таблице БД. Поля класса = колонки таблицы. |
| **Session** | «Рабочая сессия» с БД. Через неё делаешь запросы. Передаётся в конструктор репозитория. |
| **AsyncSession** | То же, но асинхронно (`async def`, `await`) — не блокирует сервер, пока БД думает. |
| **select** | SQL-запрос на чтение (аналог `SELECT ... FROM ...`). |
| **add** | «Запомни новый объект, потом сохраним в БД» (ещё не INSERT). |
| **flush** | Отправить изменения в БД **в рамках транзакции**, чтобы получить `id` новой строки. |
| **commit** | **Окончательно сохранить** все изменения в БД. До commit данные могут откатиться. |
| **selectinload** | **Eager load** — сразу подтянуть связанные таблицы (спецификации, товары), чтобы не делать 100 мелких запросов. |
| **Optional[T]** | Либо объект типа T, либо `None` («не найдено»). |
| **Pydantic-схема** | Контракт JSON для API. **Не путать** с ORM-моделью — это разные классы с похожими именами. |

---

### Три правила твоего репозитория

1. **Возвращай ORM, не Pydantic.**  
   `return contract` (тип `SupplyContract`), а не `SupplyContractResponse`.  
   Превращение ORM → JSON-схема — работа **Service**.

2. **Проверяй доступ через `company_id`.**  
   Договор видят только buyer и seller. Если чужая компания — верни `None`, не объект.

3. **После записи — перечитай из БД.**  
   Паттерн из `DealRepository`: `add` → `flush` → `commit` → снова `get_*` с `selectinload`.  
   Так ты вернёшь объект уже со всеми связями (specifications, items).

**HTTP-коды (403, 404, 409)** — не в repository. Repository только возвращает данные или `None`.

---

### Минимальный каркас класса (от чего начать)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.purchases.models import SupplyContract, SupplyContractSpecification
from app.api.purchases.models import SpecificationItem as SpecificationItemModel


class SupplyContractRepository:
	def __init__(self, session: AsyncSession):
		self.session = session  # сохраняем сессию — через неё все запросы к БД
```

Дальше добавляешь методы по одному и **сразу проверяешь** (pytest или временный вызов из консоли).

---

### Конструктор

- [ ] `__init__(self, session: AsyncSession)`

**Зачем:** FastAPI при каждом запросе создаёт новую сессию БД и передаёт её в репозиторий.  
Ты не создаёшь подключение к БД сам — только сохраняешь `self.session = session`.

---

### Приватные хелперы (сделать первыми)

> Методы с `_` в начале — **внутренние**, их не вызывает router напрямую.  
> Это переиспользуемые куски логики, чтобы не копировать один и тот же код в 5 методах.

- [ ] `_company_has_access(contract: SupplyContract, company_id: int) -> bool`  
  `company_id in (contract.buyer_company_id, contract.seller_company_id)`  
  **Зачем:** одна функция «может ли эта компания видеть договор» — используешь везде.

- [ ] `_spec_access_via_contract(spec: SupplyContractSpecification, company_id: int) -> bool`  
  Нужен загруженный `spec.supply_contract` (через `selectinload`) → вызываешь `_company_has_access`.  
  **Зачем:** у спецификации нет buyer/seller напрямую — они на родительском договоре.

- [ ] `_generate_contract_number(self, seller_company_id: int) -> str`  
  Смотри `DealRepository._generate_supply_contract_number` (~строка 906): max номер у продавца за год → `00001`, `00002`…  
  **Зачем:** номер генерирует сервер, клиент его не присылает при создании.

- [ ] `_generate_spec_number(self, supply_contract_id: int) -> str`  
  Аналогично, но max по `spec_number` **внутри одного договора**.  
  **Зачем:** unique `(supply_contract_id, spec_number)` в БД.

- [ ] `_contract_load_options()`  
  `selectinload(SupplyContract.specifications).selectinload(SupplyContractSpecification.spec_items)`  
  **Зачем:** при GET договора сразу получить список спецификаций и товаров **одним-двумя запросами**, а не N+1.

- [ ] `_spec_load_options()`  
  `selectinload(...spec_items), selectinload(...supply_contract)`  
  **Зачем:** для GET/PATCH spec нужны и строки таблицы, и родительский договор (для access check).

- [ ] `_replace_spec_items(self, spec, items) -> None`  
  Полная замена: `spec.spec_items.clear()` → создать новые `SpecificationItemModel(...)` → `spec.spec_items.append(...)`.  
  Образец: `DealRepository.update_order`, блок с `order.order_items.clear()`.  
  **Импорт:** `SpecificationItem as SpecificationItemModel` — pydantic-схема `SpecificationItem` это **другой** класс!

---

### Договор поставки — CRUD

> **CRUD** = Create, Read, Update, Delete. У тебя Delete пока нет — это нормально.

#### `create_contract`
- [ ] `async def create_contract(self, seller_company_id: int, buyer_company_id: int) -> SupplyContract`

**Endpoint:** `POST /purchases/supply-contracts`

**Логика по шагам:**
1. **Не проверяй здесь** «договор уже есть» — это service (`409`). Repository только создаёт.
2. `number = await self._generate_contract_number(seller_company_id)`
3. `date = datetime.utcnow()` — в модели поле `date` обязательное.
4. `contract = SupplyContract(seller_company_id=..., buyer_company_id=..., number=..., date=..., ...)`
5. `self.session.add(contract)` — «запомни объект»
6. `await self.session.flush()` — БД выдаст `contract.id`
7. `await self.session.commit()` — сохранить навсегда
8. `return await self.get_contract_by_id(contract.id, company_id=...)` — перечитать со связями

**Частая ошибка новичка:** забыть `await` перед `session.commit()` / `session.execute()`.

---

#### `get_contract_by_id`
- [ ] `async def get_contract_by_id(self, contract_id: int, company_id: int) -> Optional[SupplyContract]`

**Endpoint:** `GET /purchases/supply-contracts/{contract_id}`

**Логика:**
```python
result = await self.session.execute(
	select(SupplyContract)
	.options(*self._contract_load_options())  # или .options(selectinload(...))
	.where(SupplyContract.id == contract_id)
)
contract = result.scalar_one_or_none()  # один объект или None
if contract is None:
	return None
if not self._company_has_access(contract, company_id):
	return None  # service решит: 403
return contract
```

**Почему `None`, а не exception:** в этом проекте так принято — service/router переводят `None` в HTTP-ответ.

---

#### `get_contract_by_id_only`
- [ ] `async def get_contract_by_id_only(self, contract_id: int) -> Optional[SupplyContract]`

**Зачем два get-метода:**

| Ситуация | Метод | Результат | HTTP в service |
|----------|-------|-----------|----------------|
| Записи с таким id **нет в БД** | `get_*_by_id_only` → `None` | — | **404** Not Found |
| Запись **есть**, но чужая компания | `get_*_by_id_only` → объект, `get_*_by_id` → `None` | — | **403** Forbidden |

Без `*_by_id_only` ты не отличишь «не существует» от «существует, но не твоё».

---

#### `find_by_company_pair`
- [ ] `async def find_by_company_pair(self, buyer_company_id: int, seller_company_id: int) -> Optional[SupplyContract]`

**Endpoint:** `GET /purchases/supply-contracts/exists?seller_company_id=&buyer_company_id=`

**Логика:** `WHERE buyer_company_id = ... AND seller_company_id = ...` → один результат или `None`.  
**Бизнес-правило:** на пару — максимум один договор.  
Service упакует в `SupplyContractExistsResponse(is_exist=contract is not None, supply_contract=...)`.

**Access check здесь не нужен** — query params уже задают пару; service вызывает только для своей сделки.

---

#### `update_contract`
- [ ] `async def update_contract(self, contract_id: int, company_id: int, *, officials_json=..., terms_text=..., ...) -> Optional[SupplyContract]`

**Endpoint:** `PATCH /purchases/supply-contracts/{contract_id}`

**Partial update — главная идея PATCH:**
```python
if terms_text is not None:  # только если поле прислали
	contract.terms_text = terms_text
# если terms_text is None — старое значение в БД не трогаем
```

**officials_json:** из Pydantic-объектов сделай list[dict] перед записью в JSON-колонку (как в `DealRepository.update_order` для `bill_officials`).

В конце: `commit` → `return await self.get_contract_by_id(...)`.

---

### Спецификация — CRUD

> Спецификация **всегда** принадлежит договору (`supply_contract_id`). Без договора создать нельзя.

#### `create_specification`
- [ ] `async def create_specification(self, contract_id: int, company_id: int) -> Optional[SupplyContractSpecification]`

**Endpoint:** `POST /purchases/supply-contracts/{contract_id}/specifications` (body пустой)

**Логика:**
1. `contract = await self.get_contract_by_id(contract_id, company_id)` — если `None`, spec не создаём.
2. `spec_number = await self._generate_spec_number(contract_id)`
3. `spec = SupplyContractSpecification(supply_contract_id=contract.id, spec_number=..., spec_date=utcnow(), spec_text='')`
4. `add` → `flush` → `commit` → reload через `get_specification_by_id`

**Зачем пустая spec:** пользователь потом заполнит текст и товары через PATCH.

---

#### `get_specification_by_id`
- [ ] `async def get_specification_by_id(self, spec_id: int, company_id: int) -> Optional[SupplyContractSpecification]`

**Endpoint:** `GET /purchases/supply-specifications/{spec_id}`

Тот же паттерн, что `get_contract_by_id`: select + `_spec_load_options()` + access через договор.

---

#### `get_specification_by_id_only`
- [ ] `async def get_specification_by_id_only(self, spec_id: int) -> Optional[SupplyContractSpecification]`

Пара к `get_specification_by_id` — для различения 404 / 403 (см. таблицу выше).

---

#### `update_specification`
- [ ] `async def update_specification(self, spec_id: int, company_id: int, *, spec_text=..., spec_items=...) -> Optional[SupplyContractSpecification]`

**Endpoint:** `PATCH /purchases/supply-specifications/{spec_id}`

1. Загрузить spec + проверить access.
2. `if spec_text is not None: spec.spec_text = spec_text`
3. `if spec_items is not None: await self._replace_spec_items(spec, spec_items)`
4. `commit` → reload

**Почему replace, а не merge:** проще и предсказуемо — клиент прислал новый список товаров = вся таблица заменяется.

---

#### `list_specifications_by_contract` (опционально)
- [ ] `async def list_specifications_by_contract(self, contract_id: int, company_id: int) -> list[SupplyContractSpecification]`

Можно **не делать**, если `get_contract_by_id` уже тянет `specifications` через eager load.

---

### Связь со сделкой (Order) — этап dual-write

> Пока можно пропустить. Нужно, когда заказ начнёт ссылаться на `supply_contract_id` вместо legacy-полей на `orders`.

- [x] `async def bind_order_to_contract(...)` — реализован + эндпоинт `POST /deals/{id}/supply-contract-entity/bind`
- [x] `async def bind_order_to_specification(...)` — реализован + эндпоинт `POST /deals/{id}/supply-specification/bind`

---

### Матрица: метод → endpoint

| Метод | HTTP | Кто вызывает |
|-------|------|--------------|
| `create_contract` | `POST /supply-contracts` | Service → Repository |
| `update_contract` | `PATCH /supply-contracts/{contract_id}` | Service → Repository |
| `get_contract_by_id` | `GET /supply-contracts/{contract_id}` | Service → Repository |
| `find_by_company_pair` | `GET /supply-contracts/exists?...` | Service → Repository |
| `create_specification` | `POST /.../specifications` | Service → Repository |
| `update_specification` | `PATCH /supply-specifications/{spec_id}` | Service → Repository |
| `get_specification_by_id` | `GET /supply-specifications/{spec_id}` | Service → Repository |
| `get_*_by_id_only` | — | только Service (404 vs 403) |

---

### Порядок реализации (не перескакивай)

1. Каркас класса + `_company_has_access` + `_contract_load_options`
2. **`get_contract_by_id_only`** + **`get_contract_by_id`** — научись **читать** до того, как писать
3. `find_by_company_pair`
4. `create_contract` — первый **write**
5. `update_contract`
6. `_spec_load_options` + `get_specification_by_id_only` + `get_specification_by_id`
7. `_generate_spec_number` + `create_specification`
8. `_replace_spec_items` + `update_specification`
9. bind к Order — позже

**Совет:** после каждого метода — один ручной тест или pytest. Не пиши все 10 методов сразу.

---

### Что остаётся в Service, не в Repository

| Задача | Почему не в repository |
|--------|------------------------|
| `409`, если договор на пару уже есть | это **бизнес-правило**, не SQL |
| `403` vs `404` | repository отдаёт `None`/объект; HTTP — уровень API |
| `SupplyContractResponse` / `SpecificationResponse` | JSON для клиента, не ORM |
| mapping `supply_contract_number` в spec response | ORM хранит `supply_contract_id`, клиенту нужен номер |
| сериализация `officials_json` | формат для фронта может отличаться от сырого JSON в БД |

---

### Как проверить, что repository работает (без router)

1. Поднять БД и прогнать миграции.
2. Временный pytest или скрипт:
   - `repo = SupplyContractRepository(session)`
   - `contract = await repo.create_contract(seller_id=1, buyer_id=2)`
   - `assert contract.id is not None`
   - `found = await repo.get_contract_by_id(contract.id, company_id=1)`
   - `assert found is not None`
3. Смотреть SQL в логах SQLAlchemy (`echo=True` в dev) — так понимаешь, что реально уходит в БД.

---

## 7) Service слой (бизнес-правила)

> **Для новичка:** Repository = «достать/сохранить в БД». Service = «понять, можно ли это делать» + «собрать JSON-ответ».  
> Router только принимает HTTP и вызывает service. **Не пиши SQL в service** — только вызовы `self.repository.*`.

Файлы:
- `backend/app/api/purchases/services/__init__.py` (или `services/supply_contract.py`)

Чек:
- [x] `SupplyContractService` использует `SupplyContractRepository`
- [x] `create_contract` → `409`, если `find_by_company_pair` уже вернул договор
- [x] `get_contract` / `get_specification` → `404` vs `403` через `get_*_by_id_only`
- [x] `_to_contract_response(orm)` / `_to_spec_response(orm)` — mapping officials, `supply_contract_number` для spec
- [x] `exists_by_pair` → `SupplyContractExistsResponse`
- [x] `bind_order_to_contract` / `bind_order_to_specification` на этапе dual-write
- [x] Корректно отдаются ошибки:
	- `404` договор/спецификация не найдены
	- `403` нет доступа
	- `409` договор на пару уже существует

---

## 8) Router / API эндпоинты

Файл:
- `backend/app/api/purchases/router.py`

Минимальный набор:
- [x] `POST /purchases/supply-contracts` → `SupplyContractCreate` → `SupplyContractResponse`
- [x] `PATCH /purchases/supply-contracts/{contract_id}` → `SupplyContractUpdate` → `SupplyContractResponse`
- [x] `GET /purchases/supply-contracts/{contract_id}` → `SupplyContractResponse`

- [x] `POST /purchases/supply-contracts/{contract_id}/specifications` → `SpecificationCreate` → `SpecificationResponse`
- [x] `PATCH /purchases/supply-specifications/{spec_id}` → `SpecificationUpdate` → `SpecificationResponse`
- [x] `GET /purchases/supply-specifications/{spec_id}` → `SpecificationResponse`

- [x] `GET /purchases/supply-contracts/exists?seller_company_id=&buyer_company_id=` → `SupplyContractExistsResponse`
- [x] `POST /purchases/deals/{deal_id}/supply-contract-entity/bind` — привязка сделки к договору
- [x] `POST /purchases/deals/{deal_id}/supply-specification/bind` — привязка сделки к спецификации

---







## 9) Совместимость и безопасный переход

Переход лучше делать в 3 этапа:

- [x] **Этап A (dual-write):** `supply_contract_sync.py` — запись в entity + legacy `orders.supply_contracts_*` при update/assign/bind.
- [x] **Этап B (read-switch):** `_order_to_deal_response` читает из entity, fallback на legacy поля.
- [ ] **Этап C (cleanup):** удалить legacy-поля отдельной миграцией после стабилизации.

Почему это важно: минимизирует риск поломок фронта и отчетности.

---

## 10) Backfill исторических данных

- [x] Написать скрипт backfill: `backend/scripts/backfill_supply_contracts.py`
	- выбрать `orders` с заполненными `supply_contracts_number`
	- сгруппировать по `(buyer_company_id, seller_company_id, number)`
	- создать записи в `supply_contract`
	- проставить `orders.supply_contract_id`
- [x] Сделать dry-run режим (`--dry-run`).
- [ ] Прогнать на staging-копии прод-данных.
- [x] Добиться идемпотентности (повторный запуск не дублирует — skip если `supply_contract_id` уже есть).

---

## 11) Тесты

- [ ] Unit тесты:
	- выбор активного договора
	- граничные даты
	- валидации.
- [x] Integration/API тесты:
	- договор есть -> спецификация создается (`test_supply_contract_api.py`)
	- договора нет -> корректная ошибка
	- проверка доступа -> `403`
	- dual-write assign/bind (`test_supply_contract_dual_write.py`)
- [x] Регрессия старых сценариев `Order`/`Bill`/`Contract` (`test_purchases_deals_api.py`)

---

## 12) Фронтенд-интеграция

- [x] Обновить типы (`dealResponse`, `dealState`, `supplyContractEntity`).
- [x] Добавить запрос проверки наличия договора.
- [x] Перед созданием спецификации запускать check API.
- [x] Показывать понятные состояния: "договор найден / не найден / истек".
- [x] Bind сделки к entity после create contract/spec (`bindSupplyContractToDeal`, `bindSupplySpecificationToDeal`).

---

## 13) Cleanup и финализация

- [x] Удалить merge-конфликт маркеры (`<<<<<<<`, `=======`, `>>>>>>>`) в backend — не найдены.
- [x] Выровнять нейминг: модель `Order` ↔ колонки БД `supply_contracts_number/date`; API response `supply_contract_date`.
- [ ] После перехода удалить legacy поля `orders.supply_contracts_*` (этап C).
- [x] Обновить документацию по API/миграциям (этот чеклист + скрипт backfill).

---

## Быстрый порядок коммитов (рекомендуется)

1. `models + alembic`
2. `schemas + repository + service`
3. `router + tests`
4. `backfill script`
5. `frontend integration`
6. `legacy cleanup`

---

## Красные флаги

- Нет unique-ограничений на номера.
- Смешение бизнес-логики между router/service/repository.
- Отсутствие dual-write/read-fallback.
- Миграция без тестового backfill.
- Непродуманные `ondelete` приводят к потере связанных записей.
