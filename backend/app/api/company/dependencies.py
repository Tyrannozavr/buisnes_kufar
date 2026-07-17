from typing import Annotated

from fastapi import Depends

from app.api.company.repositories.company_official_repository import CompanyOfficialRepository
from app.api.company.repositories.company_repository import CompanyRepository
from app.api.company.repositories.fill_address_repository import CompanyFillAddressRepository
from app.api.company.repositories.fleet_repository import (
    CompanyVehicleRepository,
    CompanyDriverRepository,
)
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


async def get_fill_address_repository(db: async_db_dep) -> CompanyFillAddressRepository:
    return CompanyFillAddressRepository(db)


fill_address_repository_dep = Annotated[
    CompanyFillAddressRepository, Depends(get_fill_address_repository)
]


async def get_vehicle_repository(db: async_db_dep) -> CompanyVehicleRepository:
    return CompanyVehicleRepository(db)


vehicle_repository_dep = Annotated[CompanyVehicleRepository, Depends(get_vehicle_repository)]


async def get_driver_repository(db: async_db_dep) -> CompanyDriverRepository:
    return CompanyDriverRepository(db)


driver_repository_dep = Annotated[CompanyDriverRepository, Depends(get_driver_repository)]


def get_company_filter_service(db: async_db_dep) -> CompanyFilterService:
    return CompanyFilterService(db)
