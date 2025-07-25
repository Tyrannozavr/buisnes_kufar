import random
import time
from datetime import datetime, timezone
from typing import Optional

from pydantic import HttpUrl
from slugify import slugify
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.company.models.company import Company
from app.api.company.schemas.company import CompanyCreate, CompanyUpdate, CompanyCreateInactive


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
        data = company_data.model_dump()
        # Ensure all datetime fields are naive (no tzinfo)
        for field in ["registration_date", "created_at", "updated_at"]:
            if field in data and isinstance(data[field], datetime) and data[field].tzinfo is not None:
                data[field] = data[field].astimezone(timezone.utc).replace(tzinfo=None)
        company = Company(
            **data,
            slug=await self.create_company_slug(company_data.name),
            user_id=user_id,
            is_active=True  # Активная компания при создании через форму
        )
        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)
        return company

    async def create_inactive(self, company_data: CompanyCreateInactive, user_id: int) -> Company:
        """Создает неактивную компанию при регистрации пользователя"""
        data = company_data.model_dump()
        # Ensure all datetime fields are naive (no tzinfo)
        for field in ["registration_date", "created_at", "updated_at"]:
            if field in data and isinstance(data[field], datetime) and data[field].tzinfo is not None:
                data[field] = data[field].astimezone(timezone.utc).replace(tzinfo=None)
        company = Company(
            **data,
            slug=await self.create_company_slug(company_data.name),
            user_id=user_id,
            is_active=False  # Неактивная компания при регистрации
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

        # Convert ogrn and kpp to strings if present
        for field in ["ogrn", "kpp"]:
            if field in update_data and update_data[field] is not None:
                update_data[field] = str(update_data[field])

        # Check if company should be activated
        company = await self.get_by_id(company_id)
        default_name = "Новая компания"
        default_inn = "0000000000"
        if (
                ("name" in update_data and update_data["name"] != default_name) or (
                company and company.name != default_name)
        ) and (
                ("inn" in update_data and update_data["inn"] != default_inn) or (company and company.inn != default_inn)
        ):
            update_data["is_active"] = True

        # If name is being updated and is different, update slug as well
        if "name" in update_data and company and update_data["name"] != company.name:
            update_data["slug"] = await self.create_company_slug(update_data["name"])

        # Update company
        if update_data:
            await self.session.execute(
                update(Company)
                .where(Company.id == company_id)
                .values(**update_data)
            )

        await self.session.commit()
        return await self.get_by_id(company_id)

    async def activate_company(self, company_id: int) -> Optional[Company]:
        """Активирует компанию после заполнения всех обязательных полей"""
        await self.session.execute(
            update(Company)
            .where(Company.id == company_id)
            .values(is_active=True)
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

    async def create_by_default(self, user) -> Company:
        """
        Создает компанию с данными по умолчанию на основе данных пользователя.
        ИНН берется из данных пользователя, остальные поля заполняются значениями по умолчанию.
        Также создает запись в CompanyOfficial для текущего пользователя.
        """
        from app.api.company.models.official import CompanyOfficial
        from app.api.company.models.company import TradeActivity, BusinessType

        # Формируем полное имя пользователя
        full_name_parts = []
        if user.first_name:
            full_name_parts.append(user.first_name)
        if user.last_name:
            full_name_parts.append(user.last_name)
        if user.patronymic:
            full_name_parts.append(user.patronymic)

        user_full_name = " ".join(full_name_parts) if full_name_parts else "Не указано"

        # Создаем компанию с данными по умолчанию
        company = Company(
            name="Новая компания",
            slug=await self.create_company_slug("Новая компания"),
            type="ООО",
            trade_activity=TradeActivity.BOTH,
            business_type=BusinessType.BOTH,
            activity_type="Деятельность не указана",
            description=None,

            # Location - значения по умолчанию
            country="Россия",
            federal_district="Центральный федеральный округ",
            region="Москва",
            city="Москва",

            # Legal information
            full_name="Полное наименование не указано",
            inn=user.inn,  # ИНН из данных пользователя
            ogrn=None,  # Временное значение
            kpp="000000000",  # Временное значение
            registration_date=datetime.now(),
            legal_address="Адрес не указан",
            production_address=None,

            # Contact information - из данных пользователя
            phone=user.phone,
            email=user.email,
            website=None,

            # Статистика
            total_views=0,
            monthly_views=0,
            total_purchases=0,

            # Связи и статус
            user_id=user.id,
            is_active=False  # Компания неактивна по умолчанию
        )

        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)

        # Создаем запись в CompanyOfficial для текущего пользователя
        official = CompanyOfficial(
            position=user.position or "Руководитель",
            full_name=user_full_name,
            company_id=company.id
        )

        self.session.add(official)
        await self.session.commit()

        return company
