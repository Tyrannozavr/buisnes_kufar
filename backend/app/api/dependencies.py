from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_async_db

async_db_dep = Annotated[AsyncSession, Depends(get_async_db)]
