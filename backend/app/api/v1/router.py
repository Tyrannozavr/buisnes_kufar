from fastapi import APIRouter

api_router = APIRouter()

from app.api.authentication.router import router as auth_router
from app.api.company.router import router as company_router
from app.api.common.router import router as locations_router
from app.api.common.announcements_router import router as public_announcements_router
from app.api.companies.router import router as companies_router
from app.api.chats.router import router as chats_router
from app.api.products.router import owner_router as products_owner_router, public_router as public_products_router

# Include routers

api_router.include_router(companies_router, prefix="/companies", tags=["companies"])

api_router.include_router(locations_router, prefix="/locations")

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(company_router, prefix="/company", tags=["company"])
api_router.include_router(chats_router, prefix="/chats", tags=["chats"])
api_router.include_router(products_owner_router, prefix="/me/products", tags=["products", "owner"])

api_router.include_router(public_products_router, prefix="/products", tags=["public-products"])
api_router.include_router(public_announcements_router, prefix="/announcements", tags=["public-announcements"])
api_router.include_router(locations_router, prefix="/companies/locations")
