import os
import uuid

import aiofiles
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.models import User
from app.api.authentication.repositories.user_repository import UserRepository
from app.api.company.repositories.company_repository import CompanyRepository
from app.api.company.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyProfileResponse, \
    CompanyCreateInactive


class CompanyService:
    def __init__(self, company_repository: CompanyRepository, db: AsyncSession):
        self.company_repository = company_repository
        self.user_repository = UserRepository(db)
        self.db = db
        self.upload_dir = "uploads/company_logos"

    async def get_company_by_user_id(self, user_id: int) -> CompanyProfileResponse:
        """Get company profile data for user. If company doesn't exist, returns user data with default values."""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user or not user.company_id:
            return CompanyProfileResponse.create_default(user)

        company = await self.company_repository.get_by_id(user.company_id)
        if not company:
            return CompanyProfileResponse.create_default(user)

        # Return combined user and company data
        return CompanyProfileResponse.create_with_company(company, user)

    async def create_company(self, user: User, company_data: CompanyCreate) -> CompanyResponse:
        company = await self.company_repository.create(company_data)
        
        # Обновляем пользователя - устанавливаем company_id и роль владельца
        from app.api.authentication.models.user import UserRole
        from app.api.authentication.permissions import PermissionManager
        
        # Устанавливаем права владельца
        owner_permissions = PermissionManager.set_permissions_for_role(UserRole.OWNER)
        
        await self.user_repository.update_user_role(user.id, UserRole.OWNER)
        await self.user_repository.update_user_permissions(user.id, owner_permissions)
        
        # Обновляем company_id у пользователя
        from sqlalchemy import update
        await self.db.execute(
            update(User)
            .where(User.id == user.id)
            .values(company_id=company.id)
        )
        await self.db.commit()
        
        return CompanyResponse.model_validate(company.__dict__)

    async def create_inactive_company(self, user: User) -> CompanyResponse:
        """Создает неактивную компанию при регистрации пользователя"""
        # Создаем данные для неактивной компании
        company_data = CompanyCreateInactive(
            full_name=f"ООО '{user.first_name or 'Компания'}'",
            inn=user.inn,
            registration_date=user.created_at,
            phone=user.phone,
            email=user.email
        )

        company = await self.company_repository.create_inactive(company_data, user.id)
        return CompanyResponse.model_validate(company.__dict__)

    async def update_company(self, user: User, company_data: CompanyUpdate) -> CompanyResponse:
        if not user.company_id:
            # Если у пользователя нет компании, создаем новую
            company_data_create = CompanyCreate(**company_data.model_dump())
            return await self.create_company(user, company_data_create)

        company = await self.company_repository.get_by_id(user.company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        # Проверяем права доступа
        from app.api.authentication.permissions import PermissionManager, Permission
        if not PermissionManager.has_permission(user.permissions or "", Permission.COMPANY_MANAGEMENT):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this company"
            )

        updated_company = await self.company_repository.update(company.id, company_data)
        if not updated_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found after update"
            )

        # Проверяем, можно ли активировать компанию (все обязательные поля заполнены)
        if not company.is_active and self._can_activate_company(updated_company):
            updated_company = await self.company_repository.activate_company(company.id)
        print(updated_company.__dict__)
        return CompanyResponse.model_validate(updated_company.__dict__)

    def _can_activate_company(self, company) -> bool:
        """Проверяет, можно ли активировать компанию (все обязательные поля заполнены)"""
        required_fields = [
            company.name, company.full_name, company.inn, company.ogrn,
            company.kpp, company.registration_date, company.legal_address,
            company.phone, company.email, company.country, company.federal_district,
            company.region, company.city, company.type, company.trade_activity,
            company.business_type, company.activity_type
        ]

        # Проверяем, что все обязательные поля заполнены и не являются значениями по умолчанию
        default_values = {
            'name': 'Новая компания',
            'ogrn': '000000000000000',
            'kpp': '000000000',
            'legal_address': 'Адрес не указан',
            'activity_type': 'Деятельность не указана'
        }

        for field_name, field_value in zip([
            'name', 'full_name', 'inn', 'ogrn', 'kpp', 'registration_date',
            'legal_address', 'phone', 'email', 'country', 'federal_district',
            'region', 'city', 'type', 'trade_activity', 'business_type', 'activity_type'
        ], required_fields):
            if not field_value:
                return False
            if field_name in default_values and str(field_value) == default_values[field_name]:
                return False

        return True

    async def upload_logo(self, user: User, file: UploadFile) -> CompanyResponse:
        # Получаем компанию пользователя через company_id
        if not user.company_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        company = await self.company_repository.get_by_id(user.company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )

        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)

        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(self.upload_dir, filename)

        # Save file
        try:
            async with aiofiles.open(filepath, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )

        # Update company logo URL
        logo_url = f"/uploads/company_logos/{filename}"
        updated_company = await self.company_repository.update_logo(company.id, logo_url)
        if not updated_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found after logo update"
            )

        return CompanyResponse.model_validate(updated_company.__dict__)

    async def get_full_company(self, user_id: int) -> CompanyResponse:
        """Get full company data for user."""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user or not user.company_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        company = await self.company_repository.get_by_id(user.company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return CompanyResponse.model_validate(company.__dict__)
