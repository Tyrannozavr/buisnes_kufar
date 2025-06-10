from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db

# Async database session dependency
get_async_db = Annotated[AsyncSession, Depends(get_db)] 