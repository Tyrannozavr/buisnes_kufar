import json
import os
import uuid
from typing import List
from sqladmin import ModelView
from sqladmin.fields import QuerySelectField
from sqlalchemy.orm import relationship
from app.api.company.models.announcement import Announcement
from app.api.company.models.company import Company


class AnnouncementAdmin(ModelView, model=Announcement):
    name = "Объявление"
    name_plural = "Объявления"
    icon = "fa-solid fa-bullhorn"

    # Настройка отображаемых колонок
    column_list = [
        Announcement.id,
        Announcement.title,
        Announcement.category,
        Announcement.published,
        'company.name',  # Отображаем название компании
        Announcement.created_at,
        Announcement.updated_at
    ]

    # Настройка поиска
    column_searchable_list = [
        Announcement.title,
        Announcement.content,
        Announcement.category,
        'company.name'  # Поиск по названию компании
    ]

    # Настройка фильтров
    column_filters = [
        Announcement.category,
        Announcement.published,
        'company.name',  # Фильтр по названию компании
        Announcement.created_at,
        Announcement.updated_at
    ]

    # Настройка сортировки
    column_sortable_list = [
        Announcement.id,
        Announcement.title,
        Announcement.category,
        Announcement.published,
        Announcement.created_at,
        Announcement.updated_at,
        'company.name'  # Сортировка по названию компании
    ]

    # Настройка детальной информации
    column_details_list = [
        Announcement.id,
        Announcement.title,
        Announcement.content,
        Announcement.category,
        Announcement.images,
        Announcement.published,
        Announcement.created_at,
        Announcement.updated_at,
        Announcement.company_id,
        'company'
    ]

    # Настройка формы редактирования
    form_columns = [
        Announcement.title,
        Announcement.content,
        Announcement.category,
        Announcement.published,
        "company"
    ]

    # Настройка отображения в списке
    column_labels = {
        Announcement.id: "ID",
        Announcement.title: "Заголовок",
        Announcement.content: "Содержание",
        Announcement.category: "Категория",
        Announcement.images: "Изображения",
        Announcement.published: "Опубликовано",
        Announcement.created_at: "Дата создания",
        Announcement.updated_at: "Дата обновления",
        Announcement.company_id: "ID компании",
        'company.name': "Компания"
    }

    # Настройка форматирования
    column_formatters = {
        Announcement.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
        Announcement.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
        Announcement.content: lambda m, a: m.content[:100] + "..." if len(m.content) > 100 else m.content,
        Announcement.images: lambda m, a: self._format_images(m.images)
    }

    # Настройка валидации формы
    form_widget_args = {
        "created_at": {"readonly": True},
        "updated_at": {"readonly": True},
        "company_id": {"readonly": True},
        "content": {"rows": 10}
    }

    column_default_sort = (Announcement.created_at, True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # Добавляем настройку для выпадающего списка компаний
    form_overrides = {
        "company": QuerySelectField
    }

    def _format_images(self, images: List[str]) -> str:
        """Форматирует изображения для отображения в админке"""
        if not images:
            return "Нет изображений"
        
        # Показываем количество и первые несколько путей
        count = len(images)
        preview = images[:3]  # Показываем первые 3 изображения
        
        result = f"{count} изображений:\n"
        for i, img_path in enumerate(preview, 1):
            result += f"{i}. {img_path}\n"
        
        if count > 3:
            result += f"... и еще {count - 3} изображений"
        
        return result

    def get_form(self):
        form = super().get_form()
        form.company.query_factory = lambda: self.session.query(Company).all()
        return form

    def on_model_change(self, model, is_created):
        """Обработчик изменения модели"""
        # Убеждаемся, что images всегда является списком
        if model.images is None:
            model.images = []
        elif isinstance(model.images, str):
            try:
                model.images = json.loads(model.images)
            except json.JSONDecodeError:
                model.images = []

    def on_model_delete(self, model):
        """Обработчик удаления модели"""
        # Удаляем файлы изображений при удалении объявления
        if model.images:
            for image_path in model.images:
                if image_path.startswith('/uploads/'):
                    full_path = os.path.join(os.getcwd(), image_path.lstrip('/'))
                    try:
                        if os.path.exists(full_path):
                            os.remove(full_path)
                    except Exception as e:
                        print(f"Error deleting image {full_path}: {e}")

    def on_form_prefill(self, form, id):
        """Заполняет форму данными при редактировании"""
        super().on_form_prefill(form, id)
        
        # Добавляем информацию об изображениях в поле content как комментарий
        announcement = self.session.query(Announcement).get(id)
        if announcement and announcement.images:
            images_info = self._format_images(announcement.images)
            # Добавляем информацию об изображениях в начало контента как комментарий
            if not form.content.data.startswith("<!-- IMAGES INFO:"):
                form.content.data = f"<!-- IMAGES INFO:\n{images_info}\n-->\n\n{form.content.data}" 