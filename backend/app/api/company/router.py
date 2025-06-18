from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from app.api.authentication.dependencies import current_user_dep, token_data_dep
from app.api.company.dependencies import company_service_dep
from app.api.company.schemas.company import CompanyUpdate, CompanyResponse, CompanyProfileResponse
from app.api.company.schemas.products import ProductsResponse, PaginationInfo
from app.api.company.services.company_service import CompanyService


router = APIRouter(tags=["company"])





@router.get("/me", response_model=Union[CompanyResponse, CompanyProfileResponse])
async def get_my_company(
        token_data: token_data_dep,
        company_service: company_service_dep
):
    """Get company data for current user. Returns full company data if exists, otherwise returns profile data."""
    company = await company_service.get_company_by_user(user_id=token_data.user_id)
    if company.is_company_created:
        return await company_service.get_full_company(token_data.user_id)
    return company


@router.put("/me", response_model=CompanyResponse)
async def update_my_company(
        company_data: CompanyUpdate,
        current_user: current_user_dep,
        company_service: company_service_dep
):
    return await company_service.update_company(current_user, company_data)


@router.post("/me/logo", response_model=CompanyResponse)
async def upload_company_logo(
        current_user: current_user_dep,
        company_service: company_service_dep,
        file: UploadFile = File(...)
):
    return await company_service.upload_logo(current_user, file)


@router.get("/me/products", response_model=ProductsResponse)
async def get_my_products(
        current_user: current_user_dep,
        company_service: company_service_dep
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
