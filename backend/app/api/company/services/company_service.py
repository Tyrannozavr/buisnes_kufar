from typing import Optional
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.company.repositories.company_repository import CompanyRepository
from app.api.company.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.api.authentication.models import User
import aiofiles
import os
from datetime import datetime
import uuid

class CompanyService:
    def __init__(self, company_repository: CompanyRepository, db: AsyncSession):
        self.company_repository = company_repository
        self.db = db
        self.upload_dir = "uploads/company_logos"

    async def get_company_by_user(self, user: User) -> Optional[CompanyResponse]:
        company = await self.company_repository.get_by_user_id(user.id)
        if not company:
            return None
        return CompanyResponse.model_validate(company)

    async def update_company(self, user: User, company_data: CompanyUpdate) -> CompanyResponse:
        company = await self.company_repository.get_by_user_id(user.id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Verify user owns the company
        if company.user_id != user.id:
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
        
        return CompanyResponse.model_validate(updated_company)

    async def upload_logo(self, user: User, file: UploadFile) -> CompanyResponse:
        company = await self.company_repository.get_by_user_id(user.id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Verify user owns the company
        if company.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this company"
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
        
        return CompanyResponse.model_validate(updated_company)

    async def get_or_create_company_by_user(self, user: User) -> CompanyResponse:
        company = await self.company_repository.get_by_user_id(user.id)
        if not company:
            # Create an empty company record
            empty_company_data = CompanyCreate(name="", description="")
            company = await self.company_repository.create(empty_company_data, user.id)
        return CompanyResponse.model_validate(company)