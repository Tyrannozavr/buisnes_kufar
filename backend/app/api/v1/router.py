from fastapi import APIRouter

api_router = APIRouter()

from app.api.authentication.router import router as auth_router
from app.api.authentication.router_employee import router as employee_router
from app.api.company.router import router as company_router
from app.api.common.routes.location_tree import router as location_tree_router
from app.api.common.routes.location_create import router as location_create_router
from app.api.common.announcements_router import router as public_announcements_router
from app.api.companies.router import router as companies_router
from app.api.chats.router import router as chats_router
from app.api.purchases.router import router as purchases_router
from app.api.products.router import owner_router as products_owner_router, public_router as public_products_router
from app.api.common.routes.cities_filter import router as cities_filter_router

# Include routers

api_router.include_router(companies_router, prefix="/companies", tags=["companies"])

# Заменяем старые endpoints локаций на новые из локальной БД
api_router.include_router(location_tree_router, prefix="/locations", tags=["locations"])
api_router.include_router(location_create_router, prefix="/locations", tags=["locations"])

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(employee_router, prefix="/auth", tags=["employees"])
api_router.include_router(company_router, prefix="/company", tags=["company"])
api_router.include_router(chats_router, prefix="/chats", tags=["chats"])
api_router.include_router(products_owner_router, prefix="/me/products", tags=["products", "owner"])
api_router.include_router(purchases_router, prefix="/purchases", tags=["purchases", "orders"])

api_router.include_router(public_products_router, prefix="/products", tags=["public-products"])
api_router.include_router(public_announcements_router, prefix="/announcements", tags=["public-announcements"])
api_router.include_router(cities_filter_router, prefix="/cities-filter", tags=["cities-filter"])
