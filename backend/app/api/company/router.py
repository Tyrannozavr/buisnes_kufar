from typing import Union, List, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, Body

from app.api.company.schemas.company_officials import CompanyOfficialCreate, CompanyOfficialUpdate, CompanyOfficial, \
    CompanyOfficialPartialUpdate
from app.api.authentication.dependencies import current_user_dep, token_data_dep
from app.api.company.dependencies import company_service_dep, official_repository_dep
from app.api.company.schemas.company import CompanyUpdate, CompanyResponse, CompanyProfileResponse
from app.api.company.schemas.products import ProductsResponse, PaginationInfo

router = APIRouter(tags=["company"])


@router.get("/me", response_model=Union[CompanyResponse, CompanyProfileResponse])
async def get_my_company(
        token_data: token_data_dep,
        company_service: company_service_dep
):
    """Get company data for current user. Returns full company data if exists, otherwise returns profile data."""
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
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


@router.post("/me/officials")
async def add_official(
        officials_repository: official_repository_dep,
        official_data: CompanyOfficialCreate,
        token_data: token_data_dep,
        company_service: company_service_dep
) -> CompanyOfficial:
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    return await officials_repository.create(official_data, company_id=company.id)


@router.get("/me/officials", response_model=List[CompanyOfficial])
async def get_officials(
    officials_repository: official_repository_dep,
    token_data: token_data_dep,
    company_service: company_service_dep
):
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    return await officials_repository.get_by_company_id(company_id=company.id)


@router.put("/me/officials/{official_id}", response_model=CompanyOfficial)
async def update_official(
    official_id: int,
    official_data: CompanyOfficialUpdate,
    officials_repository: official_repository_dep,
    token_data: token_data_dep,
    company_service: company_service_dep
):
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    official = await officials_repository.get_by_id(official_id)
    if not official or official.company_id != company.id:
        raise HTTPException(status_code=404, detail="Official not found")
    return await officials_repository.update(official_id, official_data)


@router.delete("/me/officials/{official_id}", response_model=dict)
async def delete_official(
    official_id: int,
    officials_repository: official_repository_dep,
    token_data: token_data_dep,
    company_service: company_service_dep
):
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    official = await officials_repository.get_by_id(official_id)
    if not official or official.company_id != company.id:
        raise HTTPException(status_code=404, detail="Official not found")
    await officials_repository.delete(official_id)
    return {"message": "Official successfully deleted"}


@router.patch("/me/officials/{official_id}", response_model=CompanyOfficial)
async def patch_official(
    official_id: int,
    officials_repository: official_repository_dep,
    token_data: token_data_dep,
    company_service: company_service_dep,
    official_data: CompanyOfficialPartialUpdate,

):
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    official = await officials_repository.get_by_id(official_id)
    if not official or official.company_id != company.id:
        raise HTTPException(status_code=404, detail="Official not found")

    
    return await officials_repository.partial_update(official_id, official_data)