from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.api.authentication.dependencies import get_current_user_id_dep, user_repository_dep
from app.api.authentication.schemas.user import (
    UserWithPermissions, UserListResponse, UserPermissionUpdate, UserRoleUpdate
)
from app.api.authentication.models.user import UserRole
from app.api.authentication.permissions import PermissionManager, Permission, get_available_permissions
from app.api.company.dependencies import company_service_dep
from app_logging.logger import logger

router = APIRouter()


@router.get("/users", response_model=UserListResponse)
async def get_company_users(
    user_repository: user_repository_dep,
    company_service: company_service_dep,
    current_user_id: int = Depends(get_current_user_id_dep),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100)
):
    """Получить список пользователей компании"""
    # Получаем компанию текущего пользователя
    company_profile = await company_service.get_company_by_user_id(current_user_id)
    if not company_profile.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Проверяем права доступа
    current_user = await user_repository.get_user_by_id(current_user_id)
    if not PermissionManager.has_permission(current_user.permissions or "", Permission.USER_MANAGEMENT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Получаем пользователей компании
    users, total = await user_repository.get_users_by_company_id(
        company_profile.company_id, page, per_page
    )
    
    # Преобразуем в формат с правами
    users_with_permissions = []
    for user in users:
        permissions_dict = None
        if user.permissions:
            permissions_set = PermissionManager.deserialize_permissions(user.permissions)
            permissions_dict = {p.value: True for p in permissions_set}
        
        users_with_permissions.append(
            UserWithPermissions.from_user(user, permissions_dict)
        )
    
    return UserListResponse(
        users=users_with_permissions,
        total=total,
        page=page,
        per_page=per_page
    )


@router.put("/users/{user_id}/role", response_model=dict)
async def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    user_repository: user_repository_dep,
    company_service: company_service_dep,
    current_user_id: int = Depends(get_current_user_id_dep)
):
    """Обновить роль пользователя"""
    # Получаем компанию текущего пользователя
    company_profile = await company_service.get_company_by_user_id(current_user_id)
    if not company_profile.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Проверяем права доступа
    current_user = await user_repository.get_user_by_id(current_user_id)
    if not PermissionManager.has_permission(current_user.permissions or "", Permission.USER_MANAGEMENT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Проверяем, что пользователь принадлежит той же компании
    target_user = await user_repository.get_user_by_id(user_id)
    if not target_user or target_user.company_id != company_profile.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Нельзя изменить роль владельца
    if target_user.role == UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change owner role"
        )
    
    # Обновляем роль
    success = await user_repository.update_user_role(user_id, role_data.role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )
    
    logger.info(f"Updated user {user_id} role to {role_data.role}")
    return {"success": True, "message": "User role updated successfully"}


@router.put("/users/{user_id}/permissions", response_model=dict)
async def update_user_permissions(
    user_id: int,
    permissions_data: UserPermissionUpdate,
    user_repository: user_repository_dep,
    company_service: company_service_dep,
    current_user_id: int = Depends(get_current_user_id_dep)
):
    """Обновить права пользователя"""
    # Получаем компанию текущего пользователя
    company_profile = await company_service.get_company_by_user_id(current_user_id)
    if not company_profile.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Проверяем права доступа
    current_user = await user_repository.get_user_by_id(current_user_id)
    if not PermissionManager.has_permission(current_user.permissions or "", Permission.USER_PERMISSIONS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Проверяем, что пользователь принадлежит той же компании
    target_user = await user_repository.get_user_by_id(user_id)
    if not target_user or target_user.company_id != company_profile.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Нельзя изменить права владельца
    if target_user.role == UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change owner permissions"
        )
    
    # Преобразуем права в JSON
    permissions_set = set()
    for permission_key, granted in permissions_data.permissions.items():
        try:
            permission = Permission(permission_key)
            if granted:
                permissions_set.add(permission)
        except ValueError:
            logger.warning(f"Unknown permission: {permission_key}")
    
    permissions_json = PermissionManager.serialize_permissions(permissions_set)
    
    # Обновляем права
    success = await user_repository.update_user_permissions(user_id, permissions_json)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user permissions"
        )
    
    logger.info(f"Updated user {user_id} permissions")
    return {"success": True, "message": "User permissions updated successfully"}


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    user_repository: user_repository_dep,
    company_service: company_service_dep,
    current_user_id: int = Depends(get_current_user_id_dep)
):
    """Удалить пользователя (деактивация)"""
    # Получаем компанию текущего пользователя
    company_profile = await company_service.get_company_by_user_id(current_user_id)
    if not company_profile.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Проверяем права доступа
    current_user = await user_repository.get_user_by_id(current_user_id)
    if not PermissionManager.has_permission(current_user.permissions or "", Permission.USER_MANAGEMENT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Проверяем, что пользователь принадлежит той же компании
    target_user = await user_repository.get_user_by_id(user_id)
    if not target_user or target_user.company_id != company_profile.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Нельзя удалить владельца
    if target_user.role == UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete owner"
        )
    
    # Нельзя удалить самого себя
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    # Удаляем пользователя (деактивация)
    success = await user_repository.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    logger.info(f"Deleted user {user_id}")
    return {"success": True, "message": "User deleted successfully"}


@router.get("/permissions", response_model=dict)
async def get_available_permissions_list():
    """Получить список доступных прав"""
    permissions = get_available_permissions()
    return {"permissions": permissions}
