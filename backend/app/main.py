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
# from app.api.celery.router import router as celery_router
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
    
    # Добавляем схему безопасности Bearer
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Применяем схему безопасности только к эндпоинтам аутентификации
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["get", "post", "put", "delete", "patch"]:
                # Применяем только к эндпоинтам, которые требуют авторизации
                if "/auth/" in path and not any(public_path in path for public_path in ["/login", "/register", "/token"]):
                    openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
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
# app.include_router(celery_router, prefix=settings.API_V1_STR)

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


@app.get("/api/v1/cities-filter/cities-filter")
async def get_cities_filter_tree():
    """Получить полное дерево локаций для фильтра городов"""
    try:
        from app.db.base import AsyncSessionLocal
        from app.api.common.models.country import Country
        from app.api.common.models.federal_district import FederalDistrict
        from app.api.common.models.region import Region
        from app.api.common.models.city import City
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as db:
            # Получаем все страны
            countries_result = await db.execute(
                select(Country).where(Country.is_active == True).order_by(Country.name)
            )
            countries = countries_result.scalars().all()
            
            location_tree = []
            
            for country in countries:
                country_data = {
                    "id": country.id,
                    "code": country.code,
                    "name": country.name,
                    "federal_districts": []
                }
                
                # Получаем федеральные округа для страны
                fd_result = await db.execute(
                    select(FederalDistrict)
                    .where(FederalDistrict.country_id == country.id, FederalDistrict.is_active == True)
                    .order_by(FederalDistrict.name)
                )
                federal_districts = fd_result.scalars().all()
                
                for fd in federal_districts:
                    fd_data = {
                        "id": fd.id,
                        "name": fd.name,
                        "code": fd.code,
                        "regions": []
                    }
                    
                    # Получаем регионы для федерального округа
                    regions_result = await db.execute(
                        select(Region)
                        .where(Region.federal_district_id == fd.id, Region.is_active == True)
                        .order_by(Region.name)
                    )
                    regions = regions_result.scalars().all()
                    
                    for region in regions:
                        region_data = {
                            "id": region.id,
                            "name": region.name,
                            "code": region.code,
                            "cities": []
                        }
                        
                        # Получаем города для региона
                        cities_result = await db.execute(
                            select(City)
                            .where(City.region_id == region.id, City.is_active == True)
                            .order_by(City.name)
                        )
                        cities = cities_result.scalars().all()
                        
                        for city in cities:
                            city_data = {
                                "id": city.id,
                                "name": city.name,
                                "population": city.population,
                                "is_million_city": city.is_million_city,
                                "is_regional_center": city.is_regional_center
                            }
                            region_data["cities"].append(city_data)
                        
                        fd_data["regions"].append(region_data)
                    
                    country_data["federal_districts"].append(fd_data)
                
                location_tree.append(country_data)
            
            return {
                "countries": location_tree,
                "total_countries": len(location_tree),
                "total_federal_districts": sum(len(country["federal_districts"]) for country in location_tree),
                "total_regions": sum(
                    len(fd["regions"]) 
                    for country in location_tree 
                    for fd in country["federal_districts"]
                ),
                "total_cities": sum(
                    len(region["cities"])
                    for country in location_tree
                    for fd in country["federal_districts"]
                    for region in fd["regions"]
                )
            }
        
    except Exception as e:
        return {"error": str(e)}

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