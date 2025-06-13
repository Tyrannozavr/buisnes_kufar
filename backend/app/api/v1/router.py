from fastapi import APIRouter

api_router = APIRouter()

from app.api.authentication.router import router as auth_router
from app.api.company.router import router as company_router
from app.api.common.router import router as locations_router

# Include routers
api_router.include_router(locations_router)

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(company_router, prefix="/company", tags=["company"])
