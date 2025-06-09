from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

def get_async_database_url(sync_url: str) -> str:
    """Convert sync database URL to async URL."""
    if sync_url.startswith('sqlite:'):
        return sync_url.replace('sqlite:', 'sqlite+aiosqlite:', 1)
    elif sync_url.startswith('postgresql:'):
        return sync_url.replace('postgresql:', 'postgresql+asyncpg:', 1)
    # Add more cases for other database types as needed
    return sync_url  # Return original if no conversion is needed

class Settings(BaseSettings):
    PROJECT_NAME: str = "Talkery"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"  # Synchronous URL for Alembic

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return get_async_database_url(self.DATABASE_URL)
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key"  # Change in production
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "secretpassword"  # Замените на свой пароль администратора
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Static files
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()