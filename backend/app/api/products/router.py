from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from app.api.products.dependencies import product_service_dep
from app.api.products.schemas.product import (
    ProductCreate, 
    ProductUpdate, 
    ProductResponse, 
    ProductListResponse
)
from app.api.products.models.product import ProductType
from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User

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


@public_router.get("/company/{company_id}", response_model=ProductListResponse)
async def get_products_by_company_id(
    company_id: int,
    product_service: product_service_dep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_hidden: bool = Query(False)
):
    """Получить все продукты конкретной компании"""
    return await product_service.get_products_by_company_id(
        company_id, skip, limit, include_hidden
    )


@public_router.get("/company/{company_id}/services", response_model=ProductListResponse)
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


@public_router.get("/company/{company_id}/goods", response_model=ProductListResponse)
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


@public_router.get("/company/{company_id}/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(
    company_id: int,
    slug: str,
    product_service: product_service_dep
):
    """Получить продукт по slug и company_id (только активные и не скрытые)"""
    product = await product_service.get_product_by_slug(slug, company_id)
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