from sqladmin import ModelView
from sqladmin.fields import QuerySelectField
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.api.company.models.company import Company
from app.api.company.models.official import CompanyOfficial


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
        Company.is_active,
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
        # Bank details
        Company.current_account_number,
        Company.bic,
        Company.vat_rate,
        Company.correspondent_bank_account,
        Company.bank_name,
        # Statistics
        Company.total_views,
        Company.monthly_views,
        Company.total_purchases,
        Company.created_at,
        Company.updated_at
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
        # Bank details
        Company.current_account_number,
        Company.bic,
        Company.vat_rate,
        Company.correspondent_bank_account,
        Company.bank_name
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
        # Bank details
        Company.current_account_number: "Расчетный счет",
        Company.bic: "БИК",
        Company.vat_rate: "Ставка НДС (%)",
        Company.correspondent_bank_account: "Корреспондентский счет",
        Company.bank_name: "Название банка",
        # Statistics
        Company.total_views: "Всего просмотров",
        Company.monthly_views: "Просмотров за месяц",
        Company.total_purchases: "Всего покупок",
        Company.created_at: "Дата создания",
        Company.updated_at: "Дата обновления"
    }

    # Настройка форматирования
    column_formatters = {
        Company.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        Company.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
        Company.registration_date: lambda m, a: m.registration_date.strftime(
            "%Y-%m-%d") if m.registration_date else None
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

    # Убираем кастомную логику удаления - используем стандартную SQLAdmin с каскадным удалением
    # async def delete_model(self, request, pk):
    #     """Кастомная логика удаления компании с правильным каскадным удалением"""
    #     from app.db.base import AsyncSessionLocal
    #     
    #     async with AsyncSessionLocal() as session:
    #         # Получаем компанию
    #         company = await session.get(Company, pk)
    #         if not company:
    #             return
    #         
    #         # Удаляем компанию - каскадное удаление должно сработать автоматически
    #         await session.delete(company)
    #         await session.commit()


class CompanyOfficialAdmin(ModelView, model=CompanyOfficial):
    name = "Представитель компании"
    name_plural = "Представители компаний"
    icon = "fa-solid fa-user-tie"

    # Настройка отображаемых колонок
    column_list = [
        CompanyOfficial.id,
        CompanyOfficial.position,
        CompanyOfficial.full_name,
        'company.name'  # Отображаем название компании
    ]

    # Настройка поиска
    column_searchable_list = [
        CompanyOfficial.position,
        CompanyOfficial.full_name,
        'company.name'  # Поиск по названию компании
    ]

    # Настройка фильтров
    column_filters = [
        CompanyOfficial.position,
        'company.name'  # Фильтр по названию компании
    ]

    # Настройка сортировки
    column_sortable_list = [
        'id',
        'position',
        'full_name',
        'company.name'  # Сортировка по названию компании
    ]

    # Настройка детальной информации
    column_details_list = [
        CompanyOfficial.id,
        CompanyOfficial.position,
        CompanyOfficial.full_name,
        'company'
    ]

    # Настройка формы редактирования
    form_columns = [
        CompanyOfficial.position,
        CompanyOfficial.full_name,
        "company"
    ]

    # Настройка отображения в списке
    column_labels = {
        CompanyOfficial.id: "ID",
        CompanyOfficial.position: "Должность",
        CompanyOfficial.full_name: "ФИО",
        'company.name': "Компания"
    }

    column_default_sort = ('id', True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # Добавляем настройку для выпадающего списка компаний
    form_overrides = {
        'company': QuerySelectField
    }

    def get_form(self):
        form = super().get_form()
        form.company.query = Company.query.order_by(Company.name)
        form.company.get_label = lambda x: x.name
        return form
