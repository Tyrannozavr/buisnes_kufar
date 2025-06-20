import random
import time
from typing import Optional, List
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from slugify import slugify

from app.api.products.models.product import Product, ProductType
from app.api.company.models.company import Company
from app.api.products.schemas.product import ProductCreate, ProductUpdate


class MyProductsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_product_slug(self, name: str, company_id: int) -> str:
        base_slug = slugify(name)
        slug = base_slug
        attempt = 1

        while True:
            # Проверяем, существует ли уже продукт с таким slug в этой компании
            query = select(Product).where(
                and_(Product.slug == slug, Product.company_id == company_id)
            )
            result = await self.session.execute(query)
            existing_product = result.scalar_one_or_none()

            if not existing_product:
                return slug

            # Если slug уже существует, добавляем случайные цифры
            random_suffix = ''.join(str(random.randint(0, 9)) for _ in range(4))
            slug = f"{base_slug}-{random_suffix}"
            attempt += 1

            if attempt > 10:
                # Если после 10 попыток уникальный slug не найден, добавляем timestamp
                slug = f"{base_slug}-{int(time.time())}"
                return slug

    async def get_company_by_user_id(self, user_id: int) -> Optional[Company]:
        """Получить компанию по user_id для проверки прав доступа"""
        query = select(Company).where(Company.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, product_id: int, user_id: int) -> Optional[Product]:
        """Получить продукт по ID, только если он принадлежит компании пользователя"""
        # Сначала получаем компанию пользователя
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return None

        query = select(Product).where(
            and_(Product.id == product_id, Product.company_id == company.id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str, user_id: int) -> Optional[Product]:
        """Получить продукт по slug, только если он принадлежит компании пользователя"""
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return None

        query = select(Product).where(
            and_(Product.slug == slug, Product.company_id == company.id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_products(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        include_hidden: bool = True,
        include_deleted: bool = False
    ) -> tuple[List[Product], int]:
        """Получить все продукты компании пользователя с пагинацией"""
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return [], 0

        # Базовый запрос
        base_query = select(Product).where(Product.company_id == company.id)

        # Добавляем фильтры
        if not include_hidden:
            base_query = base_query.where(Product.is_hidden == False)
        
        if not include_deleted:
            base_query = base_query.where(Product.is_deleted == False)

        # Получаем общее количество
        count_query = select(Product).where(base_query.whereclause)
        count_result = await self.session.execute(count_query)
        total = len(count_result.scalars().all())

        # Получаем продукты с пагинацией
        query = base_query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        products = result.scalars().all()

        return list(products), total

    async def get_products_by_type(
        self, 
        user_id: int, 
        product_type: ProductType,
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[List[Product], int]:
        """Получить продукты определенного типа компании пользователя"""
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return [], 0

        base_query = select(Product).where(
            and_(
                Product.company_id == company.id,
                Product.type == product_type,
                Product.is_deleted == False
            )
        )

        # Получаем общее количество
        count_result = await self.session.execute(base_query)
        total = len(count_result.scalars().all())

        # Получаем продукты с пагинацией
        query = base_query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        products = result.scalars().all()

        return list(products), total

    async def create(self, product_data: ProductCreate, user_id: int) -> Optional[Product]:
        """Создать новый продукт для компании пользователя"""
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return None

        slug = await self.create_product_slug(product_data.name, company.id)
        
        product = Product(
            **product_data.model_dump(),
            slug=slug,
            company_id=company.id
        )
        
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, product_id: int, product_data: ProductUpdate, user_id: int) -> Optional[Product]:
        """Обновить продукт, только если он принадлежит компании пользователя"""
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return None

        # Проверяем, что продукт принадлежит компании
        existing_product = await self.get_by_id(product_id, user_id)
        if not existing_product:
            return None

        # Подготавливаем данные для обновления
        update_data = product_data.model_dump(exclude_unset=False)
        
        # Если изменяется название, генерируем новый slug
        if 'name' in update_data:
            update_data['slug'] = await self.create_product_slug(update_data['name'], company.id)

        # Обновляем продукт
        await self.session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(**update_data)
        )
        
        await self.session.commit()
        return await self.get_by_id(product_id, user_id)

    async def partial_update(self, product_id: int, product_data: ProductUpdate, user_id: int) -> Optional[Product]:
        """Частично обновить продукт, только если он принадлежит компании пользователя"""
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return None

        # Проверяем, что продукт принадлежит компании
        existing_product = await self.get_by_id(product_id, user_id)
        if not existing_product:
            return None

        # Подготавливаем данные для обновления
        update_data = product_data.model_dump(exclude_unset=True)
        
        # Если изменяется название, генерируем новый slug
        if 'name' in update_data:
            update_data['slug'] = await self.create_product_slug(update_data['name'], company.id)

        # Обновляем продукт
        await self.session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(**update_data)
        )
        
        await self.session.commit()
        return await self.get_by_id(product_id, user_id)

    async def delete(self, product_id: int, user_id: int) -> bool:
        """Удалить продукт (мягкое удаление), только если он принадлежит компании пользователя"""
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return False

        # Проверяем, что продукт принадлежит компании
        existing_product = await self.get_by_id(product_id, user_id)
        if not existing_product:
            return False

        # Мягкое удаление
        result = await self.session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(is_deleted=True)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def hard_delete(self, product_id: int, user_id: int) -> bool:
        """Полное удаление продукта, только если он принадлежит компании пользователя"""
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return False

        # Проверяем, что продукт принадлежит компании
        existing_product = await self.get_by_id(product_id, user_id)
        if not existing_product:
            return False

        result = await self.session.execute(
            delete(Product).where(Product.id == product_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def toggle_hidden(self, product_id: int, user_id: int) -> Optional[Product]:
        """Переключить видимость продукта"""
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return None

        existing_product = await self.get_by_id(product_id, user_id)
        if not existing_product:
            return None

        new_hidden_state = not existing_product.is_hidden
        
        await self.session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(is_hidden=new_hidden_state)
        )
        await self.session.commit()
        return await self.get_by_id(product_id, user_id)

    async def update_images(self, product_id: int, images: List[str], user_id: int) -> Optional[Product]:
        """Обновить изображения продукта"""
        company = await self.get_company_by_user_id(user_id)
        if not company:
            return None

        existing_product = await self.get_by_id(product_id, user_id)
        if not existing_product:
            return None

        await self.session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(images=images)
        )
        await self.session.commit()
        return await self.get_by_id(product_id, user_id)