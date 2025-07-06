from typing import Annotated

from fastapi import Depends

from app.api.companies.repositories.companies_repository import CompaniesRepository
from app.db.dependencies import async_db_dep


async def get_companies_repository(db: async_db_dep) -> CompaniesRepository:
    """Зависимость для получения репозитория компаний"""
    return CompaniesRepository(db)


companies_repository_dep = Annotated[CompaniesRepository, Depends(get_companies_repository)]
