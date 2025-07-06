from sqladmin import ModelView

from app.api.messages.models.message import Message


class MessageAdmin(ModelView, model=Message):
    name = "Сообщение"
    name_plural = "Сообщения"
    icon = "fa-solid fa-message"

    # Настройка отображаемых колонок
    column_list = [
        Message.id,
        Message.chat_id,
        Message.sender_company_id,
        Message.sender_user_id,
        Message.content,
        Message.is_read,
        Message.created_at,
        Message.updated_at,
    ]

    # Настройка поиска
    column_searchable_list = [
        Message.content,
        Message.chat_id,
        Message.sender_company_id,
        Message.sender_user_id,
    ]

    # Настройка фильтров
    column_filters = [
        Message.is_read,
        Message.created_at,
        Message.updated_at
    ]

    # Настройка сортировки
    column_sortable_list = [
        Message.id,
        Message.chat_id,
        Message.sender_company_id,
        Message.sender_user_id,
        Message.created_at,
        Message.updated_at,
        Message.is_read
    ]

    # Настройка детальной информации
    column_details_list = [
        Message.id,
        Message.chat_id,
        Message.sender_company_id,
        Message.sender_user_id,
        Message.content,
        Message.file_path,
        Message.file_name,
        Message.file_size,
        Message.file_type,
        Message.is_read,
        Message.created_at,
        Message.updated_at,
    ]

    # Настройка формы редактирования
    form_columns = [
        Message.chat_id,
        Message.sender_company_id,
        Message.sender_user_id,
        Message.content,
        Message.file_path,
        Message.file_name,
        Message.file_size,
        Message.file_type,
        Message.is_read,
    ]

    # Настройка отображения в списке
    column_labels = {
        Message.id: "ID",
        Message.chat_id: "ID чата",
        Message.sender_company_id: "ID компании отправителя",
        Message.sender_user_id: "ID пользователя отправителя",
        Message.content: "Содержание",
        Message.file_path: "Путь к файлу",
        Message.file_name: "Имя файла",
        Message.file_size: "Размер файла",
        Message.file_type: "Тип файла",
        Message.is_read: "Прочитано",
        Message.created_at: "Дата создания",
        Message.updated_at: "Дата обновления",
    }

    # Настройка форматирования
    column_formatters = {
        Message.content: lambda m, a: m.content[:50] + "..." if len(m.content) > 50 else m.content,
        Message.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        Message.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
    }

    # Настройка экспорта
    can_export = True
    export_types = ["csv", "xlsx"]

    # Настройка создания
    can_create = True

    # Настройка редактирования
    can_edit = True

    # Настройка удаления
    can_delete = True

    # Настройка просмотра
    can_view_details = True
