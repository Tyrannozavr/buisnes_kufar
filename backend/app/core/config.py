from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os

def get_async_database_url(sync_url: str) -> str:
    """Convert sync database URL to async URL."""
    if sync_url.startswith('sqlite:'):
        return sync_url.replace('sqlite:', 'sqlite+aiosqlite:', 1)
    elif sync_url.startswith('postgresql:'):
        return sync_url.replace('postgresql:', 'postgresql+asyncpg:', 1)
    # Add more cases for other database types as needed
    return sync_url  # Return original if no conversion is needed

class Settings(BaseSettings):
    PROJECT_NAME: str = "Business Kufar"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Настройки безопасности
    SECRET_KEY: str = "your-secret-key-here"  # В продакшене заменить на безопасный ключ
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Настройки базы данных
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Настройки фронтенда
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS настройки
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",  # Add this line
        "http://127.0.0.1:3000",  # Add this line
    ]
    
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: str
    MAIL_SERVER: str
    
    # Static files
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return get_async_database_url(self.SQLALCHEMY_DATABASE_URI)

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()