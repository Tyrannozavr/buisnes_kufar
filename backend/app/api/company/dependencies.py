from typing import Annotated

from fastapi import Depends

from app.api.company.repositories.company_official_repository import CompanyOfficialRepository
from app.api.company.repositories.company_repository import CompanyRepository
from app.api.company.services.company_service import CompanyService
from app.api.company.services.filter_service import CompanyFilterService
from app.db.dependencies import async_db_dep


async def get_company_service(db: async_db_dep) -> CompanyService:
    company_repository = CompanyRepository(db)
    return CompanyService(company_repository, db)


company_service_dep = Annotated[CompanyService, Depends(get_company_service)]


async def get_official_repository(db: async_db_dep) -> CompanyOfficialRepository:
    official_repository = CompanyOfficialRepository(db)
    return official_repository


official_repository_dep = Annotated[CompanyOfficialRepository, Depends(get_official_repository)]


def get_company_filter_service(db: async_db_dep) -> CompanyFilterService:
    return CompanyFilterService(db)
