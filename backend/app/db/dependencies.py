from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Корректный генератор сессии"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            pass

# Правильная аннотация зависимости
async_db_dep = Annotated[AsyncSession, Depends(get_async_db)]