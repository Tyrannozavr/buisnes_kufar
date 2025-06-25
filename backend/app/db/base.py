from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

# Import all models here to ensure they are registered with SQLAlchemy metadata
from app.api.authentication.models.user import User  # noqa
from app.api.company.models.company import Company  # noqa
from app.api.company.models.official import CompanyOfficial  # noqa
from app.api.messages.models.message import Message  # noqa
from app.api.products.models.product import Product  # noqa
from app.core.config import settings
from app.db.base_class import Base  # noqa
from app_logging.logger import logger

engine = create_async_engine(
    settings.ASYNC_DATABASE_URL, 
    echo=False, 
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


