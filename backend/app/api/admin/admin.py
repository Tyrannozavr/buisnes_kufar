from sqladmin import ModelView
from app.api.authentication.models.user import User, RegistrationToken
from datetime import datetime


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    
    # Настройка отображаемых колонок
    column_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.patronymic,
        User.phone,
        User.inn,
        User.position,
        User.is_active,
        User.created_at,
        User.updated_at,
    ]
    
    # Настройка поиска
    column_searchable_list = [
        User.email,
        User.first_name,
        User.last_name,
        User.phone
    ]
    
    # Настройка фильтров
    column_filters = [
        User.is_active,
    ]
    
    # Настройка сортировки
    column_sortable_list = [
        User.id,
        User.email,
        User.created_at,
    ]
    
    # Настройка детальной информации
    column_details_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.patronymic,
        User.phone,
        User.inn,
        User.position,
        User.is_active,
        User.created_at,
        User.updated_at
    ]
    
    # Настройка формы редактирования
    form_columns = [
        User.email,
        User.first_name,
        User.last_name,
        User.patronymic,
        User.phone,
        User.inn,
        User.position,
        User.is_active,
    ]
    
    # Настройка отображения в списке
    column_labels = {
        User.id: "ID",
        User.email: "Email",
        User.first_name: "First Name",
        User.last_name: "Last Name",
        User.patronymic: "Patronymic",
        User.phone: "Phone",
        User.inn: "INN",
        User.position: "Position",
        User.is_active: "Active",
        User.created_at: "Created At",
        User.updated_at: "Updated At"
    }
    
    # Настройка форматирования
    column_formatters = {
        User.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        User.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None
    }
    
    column_default_sort = (User.created_at, True)
    can_create = False
    can_edit = True
    can_delete = True


class RegistrationTokenAdmin(ModelView, model=RegistrationToken):
    name = "Registration Token"
    name_plural = "Registration Tokens"
    icon = "fa-solid fa-key"
    
    # Настройка отображаемых колонок
    column_list = [
        RegistrationToken.token,
        RegistrationToken.email,
        RegistrationToken.created_at,
        RegistrationToken.expires_at,
        RegistrationToken.is_used
    ]
    
    # Настройка поиска
    column_searchable_list = [
        RegistrationToken.email,
        RegistrationToken.token
    ]
    
    # Настройка фильтров
    column_filters = [
        RegistrationToken.is_used,
        RegistrationToken.created_at,
        RegistrationToken.expires_at
    ]
    
    # Настройка сортировки
    column_sortable_list = [
        RegistrationToken.email,
        RegistrationToken.created_at,
        RegistrationToken.expires_at,
        RegistrationToken.is_used
    ]
    
    # Настройка детальной информации
    column_details_list = [
        RegistrationToken.token,
        RegistrationToken.email,
        RegistrationToken.created_at,
        RegistrationToken.expires_at,
        RegistrationToken.is_used
    ]
    
    # Настройка отображения в списке
    column_labels = {
        RegistrationToken.token: "Token",
        RegistrationToken.email: "Email",
        RegistrationToken.created_at: "Created At",
        RegistrationToken.expires_at: "Expires At",
        RegistrationToken.is_used: "Used"
    }
    
    # Настройка форматирования
    column_formatters = {
        RegistrationToken.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        RegistrationToken.expires_at: lambda m, a: m.expires_at.strftime("%Y-%m-%d %H:%M:%S") if m.expires_at else None
    }
    
    # Запрет на создание и редактирование токенов через админку
    can_create = False
    can_edit = False
    can_delete = True  # Разрешаем удаление для очистки старых токенов 