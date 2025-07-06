from typing import Annotated

from fastapi import Depends

from app.api.products.repositories.company_products_repository import CompanyProductsRepository
from app.api.products.repositories.my_products_repository import MyProductsRepository
from app.api.products.services.filter_service import FilterService
from app.api.products.services.product_service import ProductService
from app.api.products.services.search_service import ProductSearchService
from app.db.dependencies import async_db_dep


async def get_my_products_repository(db: async_db_dep) -> MyProductsRepository:
    """Зависимость для репозитория собственных продуктов пользователя"""
    return MyProductsRepository(db)


async def get_company_products_repository(db: async_db_dep) -> CompanyProductsRepository:
    """Зависимость для репозитория продуктов компаний"""
    return CompanyProductsRepository(db)


async def get_product_service(db: async_db_dep) -> ProductService:
    """Зависимость для сервиса продуктов"""
    my_products_repo = MyProductsRepository(db)
    company_products_repo = CompanyProductsRepository(db)
    return ProductService(my_products_repo, company_products_repo, db)


def get_filter_service(db: async_db_dep) -> FilterService:
    return FilterService(db)


def get_search_service(db: async_db_dep) -> ProductSearchService:
    return ProductSearchService(db)


# Аннотированные зависимости для использования в эндпоинтах
my_products_repository_dep = Annotated[MyProductsRepository, Depends(get_my_products_repository)]
company_products_repository_dep = Annotated[CompanyProductsRepository, Depends(get_company_products_repository)]
product_service_dep = Annotated[ProductService, Depends(get_product_service)]
