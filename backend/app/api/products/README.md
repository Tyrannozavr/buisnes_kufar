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

# Система загрузки изображений продуктов

## Обзор

Система загрузки изображений продуктов была обновлена для сохранения файлов в директорию вместо хранения base64-encoded строк в базе данных. Это улучшает производительность и уменьшает размер базы данных.

## Архитектура

### Бэкенд

#### Эндпоинты

1. **POST /v1/products** - Создание продукта без изображений
   - Принимает: `ProductCreate` (JSON)
   - Возвращает: `ProductResponse`
   - Требует аутентификации

2. **POST /v1/products/with-images** - Создание продукта с изображениями в одном запросе
   - Принимает: `FormData` с данными продукта и файлами
   - Возвращает: `ProductResponse`
   - Требует аутентификации

3. **POST /v1/products/{product_id}/images** - Загрузка изображений для существующего продукта
   - Принимает: `files: List[UploadFile]`
   - Возвращает: `ProductResponse`
   - Требует аутентификации

4. **DELETE /v1/products/{product_id}/images/{image_index}** - Удаление изображения по индексу
   - Принимает: `product_id: int`, `image_index: int`
   - Возвращает: `ProductResponse`
   - Требует аутентификации

#### Структура файлов

```
backend/
├── uploads/
│   └── product_images/
│       ├── uuid1.jpg
│       ├── uuid2.png
│       └── ...
```

#### Сервис

`ProductService` содержит методы:
- `create_my_product()` - создание продукта без изображений
- `create_my_product_with_images()` - создание продукта с изображениями
- `upload_product_images()` - загрузка изображений для существующего продукта
- `delete_product_image()` - удаление изображения

#### Схемы

- `ProductCreate` - для создания продукта без изображений
- `ProductCreateWithFiles` - для создания продукта с изображениями
- `ProductUpdate` - для обновления продукта (без изображений)
- `ProductResponse` - ответ с изображениями

### Фронтенд

#### API функции

В `frontend/api/me/products.ts` добавлены:
- `createProduct(productData)` - создание продукта без изображений
- `createProductWithImages(productData, files)` - создание продукта с изображениями
- `uploadProductImages(productId, files)` - загрузка изображений
- `deleteProductImage(productId, imageIndex)` - удаление изображения

#### Компонент ProductForm

Обновлен для работы с новой системой:
- Изображения можно загружать как для новых, так и для существующих продуктов
- Для новых продуктов изображения сохраняются локально до отправки
- Для существующих продуктов изображения загружаются через API
- Показывает индикаторы загрузки
- Отображает уведомления об успехе/ошибке

## Использование

### Создание продукта с изображениями (рекомендуемый способ)

```typescript
const productData = {
  name: "Название продукта",
  description: "Описание",
  article: "ART-001",
  type: "Товар",
  price: 1000,
  unit_of_measurement: "шт",
  characteristics: [
    { name: "Цвет", value: "Красный" }
  ]
};

const files = [file1, file2, file3]; // File objects
const product = await createProductWithImages(productData, files);
```

### Создание продукта без изображений

```typescript
const product = await createProduct(productData);
```

### Добавление изображений к существующему продукту

```typescript
const files = [file1, file2, file3]; // File objects
const updatedProduct = await uploadProductImages(productId, files);
```

### Удаление изображения

```typescript
const updatedProduct = await deleteProductImage(productId, imageIndex);
```

## Преимущества новой системы

1. **Производительность**: Файлы хранятся на диске, а не в БД
2. **Размер БД**: Значительно уменьшен размер базы данных
3. **Масштабируемость**: Легче масштабировать хранение файлов
4. **Кэширование**: Статические файлы могут кэшироваться браузером
5. **CDN**: Возможность использования CDN для изображений
6. **UX**: Возможность создания продукта с изображениями в одном запросе

## Безопасность

- Проверка типа файла (только изображения)
- Уникальные имена файлов (UUID)
- Проверка прав доступа к продукту
- Валидация размера файлов (можно добавить)

## Обратная совместимость

- Существующие продукты с base64 изображениями продолжают работать
- Новые изображения загружаются как файлы
- При обновлении продукта старые изображения сохраняются

## Структура файлов

```
backend/
├── uploads/
│   ├── company_logos/     # Логотипы компаний (существующая)
│   └── product_images/    # Изображения продуктов (новая)
│       ├── uuid1.jpg
│       ├── uuid2.png
│       └── ...
```

## Настройка

### Директории

Создайте директорию для загрузки:
```bash
mkdir -p backend/uploads/product_images
```

### Статические файлы

FastAPI уже настроен для раздачи статических файлов:
```python
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
```

### Размер файлов

Для ограничения размера файлов добавьте в настройки FastAPI:
```python
app = FastAPI(
    title=settings.PROJECT_NAME,
    max_request_size=10 * 1024 * 1024  # 10MB
)
``` 