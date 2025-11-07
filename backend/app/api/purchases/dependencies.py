from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import async_db_dep
from app.api.purchases.repositories import DealRepository
from app.api.purchases.services import DealService


def deal_repository_dep(session: async_db_dep) -> DealRepository:
    return DealRepository(session)


def deal_service_dep(session: async_db_dep) -> DealService:
    return DealService(session)


# Аннотированные зависимости для использования в эндпоинтах
deal_repository_dep_annotated = Annotated[DealRepository, Depends(deal_repository_dep)]
deal_service_dep_annotated = Annotated[DealService, Depends(deal_service_dep)]
