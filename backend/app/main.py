from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.admin.views import setup_admin
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
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

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Returns a beautiful HTML page with links to /docs and /admin"""
    return templates.TemplateResponse("index.html", {"request": request})