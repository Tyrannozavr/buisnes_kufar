import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.responses import FileResponse

from app.admin.views import setup_admin
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base

# Import all schemas to ensure they are included in the OpenAPI schema

load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url=None,
    swagger_ui_parameters={"persistAuthorization": True}
)
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

# Database setup
engine = create_async_engine(settings.ASYNC_DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Admin panel setup
admin = setup_admin(app, engine)

# Templates setup
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

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
