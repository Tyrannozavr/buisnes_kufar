from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from app.api.authentication.dependencies import CurrentUser
from app.api.company.repositories.company_repository import CompanyRepository
from app.api.company.schemas.company import CompanyUpdate, CompanyResponse, CompanyProfileResponse
from app.api.company.schemas.products import ProductsResponse, PaginationInfo
from app.api.company.services.company_service import CompanyService
from app.db.base import get_async_db

# from app.api.dependencies import get_async_db

router = APIRouter(tags=["company"])


async def get_company_service(db: AsyncSession = Depends(get_async_db)) -> CompanyService:
    company_repository = CompanyRepository(db)
    return CompanyService(company_repository, db)


@router.get("/me", response_model=Union[CompanyResponse, CompanyProfileResponse])
async def get_my_company(
        current_user: CurrentUser,
        company_service: CompanyService = Depends(get_company_service)
):
    """Get company data for current user. Returns full company data if exists, otherwise returns profile data."""
    company = await company_service.get_company_by_user(current_user)
    if company.is_company_created:
        return await company_service.get_full_company(current_user)
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


@router.get("/me/products", response_model=ProductsResponse)
async def get_my_products(
        current_user: CurrentUser,
        company_service: CompanyService = Depends(get_company_service)
):
    return ProductsResponse(
        data=[],
        pagination=PaginationInfo(
            total=0,
            page=1,
            perPage=10,
            totalPages=20,
        )
    )
