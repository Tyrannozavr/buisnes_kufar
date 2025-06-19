# Products API

## Архитектура

API продуктов построен по принципу репозиториев и сервисов, следуя архитектуре проекта.

### Структура

```
products/
├── models/
│   └── product.py          # Модель продукта
├── repositories/
│   ├── my_products_repository.py      # Репозиторий для владельца компании
│   └── company_products_repository.py # Репозиторий для получения продуктов компаний
├── schemas/
│   └── product.py          # Pydantic схемы
├── services/
│   └── product_service.py  # Сервис для бизнес-логики
├── dependencies.py         # Зависимости для инъекции
├── router.py              # FastAPI роутер
└── README.md              # Документация
```

## Репозитории

### MyProductsRepository

Репозиторий для владельца компании. Все операции могут производиться только пользователем, на которого указывает `user_id` компании.

**Основные методы:**
- `create()` - создание продукта
- `get_by_id()` - получение продукта по ID
- `get_by_slug()` - получение продукта по slug
- `get_all_products()` - получение всех продуктов с пагинацией
- `get_products_by_type()` - получение продуктов по типу
- `update()` - обновление продукта
- `delete()` - мягкое удаление
- `hard_delete()` - полное удаление
- `toggle_hidden()` - переключение видимости
- `update_images()` - обновление изображений

### CompanyProductsRepository

Репозиторий для получения продуктов компаний. Только read-only операции.

**Основные методы:**
- `get_by_id()` - получение продукта по ID
- `get_by_slug()` - получение продукта по slug и company_id
- `get_by_company_id()` - получение продуктов компании
- `get_all_products()` - получение всех продуктов
- `get_all_services()` - получение всех услуг
- `get_all_goods()` - получение всех товаров
- `get_services_by_company_id()` - получение услуг компании
- `get_goods_by_company_id()` - получение товаров компании
- `search_products()` - поиск продуктов
- `get_products_by_price_range()` - фильтр по цене
- `get_latest_products()` - последние продукты

## Сервис

### ProductService

Объединяет функциональность обоих репозиториев и предоставляет методы для работы с продуктами.

## Зависимости

- `my_products_repository_dep` - зависимость для MyProductsRepository
- `company_products_repository_dep` - зависимость для CompanyProductsRepository
- `product_service_dep` - зависимость для ProductService

## Эндпоинты

### Для владельца компании (требуют аутентификации)

- `POST /products/my` - создание продукта
- `GET /products/my` - получение всех продуктов
- `GET /products/my/{product_id}` - получение продукта по ID
- `GET /products/my/slug/{slug}` - получение продукта по slug
- `GET /products/my/type/{product_type}` - получение продуктов по типу
- `PUT /products/my/{product_id}` - обновление продукта
- `DELETE /products/my/{product_id}` - удаление продукта
- `DELETE /products/my/{product_id}/hard` - полное удаление
- `PATCH /products/my/{product_id}/toggle-hidden` - переключение видимости

### Публичные эндпоинты

- `GET /products/` - все продукты
- `GET /products/services` - все услуги
- `GET /products/goods` - все товары
- `GET /products/company/{company_id}` - продукты компании
- `GET /products/company/{company_id}/services` - услуги компании
- `GET /products/company/{company_id}/goods` - товары компании
- `GET /products/{product_id}` - продукт по ID
- `GET /products/company/{company_id}/slug/{slug}` - продукт по slug
- `GET /products/search` - поиск продуктов
- `GET /products/price-range` - фильтр по цене
- `GET /products/latest` - последние продукты

## Безопасность

- Все операции с собственными продуктами требуют аутентификации
- Проверка прав доступа через связь `user_id` -> `company_id` -> `product.company_id`
- Публичные эндпоинты возвращают только активные и не скрытые продукты 