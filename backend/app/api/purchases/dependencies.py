from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import async_db_dep
from app.api.purchases.repositories import DealRepository
from app.api.purchases.services import DealService


async def deal_repository_dep(session: async_db_dep) -> DealRepository:
    return DealRepository(session)


async def deal_service_dep(session: async_db_dep) -> DealService:
    return DealService(session)
