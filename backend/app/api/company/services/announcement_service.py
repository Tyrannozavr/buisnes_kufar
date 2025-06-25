import os
import uuid
import base64
import aiofiles
from typing import Optional, List
from fastapi import HTTPException, status, UploadFile

from app.api.company.repositories.announcement_repository import AnnouncementRepository
from app.api.company.schemas.announcements import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse, AnnouncementListResponse
from app.api.authentication.models import User


class AnnouncementService:
    def __init__(self, announcement_repository: AnnouncementRepository):
        self.announcement_repository = announcement_repository
        self.upload_dir = "uploads/announcement_images"

    async def _save_base64_image(self, base64_data: str, announcement_id: int) -> str:
        """Сохраняет base64 изображение в файл и возвращает относительный путь"""
        try:
            # Извлекаем данные из base64
            if ',' in base64_data:
                header, data = base64_data.split(',', 1)
            else:
                data = base64_data
            
            # Определяем расширение файла
            if 'data:image/jpeg' in base64_data or 'data:image/jpg' in base64_data:
                ext = '.jpg'
            elif 'data:image/png' in base64_data:
                ext = '.png'
            elif 'data:image/gif' in base64_data:
                ext = '.gif'
            elif 'data:image/webp' in base64_data:
                ext = '.webp'
            else:
                ext = '.jpg'  # По умолчанию
            
            # Создаем директорию если не существует
            os.makedirs(self.upload_dir, exist_ok=True)
            
            # Генерируем уникальное имя файла
            filename = f"{uuid.uuid4()}{ext}"
            filepath = os.path.join(self.upload_dir, filename)
            
            # Декодируем и сохраняем файл
            image_data = base64.b64decode(data)
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(image_data)
            
            # Возвращаем относительный путь
            return f"/uploads/announcement_images/{filename}"
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save image: {str(e)}"
            )

    async def _process_images(self, images: List[str], announcement_id: int) -> List[str]:
        """Обрабатывает список base64 изображений и возвращает относительные пути"""
        if not images:
            return []
        
        image_paths = []
        for image_data in images:
            if image_data.startswith('data:image/'):
                # Это base64 изображение, сохраняем его
                image_path = await self._save_base64_image(image_data, announcement_id)
                image_paths.append(image_path)
            else:
                # Это уже относительный путь, оставляем как есть
                image_paths.append(image_data)
        
        return image_paths

    async def create_announcement(self, user: User, announcement_data: AnnouncementCreate, notifications: dict) -> AnnouncementResponse:
        """Создать новое объявление для компании пользователя"""
        # Получаем компанию пользователя через существующую сессию
        from app.api.company.repositories.company_repository import CompanyRepository
        
        # Используем ту же сессию, что и в announcement_repository
        company_repository = CompanyRepository(session=self.announcement_repository.session)
        company = await company_repository.get_by_user_id(user.id)
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Выводим notifications на печать (как требовалось)
        print("Notifications:", notifications)
        
        # Обрабатываем изображения
        processed_images = await self._process_images(announcement_data.images or [], 0)
        
        # Создаем данные для сохранения (без base64)
        save_data = announcement_data.model_dump()
        save_data['images'] = processed_images
        
        # Создаем объявление
        announcement = await self.announcement_repository.create(
            AnnouncementCreate(**save_data), company.id
        )
        return AnnouncementResponse.model_validate(announcement)

    async def get_announcement(self, user: User, announcement_id: int) -> AnnouncementResponse:
        """Получить объявление по ID"""
        announcement = await self.announcement_repository.get_by_id(announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found"
            )
        
        # Получаем компанию пользователя через существующую сессию
        from app.api.company.repositories.company_repository import CompanyRepository
        
        # Используем ту же сессию, что и в announcement_repository
        company_repository = CompanyRepository(session=self.announcement_repository.session)
        company = await company_repository.get_by_user_id(user.id)
        
        if not company or announcement.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this announcement"
            )
        
        return AnnouncementResponse.model_validate(announcement)

    async def get_company_announcements(self, user: User, page: int = 1, per_page: int = 10) -> AnnouncementListResponse:
        """Получить все объявления компании пользователя"""
        # Получаем компанию пользователя через существующую сессию
        from app.api.company.repositories.company_repository import CompanyRepository
        
        # Используем ту же сессию, что и в announcement_repository
        company_repository = CompanyRepository(session=self.announcement_repository.session)
        company = await company_repository.get_by_user_id(user.id)
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        announcements, total = await self.announcement_repository.get_by_company_id(
            company.id, page, per_page
        )
        
        return AnnouncementListResponse(
            announcements=[AnnouncementResponse.model_validate(announcement) for announcement in announcements],
            total=total,
            page=page,
            per_page=per_page
        )

    async def update_announcement(self, user: User, announcement_id: int, announcement_data: AnnouncementUpdate) -> AnnouncementResponse:
        """Обновить объявление"""
        # Проверяем, что объявление принадлежит компании пользователя
        announcement = await self.announcement_repository.get_by_id(announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found"
            )
        
        # Получаем компанию пользователя через существующую сессию
        from app.api.company.repositories.company_repository import CompanyRepository
        
        # Используем ту же сессию, что и в announcement_repository
        company_repository = CompanyRepository(session=self.announcement_repository.session)
        company = await company_repository.get_by_user_id(user.id)
        
        if not company or announcement.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this announcement"
            )
        
        # Обрабатываем изображения если они есть
        update_data = announcement_data.model_dump(exclude_unset=True)
        if 'images' in update_data and update_data['images'] is not None:
            update_data['images'] = await self._process_images(update_data['images'], announcement_id)
        
        updated_announcement = await self.announcement_repository.update(announcement_id, AnnouncementUpdate(**update_data))
        if not updated_announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found after update"
            )
        
        return AnnouncementResponse.model_validate(updated_announcement)

    async def delete_announcement(self, user: User, announcement_id: int) -> bool:
        """Удалить объявление"""
        # Проверяем, что объявление принадлежит компании пользователя
        announcement = await self.announcement_repository.get_by_id(announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found"
            )
        
        # Получаем компанию пользователя через существующую сессию
        from app.api.company.repositories.company_repository import CompanyRepository
        
        # Используем ту же сессию, что и в announcement_repository
        company_repository = CompanyRepository(session=self.announcement_repository.session)
        company = await company_repository.get_by_user_id(user.id)
        
        if not company or announcement.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this announcement"
            )
        
        return await self.announcement_repository.delete(announcement_id)

    async def get_public_announcements(self, company_id: int, page: int = 1, per_page: int = 10) -> AnnouncementListResponse:
        """Получить только опубликованные объявления компании (публичный доступ)"""
        announcements, total = await self.announcement_repository.get_published_by_company_id(
            company_id, page, per_page
        )
        
        return AnnouncementListResponse(
            announcements=[AnnouncementResponse.model_validate(announcement) for announcement in announcements],
            total=total,
            page=page,
            per_page=per_page
        )

    async def upload_announcement_image(self, user: User, announcement_id: int, file: UploadFile) -> AnnouncementResponse:
        """Загрузить изображение для объявления"""
        # Проверяем права доступа
        announcement = await self.announcement_repository.get_by_id(announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found"
            )
        
        # Получаем компанию пользователя через существующую сессию
        from app.api.company.repositories.company_repository import CompanyRepository
        
        # Используем ту же сессию, что и в announcement_repository
        company_repository = CompanyRepository(session=self.announcement_repository.session)
        company = await company_repository.get_by_user_id(user.id)
        
        if not company or announcement.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this announcement"
            )
        
        # Проверяем тип файла
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Создаем директорию если не существует
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Генерируем уникальное имя файла
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(self.upload_dir, filename)
        
        # Сохраняем файл
        try:
            async with aiofiles.open(filepath, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Добавляем изображение к объявлению
        new_image_path = f"/uploads/announcement_images/{filename}"
        current_images = announcement.images or []
        current_images.append(new_image_path)
        
        # Обновляем объявление
        update_data = AnnouncementUpdate(images=current_images)
        updated_announcement = await self.announcement_repository.update(announcement_id, update_data)
        
        return AnnouncementResponse.model_validate(updated_announcement)

    async def toggle_publish_status(self, user: User, announcement_id: int) -> AnnouncementResponse:
        """Опубликовать или снять с публикации объявление"""
        # Проверяем, что объявление принадлежит компании пользователя
        announcement = await self.announcement_repository.get_by_id(announcement_id)
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found"
            )
        
        # Получаем компанию пользователя через существующую сессию
        from app.api.company.repositories.company_repository import CompanyRepository
        
        # Используем ту же сессию, что и в announcement_repository
        company_repository = CompanyRepository(session=self.announcement_repository.session)
        company = await company_repository.get_by_user_id(user.id)
        
        if not company or announcement.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this announcement"
            )
        
        # Переключаем статус публикации
        new_published_status = not announcement.published
        update_data = AnnouncementUpdate(published=new_published_status)
        
        updated_announcement = await self.announcement_repository.update(announcement_id, update_data)
        if not updated_announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found after update"
            )
        
        return AnnouncementResponse.model_validate(updated_announcement) 