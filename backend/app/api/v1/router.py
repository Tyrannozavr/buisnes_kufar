from fastapi import APIRouter

api_router = APIRouter()

# Include routers
# api_router.include_router(auth_router, prefix="/auth", tags=["auth"])