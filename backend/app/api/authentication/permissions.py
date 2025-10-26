"""
Система прав доступа для пользователей компаний
"""
import json
from typing import Dict, List, Set
from enum import Enum

from app.api.authentication.models.roles_positions import UserRole


class Permission(str, Enum):
    """Доступные права доступа"""
    # Управление компанией
    COMPANY_MANAGEMENT = "company_management"
    USER_MANAGEMENT = "user_management"
    
    # Разделы ЛК согласно требованиям
    DOCUMENTS = "documents"  # Документы
    CONTRACTS = "contracts"  # Договоры
    SALES = "sales"  # Продажи
    PURCHASES = "purchases"  # Закупки
    MESSAGES = "messages"  # Сообщения
    AUTHORIZATION = "authorization"  # Авторизация
    
    # Дополнительные права
    PRODUCT_MANAGEMENT = "product_management"
    ANNOUNCEMENT_MANAGEMENT = "announcement_management"
    CHAT_ACCESS = "chat_access"
    VIEW_STATISTICS = "view_statistics"


# Права по умолчанию для каждой роли согласно требованиям
DEFAULT_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.OWNER: {
        # Владелец имеет все права
        Permission.COMPANY_MANAGEMENT,
        Permission.USER_MANAGEMENT,
        Permission.DOCUMENTS,
        Permission.CONTRACTS,
        Permission.SALES,
        Permission.PURCHASES,
        Permission.MESSAGES,
        Permission.AUTHORIZATION,
        Permission.PRODUCT_MANAGEMENT,
        Permission.ANNOUNCEMENT_MANAGEMENT,
        Permission.CHAT_ACCESS,
        Permission.VIEW_STATISTICS,
    },
    
    UserRole.ADMIN: {
        # Администратор имеет все права (до 3 штук)
        Permission.COMPANY_MANAGEMENT,
        Permission.USER_MANAGEMENT,
        Permission.DOCUMENTS,
        Permission.CONTRACTS,
        Permission.SALES,
        Permission.PURCHASES,
        Permission.MESSAGES,
        Permission.AUTHORIZATION,
        Permission.PRODUCT_MANAGEMENT,
        Permission.ANNOUNCEMENT_MANAGEMENT,
        Permission.CHAT_ACCESS,
        Permission.VIEW_STATISTICS,
    },
    
    UserRole.USER: {
        # Пользователь имеет стандартный набор прав
        Permission.DOCUMENTS,
        Permission.CONTRACTS,
        Permission.SALES,
        Permission.PURCHASES,
        Permission.MESSAGES,
        Permission.AUTHORIZATION,
    }
}


class PermissionManager:
    """Менеджер для работы с правами доступа"""
    
    @staticmethod
    def get_default_permissions(role: UserRole) -> Set[Permission]:
        """Получить права по умолчанию для роли"""
        return DEFAULT_PERMISSIONS.get(role, set())
    
    @staticmethod
    def serialize_permissions(permissions: Set[Permission]) -> str:
        """Сериализовать права в JSON строку"""
        permission_list = [p.value for p in permissions]
        return json.dumps(permission_list, ensure_ascii=False)
    
    @staticmethod
    def deserialize_permissions(permissions_json: str) -> Set[Permission]:
        """Десериализовать права из JSON строки"""
        if not permissions_json:
            return set()
        
        try:
            permission_list = json.loads(permissions_json)
            return {Permission(p) for p in permission_list if p in [perm.value for perm in Permission]}
        except (json.JSONDecodeError, ValueError):
            return set()
    
    @staticmethod
    def has_permission(user_permissions: str, required_permission: Permission) -> bool:
        """Проверить, есть ли у пользователя определенное право"""
        permissions = PermissionManager.deserialize_permissions(user_permissions)
        return required_permission in permissions
    
    @staticmethod
    def add_permission(user_permissions: str, permission: Permission) -> str:
        """Добавить право пользователю"""
        permissions = PermissionManager.deserialize_permissions(user_permissions)
        permissions.add(permission)
        return PermissionManager.serialize_permissions(permissions)
    
    @staticmethod
    def remove_permission(user_permissions: str, permission: Permission) -> str:
        """Удалить право у пользователя"""
        permissions = PermissionManager.deserialize_permissions(user_permissions)
        permissions.discard(permission)
        return PermissionManager.serialize_permissions(permissions)
    
    @staticmethod
    def set_permissions_for_role(role: UserRole, custom_permissions: Set[Permission] = None) -> str:
        """Установить права для роли (по умолчанию + дополнительные)"""
        permissions = PermissionManager.get_default_permissions(role)
        if custom_permissions:
            permissions.update(custom_permissions)
        return PermissionManager.serialize_permissions(permissions)


def get_available_permissions() -> List[Dict[str, str]]:
    """Получить список всех доступных прав для фронтенда"""
    return [
        {
            "key": permission.value,
            "name": permission.value.replace("_", " ").title(),
            "description": _get_permission_description(permission)
        }
        for permission in Permission
    ]


def _get_permission_description(permission: Permission) -> str:
    """Получить описание права"""
    descriptions = {
        Permission.COMPANY_MANAGEMENT: "Управление компанией",
        Permission.USER_MANAGEMENT: "Управление пользователями",
        Permission.DOCUMENTS: "Документы",
        Permission.CONTRACTS: "Договоры",
        Permission.SALES: "Продажи",
        Permission.PURCHASES: "Закупки",
        Permission.MESSAGES: "Сообщения",
        Permission.AUTHORIZATION: "Авторизация",
        Permission.PRODUCT_MANAGEMENT: "Управление продуктами",
        Permission.ANNOUNCEMENT_MANAGEMENT: "Управление объявлениями",
        Permission.CHAT_ACCESS: "Доступ к чатам",
        Permission.VIEW_STATISTICS: "Просмотр статистики",
    }
    return descriptions.get(permission, "Описание недоступно")
