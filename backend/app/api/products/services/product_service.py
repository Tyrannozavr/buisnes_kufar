from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid
import aiofiles
from fastapi import HTTPException, status, UploadFile

from app.api.company.repositories.company_repository import CompanyRepository
from app.api.products.repositories.my_products_repository import MyProductsRepository
from app.api.products.repositories.company_products_repository import CompanyProductsRepository
from app.api.products.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse, ProductCreateWithFiles, ProductListPublicResponse
from app.api.products.models.product import ProductType


class ProductService:
    def __init__(self, my_products_repo: MyProductsRepository, company_products_repo: CompanyProductsRepository, session: AsyncSession):
        self.my_products_repo = my_products_repo
        self.company_products_repo = company_products_repo
        self.company_repo = CompanyRepository(session)
        self.session = session
        self.upload_dir = "uploads/product_images"

    # Методы для работы с собственными продуктами (MyProductsRepository)
    
    async def create_my_product(self, product_data: ProductCreate, user_id: int) -> Optional[ProductResponse]:
        """Создать новый продукт для компании пользователя"""
        product = await self.my_products_repo.create(product_data, user_id)
        if product:
            return ProductResponse.model_validate(product)
        return None

    async def create_my_product_with_images(self, product_data: ProductCreateWithFiles, files: List[UploadFile], user_id: int) -> Optional[ProductResponse]:
        """Создать новый продукт с изображениями в одном запросе"""
        # Сначала создаем продукт
        product = await self.my_products_repo.create(product_data, user_id)
        if not product:
            return None
        
        # Если есть файлы, загружаем их
        if files:
            uploaded_images = []
            
            # Создаем директорию для загрузки, если она не существует
            os.makedirs(self.upload_dir, exist_ok=True)
            
            for file in files:
                # Проверяем тип файла
                if not file.content_type.startswith('image/'):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File {file.filename} must be an image"
                    )
                
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
                        detail=f"Failed to save file {file.filename}: {str(e)}"
                    )
                
                # Добавляем путь к изображению в список
                image_url = f"/uploads/product_images/{filename}"
                uploaded_images.append(image_url)
            
            # Обновляем продукт с изображениями
            updated_product = await self.my_products_repo.update_images(product.id, uploaded_images, user_id)
            if updated_product:
                return ProductResponse.model_validate(updated_product)
        
        return ProductResponse.model_validate(product)

    async def get_my_product_by_id(self, product_id: int, user_id: int) -> Optional[ProductResponse]:
        """Получить продукт по ID, только если он принадлежит компании пользователя"""
        product = await self.my_products_repo.get_by_id(product_id, user_id)
        if product:
            return ProductResponse.model_validate(product)
        return None

    async def get_my_product_by_slug(self, slug: str, user_id: int) -> Optional[ProductResponse]:
        """Получить продукт по slug, только если он принадлежит компании пользователя"""
        product = await self.my_products_repo.get_by_slug(slug, user_id)
        if product:
            return ProductResponse.model_validate(product)
        return None

    async def get_my_products(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        include_hidden: bool = True,
        include_deleted: bool = False
    ) -> ProductListResponse:
        """Получить все продукты компании пользователя с пагинацией"""
        products, total = await self.my_products_repo.get_all_products(
            user_id, skip, limit, include_hidden, include_deleted
        )
        
        product_responses = [ProductResponse.model_validate(product) for product in products]
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    async def get_my_products_by_type(
        self, 
        user_id: int, 
        product_type: ProductType,
        skip: int = 0, 
        limit: int = 100
    ) -> ProductListResponse:
        """Получить продукты определенного типа компании пользователя"""
        products, total = await self.my_products_repo.get_products_by_type(
            user_id, product_type, skip, limit
        )
        
        product_responses = [ProductResponse.model_validate(product) for product in products]
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    async def update_my_product(self, product_id: int, product_data: ProductUpdate, user_id: int) -> Optional[ProductResponse]:
        """Обновить продукт, только если он принадлежит компании пользователя"""
        product = await self.my_products_repo.update(product_id, product_data, user_id)
        if product:
            return ProductResponse.model_validate(product)
        return None

    async def partial_update_my_product(self, product_id: int, product_data: ProductUpdate, user_id: int) -> Optional[ProductResponse]:
        """Частично обновить продукт, только если он принадлежит компании пользователя"""
        product = await self.my_products_repo.partial_update(product_id, product_data, user_id)
        if product:
            return ProductResponse.model_validate(product)
        return None

    async def delete_my_product(self, product_id: int, user_id: int) -> bool:
        """Удалить продукт (мягкое удаление), только если он принадлежит компании пользователя"""
        return await self.my_products_repo.delete(product_id, user_id)

    async def hard_delete_my_product(self, product_id: int, user_id: int) -> bool:
        """Полное удаление продукта, только если он принадлежит компании пользователя"""
        return await self.my_products_repo.hard_delete(product_id, user_id)

    async def toggle_my_product_hidden(self, product_id: int, user_id: int) -> Optional[ProductResponse]:
        """Переключить видимость продукта"""
        product = await self.my_products_repo.toggle_hidden(product_id, user_id)
        if product:
            return ProductResponse.model_validate(product)
        return None

    async def update_my_product_images(self, product_id: int, images: List[str], user_id: int) -> Optional[ProductResponse]:
        """Обновить изображения продукта"""
        product = await self.my_products_repo.update_images(product_id, images, user_id)
        if product:
            return ProductResponse.model_validate(product)
        return None

    async def upload_product_images(self, product_id: int, files: List[UploadFile], user_id: int) -> Optional[ProductResponse]:
        """Загрузить изображения для продукта"""
        # Получаем продукт и проверяем права доступа
        product = await self.my_products_repo.get_by_id(product_id, user_id)
        if not product:
            return None
        
        # Создаем директорию для загрузки, если она не существует
        os.makedirs(self.upload_dir, exist_ok=True)
        
        uploaded_images = []
        
        for file in files:
            # Проверяем тип файла
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} must be an image"
                )
            
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
                    detail=f"Failed to save file {file.filename}: {str(e)}"
                )
            
            # Добавляем путь к изображению в список
            image_url = f"/uploads/product_images/{filename}"
            uploaded_images.append(image_url)
        
        # Обновляем изображения продукта
        current_images = product.images or []
        updated_images = current_images + uploaded_images
        
        updated_product = await self.my_products_repo.update_images(product_id, updated_images, user_id)
        if updated_product:
            return ProductResponse.model_validate(updated_product)
        return None

    async def delete_product_image(self, product_id: int, image_index: int, user_id: int) -> Optional[ProductResponse]:
        """Удалить изображение продукта по индексу"""
        # Получаем продукт и проверяем права доступа
        product = await self.my_products_repo.get_by_id(product_id, user_id)
        if not product:
            return None
        
        current_images = product.images or []
        
        # Проверяем, что индекс существует
        if image_index < 0 or image_index >= len(current_images):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image index"
            )
        
        # Удаляем файл с диска
        image_path = current_images[image_index]
        if image_path.startswith('/uploads/'):
            file_path = image_path[1:]  # Убираем начальный слеш
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                # Логируем ошибку, но не прерываем выполнение
                print(f"Failed to delete file {file_path}: {str(e)}")
        
        # Удаляем изображение из списка
        updated_images = current_images[:image_index] + current_images[image_index + 1:]
        
        # Обновляем продукт
        updated_product = await self.my_products_repo.update_images(product_id, updated_images, user_id)
        if updated_product:
            return ProductResponse.model_validate(updated_product)
        return None

    # Методы для работы с продуктами компаний (CompanyProductsRepository)

    async def get_product_by_id(self, product_id: int) -> Optional[ProductResponse]:
        """Получить продукт по ID (только активные и не скрытые)"""
        product = await self.company_products_repo.get_by_id(product_id)
        if product:
            return ProductResponse.model_validate(product)
        return None

    async def get_product_by_slug(self, slug: str) -> Optional[ProductResponse]:
        """Получить продукт по slug и company_id (только активные и не скрытые)"""
        product = await self.company_products_repo.get_by_slug(slug)
        if product:
            return ProductResponse.model_validate(product)
        return None

    async def get_products_by_company_slug(
        self, 
        company_slug: str,
        skip: int = 0, 
        limit: int = 100,
        include_hidden: bool = False
    ) -> ProductListPublicResponse:
        """Получить все продукты компании с пагинацией"""
        products, total = await self.company_products_repo.get_by_company_slug(
            company_slug, skip, limit, include_hidden
        )
        
        from app.api.products.schemas.product import ProductPublicItemResponse
        product_responses = [ProductPublicItemResponse.model_validate(product) for product in products]
        
        return ProductListPublicResponse(
            products=product_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    async def get_all_products(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_hidden: bool = False
    ) -> ProductListResponse:
        """Получить все продукты всех компаний с пагинацией"""
        products, total = await self.company_products_repo.get_all_products(
            skip, limit, include_hidden
        )
        
        product_responses = [ProductResponse.model_validate(product) for product in products]
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    async def get_all_services(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_hidden: bool = False
    ) -> ProductListResponse:
        """Получить все услуги всех компаний с пагинацией"""
        services, total = await self.company_products_repo.get_all_services(
            skip, limit, include_hidden
        )
        
        service_responses = [ProductResponse.model_validate(service) for service in services]
        
        return ProductListResponse(
            products=service_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    async def get_all_goods(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_hidden: bool = False
    ) -> ProductListResponse:
        """Получить все товары всех компаний с пагинацией"""
        goods, total = await self.company_products_repo.get_all_goods(
            skip, limit, include_hidden
        )
        
        goods_responses = [ProductResponse.model_validate(good) for good in goods]
        
        return ProductListResponse(
            products=goods_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    async def get_services_by_company_id(
        self, 
        company_id: int, 
        skip: int = 0, 
        limit: int = 100,
        include_hidden: bool = False
    ) -> ProductListResponse:
        """Получить все услуги конкретной компании с пагинацией"""
        services, total = await self.company_products_repo.get_services_by_company_id(
            company_id, skip, limit, include_hidden
        )
        
        service_responses = [ProductResponse.model_validate(service) for service in services]
        
        return ProductListResponse(
            products=service_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    async def get_goods_by_company_id(
        self, 
        company_id: int, 
        skip: int = 0, 
        limit: int = 100,
        include_hidden: bool = False
    ) -> ProductListResponse:
        """Получить все товары конкретной компании с пагинацией"""
        goods, total = await self.company_products_repo.get_goods_by_company_id(
            company_id, skip, limit, include_hidden
        )
        
        goods_responses = [ProductResponse.model_validate(good) for good in goods]
        
        return ProductListResponse(
            products=goods_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    async def search_products(
        self, 
        search_term: str,
        skip: int = 0, 
        limit: int = 100,
        include_hidden: bool = False
    ) -> ProductListResponse:
        """Поиск продуктов по названию или описанию"""
        products, total = await self.company_products_repo.search_products(
            search_term, skip, limit, include_hidden
        )
        
        product_responses = [ProductResponse.model_validate(product) for product in products]
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    async def get_products_by_price_range(
        self, 
        min_price: float,
        max_price: float,
        skip: int = 0, 
        limit: int = 100,
        include_hidden: bool = False
    ) -> ProductListResponse:
        """Получить продукты в диапазоне цен"""
        products, total = await self.company_products_repo.get_products_by_price_range(
            min_price, max_price, skip, limit, include_hidden
        )
        
        product_responses = [ProductResponse.model_validate(product) for product in products]
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    async def get_latest_products(
        self, 
        limit: int = 20,
        include_hidden: bool = False
    ) -> List[ProductResponse]:
        """Получить последние добавленные продукты"""
        products = await self.company_products_repo.get_latest_products(limit, include_hidden)
        return [ProductResponse.model_validate(product) for product in products]