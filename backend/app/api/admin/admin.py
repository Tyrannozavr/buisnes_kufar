from sqladmin import ModelView
from app.api.authentication.models.user import User, RegistrationToken
from app.api.company.models.company import Company
from app.api.company.models.official import CompanyOfficial
from datetime import datetime


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
        User.phone,
        User.inn
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
        User.first_name: "Имя",
        User.last_name: "Фамилия",
        User.patronymic: "Отчество",
        User.phone: "Телефон",
        User.inn: "ИНН",
        User.position: "Должность",
        User.is_active: "Активен",
        User.created_at: "Дата создания",
        User.updated_at: "Дата обновления"
    }
    
    # Настройка форматирования
    column_formatters = {
        User.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        User.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None
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


class CompanyAdmin(ModelView, model=Company):
    name = "Компания"
    name_plural = "Компании"
    icon = "fa-solid fa-building"
    
    # Настройка отображаемых колонок
    column_list = [
        Company.id,
        Company.name,
        Company.type,
        Company.trade_activity,
        Company.business_type,
        Company.inn,
        Company.ogrn,
        Company.email,
        Company.phone,
        Company.city,
        Company.created_at,
        Company.updated_at
    ]
    
    # Настройка поиска
    column_searchable_list = [
        Company.name,
        Company.inn,
        Company.ogrn,
        Company.email,
        Company.phone,
        Company.city
    ]
    
    # Настройка фильтров
    column_filters = [
        Company.trade_activity,
        Company.business_type,
        Company.type,
        Company.created_at,
        Company.updated_at
    ]
    
    # Настройка сортировки
    column_sortable_list = [
        Company.id,
        Company.name,
        Company.created_at,
        Company.updated_at,
        Company.trade_activity,
        Company.business_type
    ]
    
    # Настройка детальной информации
    column_details_list = [
        Company.id,
        Company.name,
        Company.slug,
        Company.logo,
        Company.type,
        Company.trade_activity,
        Company.business_type,
        Company.activity_type,
        Company.description,
        Company.country,
        Company.federal_district,
        Company.region,
        Company.city,
        Company.full_name,
        Company.inn,
        Company.ogrn,
        Company.kpp,
        Company.registration_date,
        Company.legal_address,
        Company.production_address,
        Company.phone,
        Company.email,
        Company.website,
        Company.total_views,
        Company.monthly_views,
        Company.total_purchases,
        Company.created_at,
        Company.updated_at,
        Company.user_id
    ]
    
    # Настройка формы редактирования
    form_columns = [
        Company.name,
        Company.type,
        Company.trade_activity,
        Company.business_type,
        Company.activity_type,
        Company.description,
        Company.country,
        Company.federal_district,
        Company.region,
        Company.city,
        Company.full_name,
        Company.inn,
        Company.ogrn,
        Company.kpp,
        Company.registration_date,
        Company.legal_address,
        Company.production_address,
        Company.phone,
        Company.email,
        Company.website,
        Company.user_id
    ]
    
    # Настройка отображения в списке
    column_labels = {
        Company.id: "ID",
        Company.name: "Название",
        Company.slug: "Slug",
        Company.logo: "Логотип",
        Company.type: "Тип",
        Company.trade_activity: "Торговая деятельность",
        Company.business_type: "Тип бизнеса",
        Company.activity_type: "Вид деятельности",
        Company.description: "Описание",
        Company.country: "Страна",
        Company.federal_district: "Федеральный округ",
        Company.region: "Регион",
        Company.city: "Город",
        Company.full_name: "Полное наименование",
        Company.inn: "ИНН",
        Company.ogrn: "ОГРН",
        Company.kpp: "КПП",
        Company.registration_date: "Дата регистрации",
        Company.legal_address: "Юридический адрес",
        Company.production_address: "Производственный адрес",
        Company.phone: "Телефон",
        Company.email: "Email",
        Company.website: "Веб-сайт",
        Company.total_views: "Всего просмотров",
        Company.monthly_views: "Просмотров за месяц",
        Company.total_purchases: "Всего покупок",
        Company.created_at: "Дата создания",
        Company.updated_at: "Дата обновления",
        Company.user_id: "ID пользователя"
    }
    
    # Настройка форматирования
    column_formatters = {
        Company.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        Company.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
        Company.registration_date: lambda m, a: m.registration_date.strftime("%Y-%m-%d") if m.registration_date else None
    }
    
    # Настройка валидации формы
    form_widget_args = {
        "slug": {"readonly": True},
        "created_at": {"readonly": True},
        "updated_at": {"readonly": True},
        "total_views": {"readonly": True},
        "monthly_views": {"readonly": True},
        "total_purchases": {"readonly": True}
    }
    
    column_default_sort = (Company.created_at, True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class CompanyOfficialAdmin(ModelView, model=CompanyOfficial):
    name = "Представитель компании"
    name_plural = "Представители компаний"
    icon = "fa-solid fa-user-tie"
    
    # Настройка отображаемых колонок
    column_list = [
        CompanyOfficial.id,
        CompanyOfficial.position,
        CompanyOfficial.full_name,
        CompanyOfficial.company_id
    ]
    
    # Настройка поиска
    column_searchable_list = [
        CompanyOfficial.position,
        CompanyOfficial.full_name,
        CompanyOfficial.company_id
    ]
    
    # Настройка фильтров
    column_filters = [
        CompanyOfficial.company_id
    ]
    
    # Настройка сортировки
    column_sortable_list = [
        CompanyOfficial.id,
        CompanyOfficial.position,
        CompanyOfficial.full_name,
        CompanyOfficial.company_id
    ]
    
    # Настройка детальной информации
    column_details_list = [
        CompanyOfficial.id,
        CompanyOfficial.position,
        CompanyOfficial.full_name,
        CompanyOfficial.company_id
    ]
    
    # Настройка формы редактирования
    form_columns = [
        CompanyOfficial.position,
        CompanyOfficial.full_name,
        CompanyOfficial.company_id
    ]
    
    # Настройка отображения в списке
    column_labels = {
        CompanyOfficial.id: "ID",
        CompanyOfficial.position: "Должность",
        CompanyOfficial.full_name: "ФИО",
        CompanyOfficial.company_id: "ID компании"
    }
    
    column_default_sort = (CompanyOfficial.id, True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True 