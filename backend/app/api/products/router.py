import json
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Query, Depends, File, UploadFile, Form

from api.dependencies import async_db_dep
from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.company.schemas.filters import ProductFilterRequest, ServiceFilterRequest
from app.api.products.dependencies import product_service_dep, get_filter_service, get_search_service
from app.api.products.models.product import ProductType
from app.api.products.schemas.filters import ProductFiltersResponse, ServiceFiltersResponse
from app.api.products.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductCreateWithFiles, ProductListPublicResponse
)
from app.api.products.services.cache_service import product_location_cache
from app.api.products.services.filter_service import FilterService
from app.api.products.services.search_service import ProductSearchService

owner_router = APIRouter(tags=["products"])


# Эндпоинты для работы с собственными продуктами (требуют аутентификации)

@owner_router.post("", response_model=ProductResponse)
async def create_my_product(
        product_data: ProductCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep
):
    """Создать новый продукт для компании пользователя"""
    product = await product_service.create_my_product(product_data, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    return product


@owner_router.post("/with-images", response_model=ProductResponse)
async def create_my_product_with_images(
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep,
        name: str = Form(...),
        description: Optional[str] = Form(None),
        article: str = Form(...),
        type: str = Form(...),
        price: float = Form(...),
        unit_of_measurement: Optional[str] = Form(None),
        is_hidden: bool = Form(False),
        characteristics: str = Form("[]"),  # JSON string
        files: list[UploadFile] = File([])
):
    """Создать новый продукт с изображениями в одном запросе"""
    try:
        # Парсим характеристики из JSON строки
        characteristics_list = json.loads(characteristics) if characteristics else []

        # Создаем объект продукта
        product_data = ProductCreateWithFiles(
            name=name,
            description=description,
            article=article,
            type=ProductType(type),
            price=price,
            unit_of_measurement=unit_of_measurement,
            is_hidden=is_hidden,
            characteristics=characteristics_list
        )

        # Создаем продукт с изображениями
        product = await product_service.create_my_product_with_images(
            product_data, files, current_user.id
        )
        if not product:
            raise HTTPException(status_code=404, detail="Company not found for this user")
        return product
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid characteristics JSON")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@owner_router.post("/{product_id}/images", response_model=ProductResponse)
async def upload_product_images(
        product_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep,
        files: list[UploadFile] = File(...)
):
    """Загрузить изображения для продукта"""
    product = await product_service.upload_product_images(product_id, files, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@owner_router.delete("/{product_id}/images/{image_index}", response_model=ProductResponse)
async def delete_product_image(
        product_id: int,
        image_index: int,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep
):
    """Удалить изображение продукта по индексу"""
    product = await product_service.delete_product_image(product_id, image_index, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@owner_router.get("", response_model=ProductListResponse)
async def get_my_products(
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        include_hidden: bool = Query(True),
        include_deleted: bool = Query(False)
):
    """Получить все продукты компании пользователя"""
    return await product_service.get_my_products(
        current_user.id, skip, limit, include_hidden, include_deleted
    )


@owner_router.get("/{product_id}", response_model=ProductResponse)
async def get_my_product(
        product_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep
):
    """Получить продукт по ID, только если он принадлежит компании пользователя"""
    product = await product_service.get_my_product_by_id(product_id, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@owner_router.get("/slug/{slug}", response_model=ProductResponse)
async def get_my_product_by_slug(
        slug: str,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep
):
    """Получить продукт по slug, только если он принадлежит компании пользователя"""
    product = await product_service.get_my_product_by_slug(slug, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@owner_router.get("/type/{product_type}", response_model=ProductListResponse)
async def get_my_products_by_type(
        product_type: ProductType,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    """Получить продукты определенного типа компании пользователя"""
    return await product_service.get_my_products_by_type(
        current_user.id, product_type, skip, limit
    )


@owner_router.put("/{product_id}", response_model=ProductResponse)
async def update_my_product(
        product_id: int,
        product_data: ProductUpdate,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep
):
    """Обновить продукт, только если он принадлежит компании пользователя"""
    product = await product_service.update_my_product(product_id, product_data, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@owner_router.patch("/{product_id}", response_model=ProductResponse)
async def update_my_product(
        product_id: int,
        product_data: ProductUpdate,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep
):
    """Обновить продукт, только если он принадлежит компании пользователя"""
    product = await product_service.partial_update_my_product(product_id, product_data, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@owner_router.delete("/{product_id}")
async def delete_my_product(
        product_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep
):
    """Удалить продукт (мягкое удаление), только если он принадлежит компании пользователя"""
    success = await product_service.delete_my_product(product_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@owner_router.delete("/{product_id}/hard")
async def hard_delete_my_product(
        product_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep
):
    """Полное удаление продукта, только если он принадлежит компании пользователя"""
    success = await product_service.hard_delete_my_product(product_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product permanently deleted"}


@owner_router.patch("/{product_id}/toggle-hidden", response_model=ProductResponse)
async def toggle_my_product_hidden(
        product_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        product_service: product_service_dep
):
    """Переключить видимость продукта"""
    product = await product_service.toggle_my_product_hidden(product_id, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Эндпоинты для работы с продуктами компаний (публичные)
public_router = APIRouter()


# Новые endpoints для фильтров (должны быть выше других endpoints)
@public_router.get("/filters", response_model=ProductFiltersResponse)
async def get_product_filters(
        filter_service: Annotated[FilterService, Depends(get_filter_service)]
):
    """Получить фильтры для товаров"""
    return await filter_service.get_product_filters()


@public_router.get("/services/filters", response_model=ServiceFiltersResponse)
async def get_service_filters(
        filter_service: Annotated[FilterService, Depends(get_filter_service)]
):
    """Получить фильтры для услуг"""
    return await filter_service.get_service_filters()


@public_router.get("/", response_model=ProductListResponse)
async def get_all_products(
        product_service: product_service_dep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        include_hidden: bool = Query(False)
):
    """Получить все продукты всех компаний"""
    return await product_service.get_all_products(skip, limit, include_hidden)


@public_router.get("/services", response_model=ProductListResponse)
async def get_all_services(
        product_service: product_service_dep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        include_hidden: bool = Query(False)
):
    """Получить все услуги всех компаний"""
    return await product_service.get_all_services(skip, limit, include_hidden)


@public_router.get("/goods", response_model=ProductListResponse)
async def get_all_goods(
        product_service: product_service_dep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        include_hidden: bool = Query(False)
):
    """Получить все товары всех компаний"""
    return await product_service.get_all_goods(skip, limit, include_hidden)


@public_router.get("/company/{company_slug}", response_model=ProductListPublicResponse)
async def get_products_by_company_id(
        company_slug: str,
        product_service: product_service_dep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        include_hidden: bool = Query(False)
):
    """Получить все продукты конкретной компании"""
    return await product_service.get_products_by_company_slug(
        company_slug, skip, limit, include_hidden
    )


@public_router.get("/company/{company_id}/services", response_model=ProductListPublicResponse)
async def get_services_by_company_id(
        company_id: int,
        product_service: product_service_dep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        include_hidden: bool = Query(False)
):
    """Получить все услуги конкретной компании"""
    return await product_service.get_services_by_company_id(
        company_id, skip, limit, include_hidden
    )


@public_router.get("/company/{company_id}/goods", response_model=ProductListPublicResponse)
async def get_goods_by_company_id(
        company_id: int,
        product_service: product_service_dep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        include_hidden: bool = Query(False)
):
    """Получить все товары конкретной компании"""
    return await product_service.get_goods_by_company_id(
        company_id, skip, limit, include_hidden
    )


@public_router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
        product_id: int,
        product_service: product_service_dep
):
    """Получить продукт по ID (только активные и не скрытые)"""
    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@public_router.get("/slug/{product_slug}", response_model=ProductResponse)
async def get_product_by_slug(
        product_slug: str,
        product_service: product_service_dep
):
    """Получить продукт по ID (только активные и не скрытые)"""
    product = await product_service.get_product_by_slug(product_slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@public_router.get("/search", response_model=ProductListResponse)
async def search_products(
        product_service: product_service_dep,
        q: str = Query(..., min_length=1, description="Search term"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        include_hidden: bool = Query(False)
):
    """Поиск продуктов по названию или описанию"""
    return await product_service.search_products(q, skip, limit, include_hidden)


@public_router.get("/price-range", response_model=ProductListResponse)
async def get_products_by_price_range(
        product_service: product_service_dep,
        min_price: float = Query(..., ge=0),
        max_price: float = Query(..., ge=0),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        include_hidden: bool = Query(False)
):
    """Получить продукты в диапазоне цен"""
    if min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")
    return await product_service.get_products_by_price_range(
        min_price, max_price, skip, limit, include_hidden
    )


@public_router.get("/latest", response_model=list[ProductResponse])
async def get_latest_products(
        product_service: product_service_dep,
        limit: int = Query(20, ge=1, le=100),
        include_hidden: bool = Query(False)
):
    """Получить последние добавленные продукты"""
    return await product_service.get_latest_products(limit, include_hidden)


# Новые endpoints для поиска с фильтрацией
@public_router.post("/search", response_model=ProductListResponse)
async def search_products_with_filters(
        filter_request: ProductFilterRequest,
        search_service: Annotated[ProductSearchService, Depends(get_search_service)]
):
    """Поиск товаров с фильтрацией"""
    return await search_service.search_products(filter_request)


@public_router.post("/services/search", response_model=ProductListResponse)
async def search_services_with_filters(
        filter_request: ServiceFilterRequest,
        search_service: Annotated[ProductSearchService, Depends(get_search_service)]
):
    """Поиск услуг с фильтрацией"""
    return await search_service.search_services(filter_request)


# Endpoints для управления кэшем
@public_router.post("/cache/refresh")
async def refresh_cache(
        db: async_db_dep
):
    """Обновить кэш фильтров"""
    await product_location_cache.refresh_cache(db)
    return {"message": "Cache refreshed successfully"}


@public_router.delete("/cache/clear")
async def clear_cache():
    """Очистить кэш фильтров"""
    await product_location_cache.clear_cache()
    return {"message": "Cache cleared successfully"}

# router = APIRouter(tags=["company_products"])
#
# @router.get("/company/{company_id}/products", response_model=ProductsResponse)
# async def get_company_products_by_id(
#     company_id: int,
#     page: int = Query(1, ge=1),
#     per_page: int = Query(10, ge=1, le=100),
#     products_repository: CompanyProductsRepository = Depends(get_company_products_repository)
# ):
#     return await products_repository.get_company_paginated_products(
#         company_id=company_id,
#         page=page,
#         per_page=per_page
#     )
#
# @router.get("/company/{company_slug}/products", response_model=ProductsResponse)
# async def get_company_products_by_slug(
#     company_slug: str,
#     page: int = Query(1, ge=1),
#     per_page: int = Query(10, ge=1, le=100),
#     products_repository: CompanyProductsRepository = Depends(get_company_products_repository)
# ):
#     return await products_repository.get_company_paginated_products(
#         company_slug=company_slug,
#         page=page,
#         per_page=per_page
#     )
