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
    # Не используем кэш, чтобы всегда генерировать свежую схему
    # if app.openapi_schema:
    #     return app.openapi_schema
    
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
    # Обычно она называется "BearerAuth", но некоторые эндпоинты используют "Bearer"
    # Мы создаем обе схемы для совместимости
    security_schemes = openapi_schema["components"]["securitySchemes"]
    
    # Находим существующую схему (BearerAuth или Bearer)
    existing_scheme = None
    for name in ["BearerAuth", "Bearer"]:
        if name in security_schemes:
            existing_scheme = security_schemes[name]
            break
    
    # Создаем правильную схему
    correct_scheme = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "OAuth2 password bearer token"
    }
    
    # Если есть существующая схема, используем её как основу, но исправляем поля
    # ВАЖНО: для Bearer токенов тип должен быть "http", а не "oauth2"
    if existing_scheme and isinstance(existing_scheme, dict):
        # Принудительно устанавливаем правильный тип для Bearer токенов
        correct_scheme["type"] = "http"
        correct_scheme["scheme"] = existing_scheme.get("scheme", "bearer")
        correct_scheme["bearerFormat"] = existing_scheme.get("bearerFormat", "JWT")
        if "description" in existing_scheme:
            correct_scheme["description"] = existing_scheme["description"]
    
    # Убеждаемся, что type всегда "http" для Bearer токенов
    correct_scheme["type"] = "http"
    
    # Убеждаемся, что все security schemes правильно структурированы
    # Удаляем любые схемы с undefined значениями
    for scheme_name, scheme_def in list(security_schemes.items()):
        if not isinstance(scheme_def, dict) or scheme_def.get("type") is None:
            # Удаляем некорректные схемы
            del security_schemes[scheme_name]
    
    # Создаем только одну схему Bearer для стандартного вида в Swagger UI
    # Удаляем BearerAuth, если он есть, чтобы не было дублирования форм авторизации
    security_schemes_dict = openapi_schema["components"]["securitySchemes"]
    
    # Удаляем BearerAuth, если он существует
    if "BearerAuth" in security_schemes_dict:
        del security_schemes_dict["BearerAuth"]
    
    # Убеждаемся, что изменения применены - принудительно перезаписываем
    # Создаем только схему Bearer для стандартного вида
    # ВАЖНО: тип должен быть "http" для Bearer токенов, а не "oauth2"
    final_schemes = {
        "Bearer": {
            "type": "http",  # Принудительно устанавливаем правильный тип
            "scheme": correct_scheme.get("scheme", "bearer"),
            "bearerFormat": correct_scheme.get("bearerFormat", "JWT"),
            "description": correct_scheme.get("description", "OAuth2 password bearer token")
        }
    }
    
    # Принудительно устанавливаем только схему Bearer
    openapi_schema["components"]["securitySchemes"] = final_schemes

    # Описания тегов для Swagger UI (счет, договор, договор поставки)
    if "tags" not in openapi_schema:
        openapi_schema["tags"] = []
    doc_tags = [
        {"name": "bill", "description": "Создание номера и даты счета на оплату"},
        {"name": "contract", "description": "Создание номера и даты договора"},
        {"name": "supply-contract", "description": "Создание номера и даты договора поставки"},
        {"name": "versions", "description": "Управление версиями сделки: создание новой и удаление последней версии"},
        {"name": "batch", "description": "Массовое получение сделок по списку ID (аналог GET /deals/{id} для нескольких сделок)"},
    ]
    existing_names = {t["name"] for t in openapi_schema["tags"] if isinstance(t, dict) and "name" in t}
    for tag in doc_tags:
        if tag["name"] not in existing_names:
            openapi_schema["tags"].append(tag)

    # Не кэшируем схему, чтобы изменения применялись сразу
    # app.openapi_schema = openapi_schema
    return openapi_schema

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