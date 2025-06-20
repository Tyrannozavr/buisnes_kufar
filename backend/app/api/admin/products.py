from sqladmin import ModelView
from sqladmin.fields import QuerySelectField
from app.api.products.models.product import Product, ProductType
from app.api.company.models.company import Company


class ProductAdmin(ModelView, model=Product):
    name = "Продукт"
    name_plural = "Продукты"
    icon = "fa-solid fa-box"

    # Настройка отображаемых колонок
    column_list = [
        Product.id,
        Product.name,
        Product.article,
        Product.type,
        Product.price,
        Product.unit_of_measurement,
        Product.is_hidden,
        Product.is_deleted,
        'company.name',  # Отображаем название компании
        Product.created_at,
        Product.updated_at
    ]

    # Настройка поиска
    column_searchable_list = [
        Product.name,
        Product.article,
        Product.description,
        'company.name'  # Поиск по названию компании
    ]

    # Настройка фильтров
    column_filters = [
        Product.type,
        Product.is_hidden,
        Product.is_deleted,
        Product.created_at,
        Product.updated_at,
        'company.name'  # Фильтр по названию компании
    ]

    # Настройка сортировки
    column_sortable_list = [
        Product.id,
        Product.name,
        Product.article,
        Product.price,
        Product.created_at,
        Product.updated_at,
        'company.name'  # Сортировка по названию компании
    ]

    # Настройка детальной информации
    column_details_list = [
        Product.id,
        Product.name,
        Product.slug,
        Product.description,
        Product.article,
        Product.type,
        Product.price,
        Product.unit_of_measurement,
        Product.images,
        Product.characteristics,
        Product.is_hidden,
        Product.is_deleted,
        Product.created_at,
        Product.updated_at,
        'company'
    ]

    # Настройка формы редактирования
    form_columns = [
        Product.name,
        Product.slug,
        Product.description,
        Product.article,
        Product.type,
        Product.price,
        Product.unit_of_measurement,
        Product.images,
        Product.characteristics,
        Product.is_hidden,
        Product.is_deleted,
        "company"
    ]

    # Настройка отображения в списке
    column_labels = {
        Product.id: "ID",
        Product.name: "Название",
        Product.slug: "Slug",
        Product.description: "Описание",
        Product.article: "Артикул",
        Product.type: "Тип",
        Product.price: "Цена",
        Product.unit_of_measurement: "Единица измерения",
        Product.images: "Изображения",
        Product.characteristics: "Характеристики",
        Product.is_hidden: "Скрыт",
        Product.is_deleted: "Удален",
        Product.created_at: "Дата создания",
        Product.updated_at: "Дата обновления",
        'company.name': "Компания"
    }

    # Настройка форматирования
    column_formatters = {
        Product.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        Product.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
        Product.price: lambda m, a: f"{m.price:.2f}" if m.price else None,
        Product.images: lambda m, a: f"{len(m.images)} изображений" if m.images else "Нет изображений",
        Product.characteristics: lambda m, a: f"{len(m.characteristics)} характеристик" if m.characteristics else "Нет характеристик"
    }

    # Настройка валидации формы
    form_widget_args = {
        "slug": {"readonly": True},
        "created_at": {"readonly": True},
        "updated_at": {"readonly": True}
    }

    column_default_sort = (Product.created_at, True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # Добавляем настройку для выпадающего списка компаний
    form_overrides = {
        "company": QuerySelectField
    }

    def get_form(self):
        form = super().get_form()
        form.company.query_factory = lambda: Company.query.all()
        return form
