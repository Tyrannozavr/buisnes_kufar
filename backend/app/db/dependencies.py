from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import base as db_base


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Корректный генератор сессии"""
    async with db_base.AsyncSessionLocal() as session:
        try:
            yield session
            # Сессию могли закрыть до долгого I/O (Gotenberg и т.п.)
            if session.is_active:
                await session.commit()
        except Exception:
            if session.is_active:
                await session.rollback()
            raise


# Правильная аннотация зависимости
async_db_dep = Annotated[AsyncSession, Depends(get_async_db)]
