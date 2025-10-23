from sqladmin import ModelView
from sqladmin.fields import QuerySelectField

from app.api.company.models.company import Company
from app.api.products.models.product import Product
# from app.api.purchases.models import Deal, DealItem, DealDocument, DealChange


# class DealAdmin(ModelView, model=Deal):
#     name = "Сделка"
#     name_plural = "Сделки"
#     icon = "fa-solid fa-handshake"
#
#     # Настройка отображаемых колонок
#     column_list = [
#         Deal.id,
#         Deal.buyer_order_number,
#         Deal.seller_order_number,
#         Deal.status,
#         Deal.deal_type,
#         Deal.total_amount,
#         'buyer_company.short_name',
#         'seller_company.short_name',
#         Deal.created_at,
#         Deal.updated_at
#     ]
#
#     # Настройка поиска
#     column_searchable_list = [
#         Deal.buyer_order_number,
#         Deal.seller_order_number,
#         Deal.comments,
#         'buyer_company.short_name',
#         'seller_company.short_name'
#     ]
#
#     # Настройка фильтров
#     column_filters = [
#         Deal.status,
#         Deal.deal_type,
#         Deal.created_at,
#         Deal.updated_at,
#         'buyer_company.short_name',
#         'seller_company.short_name'
#     ]
#
#     # Настройка сортировки
#     column_sortable_list = [
#         Deal.id,
#         Deal.buyer_order_number,
#         Deal.seller_order_number,
#         Deal.status,
#         Deal.total_amount,
#         Deal.created_at,
#         Deal.updated_at
#     ]
#
#     # Настройка детальной информации
#     column_details_list = [
#         Deal.id,
#         Deal.buyer_order_number,
#         Deal.seller_order_number,
#         Deal.status,
#         Deal.deal_type,
#         Deal.comments,
#         Deal.total_amount,
#         Deal.last_modified_by_company_id,
#         Deal.created_at,
#         Deal.updated_at,
#         'buyer_company',
#         'seller_company',
#         'last_modified_by',
#         'items',
#         'documents',
#         'changes'
#     ]
#
#     # Настройка формы редактирования
#     form_columns = [
#         Deal.buyer_order_number,
#         Deal.seller_order_number,
#         Deal.status,
#         Deal.deal_type,
#         Deal.comments,
#         Deal.total_amount,
#         "buyer_company",
#         "seller_company",
#         "last_modified_by"
#     ]
#
#     # Настройка отображения в списке
#     column_labels = {
#         Deal.id: "ID",
#         Deal.buyer_order_number: "Номер заказа покупателя",
#         Deal.seller_order_number: "Номер заказа продавца",
#         Deal.status: "Статус",
#         Deal.deal_type: "Тип сделки",
#         Deal.comments: "Комментарии",
#         Deal.total_amount: "Общая сумма",
#         Deal.last_modified_by_company_id: "Последний редактор",
#         Deal.created_at: "Дата создания",
#         Deal.updated_at: "Дата обновления",
#         'buyer_company.short_name': "Покупатель",
#         'seller_company.short_name': "Продавец"
#     }
#
#     # Настройка форматирования
#     column_formatters = {
#         Deal.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
#         Deal.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
#         Deal.total_amount: lambda m, a: f"{m.total_amount:.2f} руб." if m.total_amount else "Не указано",
#     }
#
#     # Настройка валидации формы
#     form_widget_args = {
#         "buyer_order_number": {"readonly": True},
#         "seller_order_number": {"readonly": True},
#         "created_at": {"readonly": True},
#         "updated_at": {"readonly": True}
#     }
#
#     column_default_sort = (Deal.created_at, True)
#     can_create = True
#     can_edit = True
#     can_delete = True
#     can_view_details = True
#
#     # Добавляем настройку для выпадающих списков
#     form_overrides = {
#         "buyer_company": QuerySelectField,
#         "seller_company": QuerySelectField,
#         "last_modified_by": QuerySelectField
#     }
#
#     def get_form(self):
#         form = super().get_form()
#         form.buyer_company.query_factory = lambda: Company.query.all()
#         form.seller_company.query_factory = lambda: Company.query.all()
#         form.last_modified_by.query_factory = lambda: Company.query.all()
#         return form
#
#
# class DealItemAdmin(ModelView, model=DealItem):
#     name = "Позиция заказа"
#     name_plural = "Позиции заказов"
#     icon = "fa-solid fa-list"
#
#     # Настройка отображаемых колонок
#     column_list = [
#         DealItem.id,
#         DealItem.name,
#         DealItem.article,
#         DealItem.item_type,
#         DealItem.quantity,
#         DealItem.unit_of_measurement,
#         DealItem.price,
#         DealItem.amount,
#         'deal.buyer_order_number',
#         DealItem.created_at
#     ]
#
#     # Настройка поиска
#     column_searchable_list = [
#         DealItem.name,
#         DealItem.article,
#         'deal.buyer_order_number',
#         'deal.seller_order_number'
#     ]
#
#     # Настройка фильтров
#     column_filters = [
#         DealItem.item_type,
#         DealItem.unit_of_measurement,
#         DealItem.created_at,
#         'deal.buyer_order_number'
#     ]
#
#     # Настройка сортировки
#     column_sortable_list = [
#         DealItem.id,
#         DealItem.name,
#         DealItem.article,
#         DealItem.price,
#         DealItem.amount,
#         DealItem.created_at
#     ]
#
#     # Настройка детальной информации
#     column_details_list = [
#         DealItem.id,
#         DealItem.name,
#         DealItem.article,
#         DealItem.item_type,
#         DealItem.quantity,
#         DealItem.unit_of_measurement,
#         DealItem.price,
#         DealItem.amount,
#         DealItem.characteristics,
#         DealItem.created_at,
#         'deal',
#         'product'
#     ]
#
#     # Настройка формы редактирования
#     form_columns = [
#         DealItem.name,
#         DealItem.article,
#         DealItem.item_type,
#         DealItem.quantity,
#         DealItem.unit_of_measurement,
#         DealItem.price,
#         DealItem.amount,
#         DealItem.characteristics,
#         "deal",
#         "product"
#     ]
#
#     # Настройка отображения в списке
#     column_labels = {
#         DealItem.id: "ID",
#         DealItem.name: "Наименование",
#         DealItem.article: "Артикул",
#         DealItem.item_type: "Тип",
#         DealItem.quantity: "Количество",
#         DealItem.unit_of_measurement: "Единица измерения",
#         DealItem.price: "Цена",
#         DealItem.amount: "Сумма",
#         DealItem.characteristics: "Характеристики",
#         DealItem.created_at: "Дата создания",
#         'deal.buyer_order_number': "Номер заказа"
#     }
#
#     # Настройка форматирования
#     column_formatters = {
#         DealItem.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
#         DealItem.price: lambda m, a: f"{m.price:.2f} руб." if m.price else None,
#         DealItem.amount: lambda m, a: f"{m.amount:.2f} руб." if m.amount else None,
#         DealItem.characteristics: lambda m, a: f"{len(m.characteristics)} характеристик" if m.characteristics else "Нет характеристик",
#     }
#
#     # Настройка валидации формы
#     form_widget_args = {
#         "created_at": {"readonly": True}
#     }
#
#     column_default_sort = (DealItem.created_at, True)
#     can_create = True
#     can_edit = True
#     can_delete = True
#     can_view_details = True
#
#     # Добавляем настройку для выпадающих списков
#     form_overrides = {
#         "deal": QuerySelectField,
#         "product": QuerySelectField
#     }
#
#     def get_form(self):
#         form = super().get_form()
#         form.deal.query_factory = lambda: Deal.query.all()
#         form.product.query_factory = lambda: Product.query.all()
#         return form
#
#
# class DealDocumentAdmin(ModelView, model=DealDocument):
#     name = "Документ сделки"
#     name_plural = "Документы сделок"
#     icon = "fa-solid fa-file"
#
#     # Настройка отображаемых колонок
#     column_list = [
#         DealDocument.id,
#         DealDocument.document_type,
#         DealDocument.document_number,
#         DealDocument.document_date,
#         DealDocument.status,
#         DealDocument.file_name,
#         DealDocument.file_size,
#         'deal.buyer_order_number',
#         'created_by.short_name',
#         DealDocument.created_at
#     ]
#
#     # Настройка поиска
#     column_searchable_list = [
#         DealDocument.document_number,
#         DealDocument.file_name,
#         DealDocument.description,
#         'deal.buyer_order_number',
#         'deal.seller_order_number'
#     ]
#
#     # Настройка фильтров
#     column_filters = [
#         DealDocument.document_type,
#         DealDocument.status,
#         DealDocument.document_date,
#         DealDocument.created_at,
#         'deal.buyer_order_number'
#     ]
#
#     # Настройка сортировки
#     column_sortable_list = [
#         DealDocument.id,
#         DealDocument.document_number,
#         DealDocument.document_date,
#         DealDocument.file_size,
#         DealDocument.created_at
#     ]
#
#     # Настройка детальной информации
#     column_details_list = [
#         DealDocument.id,
#         DealDocument.document_type,
#         DealDocument.document_number,
#         DealDocument.document_date,
#         DealDocument.file_path,
#         DealDocument.file_name,
#         DealDocument.file_size,
#         DealDocument.status,
#         DealDocument.description,
#         DealDocument.created_at,
#         DealDocument.updated_at,
#         'deal',
#         'created_by'
#     ]
#
#     # Настройка формы редактирования
#     form_columns = [
#         DealDocument.document_type,
#         DealDocument.document_number,
#         DealDocument.document_date,
#         DealDocument.file_path,
#         DealDocument.file_name,
#         DealDocument.file_size,
#         DealDocument.status,
#         DealDocument.description,
#         "deal",
#         "created_by"
#     ]
#
#     # Настройка отображения в списке
#     column_labels = {
#         DealDocument.id: "ID",
#         DealDocument.document_type: "Тип документа",
#         DealDocument.document_number: "Номер документа",
#         DealDocument.document_date: "Дата документа",
#         DealDocument.file_path: "Путь к файлу",
#         DealDocument.file_name: "Имя файла",
#         DealDocument.file_size: "Размер файла",
#         DealDocument.status: "Статус",
#         DealDocument.description: "Описание",
#         DealDocument.created_at: "Дата создания",
#         DealDocument.updated_at: "Дата обновления",
#         'deal.buyer_order_number': "Номер заказа",
#         'created_by.short_name': "Создал"
#     }
#
#     # Настройка форматирования
#     column_formatters = {
#         DealDocument.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
#         DealDocument.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
#         DealDocument.document_date: lambda m, a: m.document_date.strftime("%Y-%m-%d") if m.document_date else None,
#         DealDocument.file_size: lambda m, a: f"{m.file_size / 1024:.1f} KB" if m.file_size else "Не указано",
#     }
#
#     # Настройка валидации формы
#     form_widget_args = {
#         "created_at": {"readonly": True},
#         "updated_at": {"readonly": True}
#     }
#
#     column_default_sort = (DealDocument.created_at, True)
#     can_create = True
#     can_edit = True
#     can_delete = True
#     can_view_details = True
#
#     # Добавляем настройку для выпадающих списков
#     form_overrides = {
#         "deal": QuerySelectField,
#         "created_by": QuerySelectField
#     }
#
#     def get_form(self):
#         form = super().get_form()
#         form.deal.query_factory = lambda: Deal.query.all()
#         form.created_by.query_factory = lambda: Company.query.all()
#         return form
#
#
# class DealChangeAdmin(ModelView, model=DealChange):
#     name = "Изменение сделки"
#     name_plural = "История изменений"
#     icon = "fa-solid fa-history"
#
#     # Настройка отображаемых колонок
#     column_list = [
#         DealChange.id,
#         DealChange.change_type,
#         DealChange.comment,
#         'deal.buyer_order_number',
#         'changed_by.short_name',
#         DealChange.created_at
#     ]
#
#     # Настройка поиска
#     column_searchable_list = [
#         DealChange.comment,
#         'deal.buyer_order_number',
#         'deal.seller_order_number',
#         'changed_by.short_name'
#     ]
#
#     # Настройка фильтров
#     column_filters = [
#         DealChange.change_type,
#         DealChange.created_at,
#         'deal.buyer_order_number',
#         'changed_by.short_name'
#     ]
#
#     # Настройка сортировки
#     column_sortable_list = [
#         DealChange.id,
#         DealChange.change_type,
#         DealChange.created_at
#     ]
#
#     # Настройка детальной информации
#     column_details_list = [
#         DealChange.id,
#         DealChange.change_type,
#         DealChange.old_data,
#         DealChange.new_data,
#         DealChange.comment,
#         DealChange.created_at,
#         'deal',
#         'changed_by'
#     ]
#
#     # Настройка формы редактирования
#     form_columns = [
#         DealChange.change_type,
#         DealChange.old_data,
#         DealChange.new_data,
#         DealChange.comment,
#         "deal",
#         "changed_by"
#     ]
#
#     # Настройка отображения в списке
#     column_labels = {
#         DealChange.id: "ID",
#         DealChange.change_type: "Тип изменения",
#         DealChange.old_data: "Старые данные",
#         DealChange.new_data: "Новые данные",
#         DealChange.comment: "Комментарий",
#         DealChange.created_at: "Дата изменения",
#         'deal.buyer_order_number': "Номер заказа",
#         'changed_by.short_name': "Изменил"
#     }
#
#     # Настройка форматирования
#     column_formatters = {
#         DealChange.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
#         DealChange.old_data: lambda m, a: "Есть данные" if m.old_data else "Нет данных",
#         DealChange.new_data: lambda m, a: "Есть данные" if m.new_data else "Нет данных",
#     }
#
#     # Настройка валидации формы
#     form_widget_args = {
#         "created_at": {"readonly": True}
#     }
#
#     column_default_sort = (DealChange.created_at, True)
#     can_create = False  # Изменения создаются автоматически
#     can_edit = False    # История неизменяема
#     can_delete = False  # История не удаляется
#     can_view_details = True
#
#     # Добавляем настройку для выпадающих списков
#     form_overrides = {
#         "deal": QuerySelectField,
#         "changed_by": QuerySelectField
#     }
#
#     def get_form(self):
#         form = super().get_form()
#         form.deal.query_factory = lambda: Deal.query.all()
#         form.changed_by.query_factory = lambda: Company.query.all()
#         return form
