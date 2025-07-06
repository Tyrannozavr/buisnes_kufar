from sqladmin import ModelView

from app.api.chats.models.chat import Chat
from app.api.chats.models.chat_participant import ChatParticipant


class ChatAdmin(ModelView, model=Chat):
    name = "Чат"
    name_plural = "Чаты"
    icon = "fa-solid fa-comments"

    # Настройка отображаемых колонок
    column_list = [
        Chat.id,
        Chat.title,
        Chat.is_group,
        Chat.created_at,
        Chat.updated_at,
    ]

    # Настройка поиска
    column_searchable_list = [
        Chat.title,
    ]

    # Настройка фильтров
    column_filters = [
        Chat.is_group,
        Chat.created_at,
        Chat.updated_at
    ]

    # Настройка сортировки
    column_sortable_list = [
        Chat.id,
        Chat.title,
        Chat.created_at,
        Chat.updated_at,
        Chat.is_group
    ]

    # Настройка детальной информации
    column_details_list = [
        Chat.id,
        Chat.title,
        Chat.is_group,
        Chat.created_at,
        Chat.updated_at
    ]

    # Настройка формы редактирования
    form_columns = [
        Chat.title,
        Chat.is_group,
    ]

    # Настройка отображения в списке
    column_labels = {
        Chat.id: "ID",
        Chat.title: "Название",
        Chat.is_group: "Групповой чат",
        Chat.created_at: "Дата создания",
        Chat.updated_at: "Дата обновления",
    }

    # Настройка форматирования
    column_formatters = {
        Chat.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        Chat.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
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


class ChatParticipantAdmin(ModelView, model=ChatParticipant):
    name = "Участник чата"
    name_plural = "Участники чатов"
    icon = "fa-solid fa-users"

    # Настройка отображаемых колонок
    column_list = [
        ChatParticipant.id,
        ChatParticipant.chat_id,
        ChatParticipant.company_id,
        ChatParticipant.user_id,
        ChatParticipant.is_admin,
        ChatParticipant.joined_at,
        ChatParticipant.left_at,
    ]

    # Настройка поиска
    column_searchable_list = [
        ChatParticipant.chat_id,
        ChatParticipant.company_id,
        ChatParticipant.user_id,
    ]

    # Настройка фильтров
    column_filters = [
        ChatParticipant.is_admin,
        ChatParticipant.joined_at,
        ChatParticipant.left_at
    ]

    # Настройка сортировки
    column_sortable_list = [
        ChatParticipant.id,
        ChatParticipant.chat_id,
        ChatParticipant.company_id,
        ChatParticipant.user_id,
        ChatParticipant.joined_at,
        ChatParticipant.left_at,
        ChatParticipant.is_admin
    ]

    # Настройка детальной информации
    column_details_list = [
        ChatParticipant.id,
        ChatParticipant.chat_id,
        ChatParticipant.company_id,
        ChatParticipant.user_id,
        ChatParticipant.is_admin,
        ChatParticipant.joined_at,
        ChatParticipant.left_at,
    ]

    # Настройка формы редактирования
    form_columns = [
        ChatParticipant.chat_id,
        ChatParticipant.company_id,
        ChatParticipant.user_id,
        ChatParticipant.is_admin,
        ChatParticipant.left_at,
    ]

    # Настройка отображения в списке
    column_labels = {
        ChatParticipant.id: "ID",
        ChatParticipant.chat_id: "ID чата",
        ChatParticipant.company_id: "ID компании",
        ChatParticipant.user_id: "ID пользователя",
        ChatParticipant.is_admin: "Администратор",
        ChatParticipant.joined_at: "Дата присоединения",
        ChatParticipant.left_at: "Дата выхода",
    }

    # Настройка форматирования
    column_formatters = {
        ChatParticipant.joined_at: lambda m, a: m.joined_at.strftime("%Y-%m-%d %H:%M:%S") if m.joined_at else None,
        ChatParticipant.left_at: lambda m, a: m.left_at.strftime("%Y-%m-%d %H:%M:%S") if m.left_at else None,
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
