from sqladmin import ModelView

from app.api.authentication.models.user import User, RegistrationToken, PasswordRecoveryCode


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"

    # Настройка отображаемых колонок
    column_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.patronymic,
        User.phone,
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
        User.created_at,
        User.updated_at
    ]

    # Настройка сортировки
    column_sortable_list = [
        User.id,
        User.email,
        User.created_at,
        User.updated_at,
        User.is_active
    ]

    # Настройка детальной информации
    column_details_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.patronymic,
        User.phone,
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
        User.position,
        User.is_active,
    ]

    # Настройка отображения в списке
    column_labels = {
        User.id: "ID",
        User.email: "Email",
        User.first_name: "Имя",
        User.last_name: "Фамилия",
        User.patronymic: "Отчество",
        User.phone: "Телефон",
        User.position: "Должность",
        User.is_active: "Активен",
        User.created_at: "Дата создания",
        User.updated_at: "Дата обновления"
    }

    # Настройка форматирования
    column_formatters = {
        User.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        User.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
    }

    # Настройка валидации формы
    form_widget_args = {
        "email": {"readonly": True},  # Email нельзя менять
        "created_at": {"readonly": True},  # Дата создания только для чтения
        "updated_at": {"readonly": True},  # Дата обновления только для чтения
    }

    column_default_sort = (User.created_at, True)
    can_create = False
    can_edit = True
    can_delete = True
    can_view_details = True


class RegistrationTokenAdmin(ModelView, model=RegistrationToken):
    name = "Токен регистрации"
    name_plural = "Токены регистрации"
    icon = "fa-solid fa-key"

    # Настройка отображаемых колонок
    column_list = [
        RegistrationToken.id,
        RegistrationToken.token,
        RegistrationToken.email,
        RegistrationToken.user_id,
        RegistrationToken.created_at,
        RegistrationToken.expires_at,
        RegistrationToken.is_used
    ]

    # Настройка поиска
    column_searchable_list = [
        RegistrationToken.email,
        RegistrationToken.token,
        RegistrationToken.user_id
    ]

    # Настройка фильтров
    column_filters = [
        RegistrationToken.is_used,
        RegistrationToken.created_at,
        RegistrationToken.expires_at,
        RegistrationToken.user_id
    ]

    # Настройка сортировки
    column_sortable_list = [
        RegistrationToken.id,
        RegistrationToken.email,
        RegistrationToken.created_at,
        RegistrationToken.expires_at,
        RegistrationToken.is_used,
        RegistrationToken.user_id
    ]

    # Настройка детальной информации
    column_details_list = [
        RegistrationToken.id,
        RegistrationToken.token,
        RegistrationToken.email,
        RegistrationToken.user_id,
        RegistrationToken.created_at,
        RegistrationToken.expires_at,
        RegistrationToken.is_used
    ]

    # Настройка формы редактирования
    form_columns = [
        RegistrationToken.token,
        RegistrationToken.email,
        RegistrationToken.user_id,
        RegistrationToken.expires_at,
        RegistrationToken.is_used
    ]

    # Настройка отображения в списке
    column_labels = {
        RegistrationToken.id: "ID",
        RegistrationToken.token: "Токен",
        RegistrationToken.email: "Email",
        RegistrationToken.user_id: "ID пользователя",
        RegistrationToken.created_at: "Дата создания",
        RegistrationToken.expires_at: "Срок действия",
        RegistrationToken.is_used: "Использован"
    }

    # Настройка форматирования
    column_formatters = {
        RegistrationToken.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        RegistrationToken.expires_at: lambda m, a: m.expires_at.strftime("%Y-%m-%d %H:%M:%S") if m.expires_at else None
    }

    # Настройка валидации формы
    form_widget_args = {
        "token": {"readonly": True},  # Токен нельзя менять
        "email": {"readonly": True},  # Email нельзя менять
        "created_at": {"readonly": True},  # Дата создания только для чтения
    }

    column_default_sort = (RegistrationToken.created_at, True)
    can_create = False
    can_edit = True  # Разрешаем редактирование
    can_delete = True
    can_view_details = True


class PasswordRecoveryCodeAdmin(ModelView, model=PasswordRecoveryCode):
    name = "Код восстановления пароля"
    name_plural = "Коды восстановления пароля"
    icon = "fa-solid fa-unlock"

    # Настройка отображаемых колонок
    column_list = [
        PasswordRecoveryCode.id,
        PasswordRecoveryCode.email,
        PasswordRecoveryCode.code,
        PasswordRecoveryCode.created_at,
        PasswordRecoveryCode.expires_at,
        PasswordRecoveryCode.is_used
    ]

    # Настройка поиска
    column_searchable_list = [
        PasswordRecoveryCode.email,
        PasswordRecoveryCode.code
    ]

    # Настройка фильтров
    column_filters = [
        PasswordRecoveryCode.is_used,
        PasswordRecoveryCode.created_at,
        PasswordRecoveryCode.expires_at
    ]

    # Настройка сортировки
    column_sortable_list = [
        PasswordRecoveryCode.id,
        PasswordRecoveryCode.email,
        PasswordRecoveryCode.created_at,
        PasswordRecoveryCode.expires_at,
        PasswordRecoveryCode.is_used
    ]

    # Настройка детальной информации
    column_details_list = [
        PasswordRecoveryCode.id,
        PasswordRecoveryCode.email,
        PasswordRecoveryCode.code,
        PasswordRecoveryCode.created_at,
        PasswordRecoveryCode.expires_at,
        PasswordRecoveryCode.is_used
    ]

    # Настройка формы редактирования
    form_columns = [
        PasswordRecoveryCode.email,
        PasswordRecoveryCode.code,
        PasswordRecoveryCode.expires_at,
        PasswordRecoveryCode.is_used
    ]

    # Настройка отображения в списке
    column_labels = {
        PasswordRecoveryCode.id: "ID",
        PasswordRecoveryCode.email: "Email",
        PasswordRecoveryCode.code: "Код",
        PasswordRecoveryCode.created_at: "Дата создания",
        PasswordRecoveryCode.expires_at: "Срок действия",
        PasswordRecoveryCode.is_used: "Использован"
    }

    # Настройка форматирования
    column_formatters = {
        PasswordRecoveryCode.created_at: lambda m, a: m.created_at.strftime(
            "%Y-%m-%d %H:%M:%S") if m.created_at else None,
        PasswordRecoveryCode.expires_at: lambda m, a: m.expires_at.strftime(
            "%Y-%m-%d %H:%M:%S") if m.expires_at else None
    }

    # Настройка валидации формы
    form_widget_args = {
        "email": {"readonly": True},  # Email нельзя менять
        "code": {"readonly": True},  # Код нельзя менять
        "created_at": {"readonly": True},  # Дата создания только для чтения
    }

    column_default_sort = (PasswordRecoveryCode.created_at, True)
    can_create = False
    can_edit = True
    can_delete = True
    can_view_details = True
