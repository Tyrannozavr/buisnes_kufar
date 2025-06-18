from typing import Annotated

from fastapi import Depends

from app.api.company.repositories.company_repository import CompanyRepository
from app.api.company.services.company_service import CompanyService
from app.db.dependencies import async_db_dep


async def get_company_service(db: async_db_dep) -> CompanyService:
    company_repository = CompanyRepository(db)
    return CompanyService(company_repository, db)


company_service_dep = Annotated[CompanyService, Depends(get_company_service)]
