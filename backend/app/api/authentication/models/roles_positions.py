"""
Единый модуль для управления ролями и должностями
"""
from enum import Enum
from typing import Dict, List


class UserRole(str, Enum):
    """Роли пользователей в системе"""
    OWNER = "owner"  # Владелец компании (создатель)
    ADMIN = "admin"  # Администратор (до 3 штук)
    USER = "user"    # Обычный пользователь (неограниченно)


class Position(str, Enum):
    """Должности в компании"""
    OWNER = "owner"  # Владелец компании
    GENERAL_DIRECTOR = "general_director"  # Генеральный директор
    EXECUTIVE_DIRECTOR = "executive_director"  # Исполнительный директор
    DIRECTOR = "director"  # Директор
    DEPUTY_DIRECTOR = "deputy_director"  # Заместитель директора
    CHIEF_ACCOUNTANT = "chief_accountant"  # Главный бухгалтер
    ACCOUNTANT = "accountant"  # Бухгалтер


class RoleManager:
    """Менеджер для работы с ролями и должностями"""
    
    # Маппинг ролей на человекочитаемые названия
    ROLE_LABELS = {
        UserRole.OWNER: "Владелец",
        UserRole.ADMIN: "Администратор", 
        UserRole.USER: "Пользователь"
    }
    
    # Маппинг должностей на человекочитаемые названия
    POSITION_LABELS = {
        Position.OWNER: "Владелец",
        Position.GENERAL_DIRECTOR: "Генеральный директор",
        Position.EXECUTIVE_DIRECTOR: "Исполнительный директор",
        Position.DIRECTOR: "Директор",
        Position.DEPUTY_DIRECTOR: "Заместитель директора",
        Position.CHIEF_ACCOUNTANT: "Главный бухгалтер",
        Position.ACCOUNTANT: "Бухгалтер"
    }
    
    # Описания ролей для регистрации
    ROLE_DESCRIPTIONS = {
        UserRole.ADMIN: "Полные права доступа (до 3 администраторов в компании)",
        UserRole.USER: "Стандартный набор прав (неограниченное количество)"
    }
    
    @staticmethod
    def get_registration_roles() -> List[Dict[str, str]]:
        """Получить роли для регистрации (Администратор и Пользователь)"""
        return [
            {
                "value": UserRole.ADMIN.value,
                "label": RoleManager.ROLE_LABELS[UserRole.ADMIN],
                "description": RoleManager.ROLE_DESCRIPTIONS[UserRole.ADMIN]
            },
            {
                "value": UserRole.USER.value,
                "label": RoleManager.ROLE_LABELS[UserRole.USER],
                "description": RoleManager.ROLE_DESCRIPTIONS[UserRole.USER]
            }
        ]
    
    @staticmethod
    def get_all_positions() -> List[Dict[str, str]]:
        """Получить все должности"""
        return [
            {
                "value": position.value,
                "label": RoleManager.POSITION_LABELS[position]
            }
            for position in Position
        ]
    
