from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base_class import Base  # noqa

# Import all models here to ensure they are registered with SQLAlchemy metadata
from app.api.authentication.models.user import User  # noqa
from app.api.company.models.company import Company  # noqa
from app.api.company.models.official import CompanyOfficial  # noqa
from app.api.products.models.product import Product  # noqa
from app.api.messages.models.message import Message  # noqa
from app_logging.logger import logger


engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
