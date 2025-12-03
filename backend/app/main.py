import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.responses import FileResponse

from app.admin.views import setup_admin
from app.api.v1.router import api_router
from app.api.celery.router import router as celery_router
from app.core.config import settings
from app.db.base import Base

# Import all schemas to ensure they are included in the OpenAPI schema

load_dotenv()

# Database setup
engine = create_async_engine(settings.ASYNC_DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔧 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created!")
    yield
    # Shutdown
    print("🔄 Disposing database engine...")
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url=None,
    swagger_ui_parameters={"persistAuthorization": True},
    lifespan=lifespan
)

# Настройка схемы безопасности для Swagger UI
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version="0.1.0",
        description="Business Trade API",
        routes=app.routes,
    )
    
    # Убеждаемся, что components существует
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    # Инициализируем securitySchemes, если его нет
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}
    
    # FastAPI автоматически создает схему безопасности через OAuth2PasswordBearer
    # Мы убеждаемся, что схема правильно определена и не содержит undefined значений
    # Проверяем и исправляем существующую схему Bearer, если она есть
    bearer_scheme = openapi_schema["components"]["securitySchemes"].get("Bearer")
    
    # Если схема существует, убеждаемся, что она правильно структурирована
    if bearer_scheme:
        # Убеждаемся, что все обязательные поля присутствуют
        if "type" not in bearer_scheme or bearer_scheme.get("type") is None:
            bearer_scheme["type"] = "http"
        if "scheme" not in bearer_scheme or bearer_scheme.get("scheme") is None:
            bearer_scheme["scheme"] = "bearer"
        if "bearerFormat" not in bearer_scheme:
            bearer_scheme["bearerFormat"] = "JWT"
    else:
        # Создаем схему, если её нет
        openapi_schema["components"]["securitySchemes"]["Bearer"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "OAuth2 password bearer token"
        }
    
    # Убеждаемся, что все security schemes правильно структурированы
    # Удаляем любые схемы с undefined значениями
    security_schemes = openapi_schema["components"]["securitySchemes"]
    for scheme_name, scheme_def in list(security_schemes.items()):
        if not isinstance(scheme_def, dict) or scheme_def.get("type") is None:
            # Удаляем некорректные схемы
            del security_schemes[scheme_name]
    
    # Нормализуем схемы безопасности: убеждаемся, что "Bearer" существует
    # FastAPI может создавать "BearerAuth", но эндпоинты используют "Bearer"
    if "BearerAuth" in security_schemes and "Bearer" not in security_schemes:
        # Копируем BearerAuth в Bearer, если Bearer не существует
        bearer_auth = security_schemes.get("BearerAuth")
        if bearer_auth and isinstance(bearer_auth, dict) and bearer_auth.get("type") is not None:
            security_schemes["Bearer"] = bearer_auth.copy()
    elif "BearerAuth" in security_schemes:
        # Если обе схемы существуют, используем Bearer как основную
        if "Bearer" not in security_schemes:
            bearer_auth = security_schemes.get("BearerAuth")
            if bearer_auth and isinstance(bearer_auth, dict) and bearer_auth.get("type") is not None:
                security_schemes["Bearer"] = bearer_auth.copy()
    
    # Убеждаемся, что Bearer схема правильно определена
    if "Bearer" in security_schemes:
        bearer_scheme = security_schemes["Bearer"]
        if not isinstance(bearer_scheme, dict) or bearer_scheme.get("type") is None:
            security_schemes["Bearer"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "OAuth2 password bearer token"
            }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
favicon_path = 'app/favicon.ico'


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


@app.get('/health', include_in_schema=False)
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "backend"}


# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin panel setup
admin = setup_admin(app, engine)

# Templates setup
templates = Jinja2Templates(directory="app/templates")


# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(celery_router, prefix=settings.API_V1_STR)

# Простые endpoints для фильтра городов
@app.get("/api/v1/cities-filter/cities-stats")
async def get_cities_stats():
    """Получить статистику по городам"""
    try:
        from app.db.base import AsyncSessionLocal
        from app.api.common.models.city import City
        from app.api.common.models.federal_district import FederalDistrict
        from app.api.common.models.region import Region
        from sqlalchemy import select, and_
        
        async with AsyncSessionLocal() as db:
            # Общее количество городов
            total_cities_result = await db.execute(
                select(City).where(City.is_active == True)
            )
            total_cities = len(total_cities_result.scalars().all())
            
            # Города-миллионники
            million_cities_result = await db.execute(
                select(City).where(and_(City.is_active == True, City.is_million_city == True))
            )
            million_cities = len(million_cities_result.scalars().all())
            
            # Региональные центры
            regional_centers_result = await db.execute(
                select(City).where(and_(City.is_active == True, City.is_regional_center == True))
            )
            regional_centers = len(regional_centers_result.scalars().all())
            
            # Количество федеральных округов
            fd_result = await db.execute(
                select(FederalDistrict).where(FederalDistrict.is_active == True)
            )
            total_federal_districts = len(fd_result.scalars().all())
            
            # Количество регионов
            regions_result = await db.execute(
                select(Region).where(Region.is_active == True)
            )
            total_regions = len(regions_result.scalars().all())
            
            return {
                "total_cities": total_cities,
                "million_cities": million_cities,
                "regional_centers": regional_centers,
                "total_federal_districts": total_federal_districts,
                "total_regions": total_regions
            }
        
    except Exception as e:
        return {"error": str(e)}


# Эндпоинт перенесен в cities_filter.py router

# Get the absolute path to the uploads directory
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

os.makedirs(uploads_dir, exist_ok=True)  # Create the uploads directory if it doesn't exist'
# Mount the static files directory
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Returns a beautiful HTML page with links to /docs and /admin"""
    return templates.TemplateResponse("index.html", {"request": request})


DEV_REDIRECT_URL = os.getenv("DEV_REDIRECT_URL", "http://localhost:3000")