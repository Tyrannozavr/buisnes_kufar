from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import async_db_dep
from app.api.purchases.repositories import DealRepository
from app.api.purchases.services import DealService
from app.api.purchases.services.supply_contract import SupplyContractService
from app.api.purchases.services.company_contract import CompanyContractService
from app.api.purchases.services.supply_contract_template import (
	SupplyContractTemplateService,
	SupplyContractTemplateAlreadyExistsError,
)


def deal_repository_dep(session: async_db_dep) -> DealRepository:
    return DealRepository(session)


def deal_service_dep(session: async_db_dep) -> DealService:
    return DealService(session)


def supply_contract_service_dep(session: async_db_dep) -> SupplyContractService:
	return SupplyContractService(session)


def company_contract_service_dep(session: async_db_dep) -> CompanyContractService:
	return CompanyContractService(session)


def supply_contract_template_service_dep(session: async_db_dep) -> SupplyContractTemplateService:
	return SupplyContractTemplateService(session)


# Аннотированные зависимости для использования в эндпоинтах
deal_repository_dep_annotated = Annotated[DealRepository, Depends(deal_repository_dep)]
deal_service_dep_annotated = Annotated[DealService, Depends(deal_service_dep)]
supply_contract_service_dep_annotated = Annotated[SupplyContractService, Depends(supply_contract_service_dep)]
company_contract_service_dep_annotated = Annotated[CompanyContractService, Depends(company_contract_service_dep)]
supply_contract_template_service_dep_annotated = Annotated[
	SupplyContractTemplateService,
	Depends(supply_contract_template_service_dep),
]
