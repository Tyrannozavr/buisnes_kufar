from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base_class import Base

# Create a synchronous engine specifically for Alembic
sync_engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Function to get database URL for Alembic
def get_ASYNC_DATABASE_URL():
    return settings.DATABASE_URL 