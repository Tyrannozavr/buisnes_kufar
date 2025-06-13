from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.dependencies import CurrentUser
from app.api.company.repositories.company_repository import CompanyRepository
from app.api.company.schemas.company import CompanyUpdate, CompanyResponse
from app.api.company.services.company_service import CompanyService
from app.db.base import get_async_db

# from app.api.dependencies import get_async_db

router = APIRouter(tags=["company"])

async def get_company_service(db: AsyncSession = Depends(get_async_db)) -> CompanyService:
    company_repository = CompanyRepository(db)
    return CompanyService(company_repository, db)

@router.get("/me", response_model=CompanyResponse)
async def get_my_company(
    current_user: CurrentUser,
    company_service: CompanyService = Depends(get_company_service)
):
    """Это проверка компании текущего пользователя. Если компании нет, создается пустая запись."""
    company = await company_service.get_or_create_company_by_user(current_user)
    return company

@router.put("/me", response_model=CompanyResponse)
async def update_my_company(
    company_data: CompanyUpdate,
    current_user: CurrentUser,
    company_service: CompanyService = Depends(get_company_service)
):
    return await company_service.update_company(current_user, company_data)

@router.post("/me/logo", response_model=CompanyResponse)
async def upload_company_logo(
    current_user: CurrentUser,
    company_service: CompanyService = Depends(get_company_service),
    file: UploadFile = File(...)
):
    return await company_service.upload_logo(current_user, file)