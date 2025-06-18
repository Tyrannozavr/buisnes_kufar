from typing import Optional
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from api.authentication.repositories.user_repository import UserRepository
from app.api.company.repositories.company_repository import CompanyRepository
from app.api.company.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyProfileResponse
from app.api.authentication.models import User
import aiofiles
import os
from datetime import datetime
import uuid

class CompanyService:
    def __init__(self, company_repository: CompanyRepository, db: AsyncSession):
        self.company_repository = company_repository
        self.user_repository = UserRepository(db)
        self.db = db
        self.upload_dir = "uploads/company_logos"

    async def get_company_by_user(self, user_id: int) -> CompanyProfileResponse:
        """Get company profile data for user. If company doesn't exist, returns user data with default values."""
        company = await self.company_repository.get_by_user_id(user_id)
        user = await self.user_repository.get_user_by_id(user_id)

        # Always return a response with user data
        if not company:
            return CompanyProfileResponse.create_default(user)
            
        # Return combined user and company data
        return CompanyProfileResponse.create_with_company(company, user)

    async def create_company(self, user: User, company_data: CompanyCreate) -> CompanyResponse:
        company = await self.company_repository.create(company_data, user.id)
        return CompanyResponse.model_validate(company.__dict__)


    async def update_company(self, user: User, company_data: CompanyUpdate) -> CompanyResponse:
        company = await self.company_repository.get_by_user_id(user.id)
        if not company:
            company_data = CompanyCreate(**company_data.model_dump())  # Convert to CompanyCreate if not provided
            return await self.create_company(user, company_data)

        
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
        
        return CompanyResponse.model_validate(updated_company.__dict__)

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
        
        return CompanyResponse.model_validate(updated_company.__dict__)


    async def get_full_company(self, user_id: int) -> CompanyResponse:
        """Get full company data for user."""
        company = await self.company_repository.get_by_user_id(user_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return CompanyResponse.model_validate(company.__dict__)