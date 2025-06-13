from typing import Optional, List

from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.api.company.models.company import Company
from app.api.company.models.official import CompanyOfficial
from app.api.company.schemas.company import CompanyCreate, CompanyUpdate, CompanyOfficialUpdate
from slugify import slugify
import random
import time


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_company_slug(self, name: str) -> str:
        base_slug = slugify(name)
        slug = base_slug
        attempt = 1

        while True:
            # Проверяем, существует ли уже компания с таким slug
            query = select(Company).where(Company.slug == slug)
            result = await self.session.execute(query)
            existing_company = result.scalar_one_or_none()

            if not existing_company:
                return slug

            # Если slug уже существует, добавляем случайные цифры
            random_suffix = ''.join(str(random.randint(0, 9)) for _ in range(4))
            slug = f"{base_slug}-{random_suffix}"
            attempt += 1

            if attempt > 10:
                # Если после 10 попыток уникальный slug не найден, добавляем timestamp
                slug = f"{base_slug}-{int(time.time())}"
                return slug

    async def get_by_id(self, company_id: int) -> Optional[Company]:
        query = select(Company).options(
            selectinload(Company.officials)
        ).where(Company.id == company_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Optional[Company]:
        query = select(Company).options(
            selectinload(Company.officials)
        ).where(Company.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Company]:
        query = select(Company).options(
            selectinload(Company.officials)
        ).where(Company.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, company_data: CompanyCreate, user_id: int) -> Company:
        company = Company(
            **company_data.model_dump(),
            slug=await self.create_company_slug(company_data.name),
            user_id=user_id
        )
        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)
        return company

    async def update(self, company_id: int, company_data: CompanyUpdate) -> Optional[Company]:
        # Update company fields
        update_data = company_data.model_dump(exclude_unset=True)

        # Convert HttpUrl to string if present
        if 'website' in update_data and isinstance(update_data['website'], HttpUrl):
            update_data['website'] = str(update_data['website'])

        if 'officials' in update_data:
            officials_data = update_data.pop('officials')
            
            # Delete existing officials
            await self.session.execute(
                delete(CompanyOfficial).where(CompanyOfficial.company_id == company_id)
            )
            
            # Create new officials
            if officials_data:
                officials = [
                    CompanyOfficial(**official.model_dump(), company_id=company_id)
                    for official in officials_data
                ]
                self.session.add_all(officials)
        
        # Update company
        if update_data:
            await self.session.execute(
                update(Company)
                .where(Company.id == company_id)
                .values(**update_data)
            )
        
        await self.session.commit()
        return await self.get_by_id(company_id)

    async def delete(self, company_id: int) -> bool:
        result = await self.session.execute(
            delete(Company).where(Company.id == company_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def update_logo(self, company_id: int, logo_url: str) -> Optional[Company]:
        await self.session.execute(
            update(Company)
            .where(Company.id == company_id)
            .values(logo=logo_url)
        )
        await self.session.commit()
        return await self.get_by_id(company_id)