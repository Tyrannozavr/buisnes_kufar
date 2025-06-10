from fastapi import APIRouter

api_router = APIRouter()

from app.api.authentication.router import router as auth_router

# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])