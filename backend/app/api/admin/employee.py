from sqladmin import ModelView
from app.api.authentication.models.employee import Employee, EmployeePermission


class EmployeeAdmin(ModelView, model=Employee):
    """Админ-панель для управления сотрудниками"""
    
    # Основные настройки
    name = "Сотрудник"
    name_plural = "Сотрудники"
    icon = "fa-solid fa-users"
    
    # Отображаемые колонки
    column_list = [
        "id", "email", "first_name", "last_name", "patronymic", 
        "phone", "position", "role", "is_active", "created_at"
    ]
    
    # Колонки для детального просмотра
    column_details_list = [
        "id", "email", "first_name", "last_name", "patronymic",
        "phone", "position", "role", "is_active", "pending_deletion_at",
        "created_at", "updated_at", "company_id", "user_id"
    ]
    
    # Колонки для редактирования
    form_columns = [
        "email", "first_name", "last_name", "patronymic",
        "phone", "position", "role", "is_active", "company_id", "user_id"
    ]
    
    # Поиск
    column_searchable_list = ["email", "first_name", "last_name", "phone"]
    
    # Фильтры
    column_filters = ["role", "is_active", "company_id"]
    
    # Сортировка по умолчанию
    column_default_sort = [("created_at", True)]
    
    # Настройки формы
    form_widget_args = {
        "email": {"readonly": True},
        "created_at": {"readonly": True},
        "updated_at": {"readonly": True}
    }


class EmployeePermissionAdmin(ModelView, model=EmployeePermission):
    """Админ-панель для управления правами сотрудников"""
    
    # Основные настройки
    name = "Право сотрудника"
    name_plural = "Права сотрудников"
    icon = "fa-solid fa-key"
    
    # Отображаемые колонки
    column_list = [
        "id", "employee_id", "section", "can_view", "can_edit", 
        "can_create", "can_delete"
    ]
    
    # Колонки для детального просмотра
    column_details_list = [
        "id", "employee_id", "section", "can_view", "can_edit",
        "can_create", "can_delete"
    ]
    
    # Колонки для редактирования
    form_columns = [
        "employee_id", "section", "can_view", "can_edit", 
        "can_create", "can_delete"
    ]
    
    # Поиск
    column_searchable_list = ["section"]
    
    # Фильтры
    column_filters = ["section", "can_view", "can_edit", "can_create", "can_delete"]
    
    # Сортировка по умолчанию
    column_default_sort = [("employee_id", True), ("section", True)]
    
    # Настройки формы
    form_widget_args = {
        "id": {"readonly": True}
    }
