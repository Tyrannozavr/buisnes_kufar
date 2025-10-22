from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables before anything else
load_dotenv()

from pydantic_settings import BaseSettings


def get_async_database_url(sync_url: str) -> str:
    """Convert sync database URL to async URL."""
    if sync_url is None:
        sync_url = "sqlite:///./database.db"
    if sync_url.startswith('sqlite:'):
        return sync_url.replace('sqlite:', 'sqlite+aiosqlite:', 1)
    elif sync_url.startswith('postgresql:'):
        return sync_url.replace('postgresql:', 'postgresql+asyncpg:', 1)
    # Add more cases for other database types as needed
    return sync_url  # Return original if no conversion is needed


class Settings(BaseSettings):
    PROJECT_NAME: str = "Business Trade API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "your-secret-key-here"  # В продакшене заменить на безопасный ключ
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Cookie settings
    COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"  # Options: "lax", "strict", "none"
    COOKIE_DOMAIN: Optional[str] = None
    COOKIE_PATH: str = "/"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "business_trade"
    SQLALCHEMY_DATABASE_URL: Optional[str] = None

    # Настройки фронтенда
    FRONTEND_URL: str = "http://localhost:3000"
    BASE_IMAGE_URL: str = "http://localhost:8000"

    BASE_FILES_URL: str = "http://localhost:8000"

    # CORS настройки
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",  # Для Docker dev окружения
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost",  # Для nginx прокси
        "http://127.0.0.1",  # Для nginx прокси
    ]

    MAIL_USERNAME: str | None = "mock_email@example.com"
    MAIL_PASSWORD: str | None = "mock_password_here"
    MAIL_FROM: str | None = "mock_email@example.com"
    MAIL_PORT: int | None = 587
    MAIL_SERVER: str | None = "smtp.gmail.com"

    # Static files
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"

    # API ключ для сервиса локаций (htmlweb.ru)
    LOCATION_API_KEY: Optional[str] = None

    # reCAPTCHA v3 settings
    RECAPTCHA_SECRET_KEY: str = "6LdJHHorAAAAAEUE2R1s_QsmJPLR0PSCPnB1_TQy"  # Замените на ваш секретный ключ
    RECAPTCHA_SITE_KEY: str = "6LdJHHorAAAAAG2JB9CyOtRQbPJWrxbdRPy0dMHO"  # Замените на ваш публичный ключ
    RECAPTCHA_MIN_SCORE: float = 0.5  # Минимальный балл для прохождения проверки

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return get_async_database_url(self.SQLALCHEMY_DATABASE_URL)

    class Config:
        case_sensitive = True


settings = Settings()
