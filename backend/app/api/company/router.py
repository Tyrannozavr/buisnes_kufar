from typing import Union, List

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi import status

from app.api.authentication.dependencies import current_user_dep, token_data_dep
from app.api.authentication.models import User
from app.api.company.dependencies import company_service_dep, official_repository_dep
from app.api.company.repositories.announcement_repository import AnnouncementRepository
from app.api.company.schemas.announcements import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse, \
    AnnouncementListResponse
from app.api.company.schemas.company import CompanyUpdate, CompanyResponse, CompanyProfileResponse
from app.api.company.schemas.company_officials import CompanyOfficialCreate, CompanyOfficialUpdate, CompanyOfficial, \
    CompanyOfficialPartialUpdate
from app.api.company.services.announcement_service import AnnouncementService
from app.api.dependencies import async_db_dep

router = APIRouter(tags=["company"])


@router.get("/me", response_model=Union[CompanyResponse, CompanyProfileResponse])
async def get_my_company(
        token_data: token_data_dep,
        company_service: company_service_dep
):
    """Get company data for current user. Returns full company data if exists, otherwise returns profile data."""
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    if company.is_company_created:
        return await company_service.get_full_company(token_data.user_id)
    return company


@router.put("/me", response_model=CompanyResponse)
async def update_my_company(
        company_data: CompanyUpdate,
        current_user: current_user_dep,
        company_service: company_service_dep
):
    return await company_service.update_company(current_user, company_data)


@router.post("/me/logo", response_model=CompanyResponse)
async def upload_company_logo(
        current_user: current_user_dep,
        company_service: company_service_dep,
        file: UploadFile = File(...)
):
    return await company_service.upload_logo(current_user, file)


@router.post("/me/officials")
async def add_official(
        officials_repository: official_repository_dep,
        official_data: CompanyOfficialCreate,
        token_data: token_data_dep,
        company_service: company_service_dep
) -> CompanyOfficial:
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    return await officials_repository.create(official_data, company_id=company.id)


@router.get("/me/officials", response_model=List[CompanyOfficial])
async def get_officials(
        officials_repository: official_repository_dep,
        token_data: token_data_dep,
        company_service: company_service_dep
):
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    return await officials_repository.get_by_company_id(company_id=company.id)


@router.put("/me/officials/{official_id}", response_model=CompanyOfficial)
async def update_official(
        official_id: int,
        official_data: CompanyOfficialUpdate,
        officials_repository: official_repository_dep,
        token_data: token_data_dep,
        company_service: company_service_dep
):
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    official = await officials_repository.get_by_id(official_id)
    if not official or official.company_id != company.id:
        raise HTTPException(status_code=404, detail="Official not found")
    return await officials_repository.update(official_id, official_data)


@router.delete("/me/officials/{official_id}", response_model=dict)
async def delete_official(
        official_id: int,
        officials_repository: official_repository_dep,
        token_data: token_data_dep,
        company_service: company_service_dep
):
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    official = await officials_repository.get_by_id(official_id)
    if not official or official.company_id != company.id:
        raise HTTPException(status_code=404, detail="Official not found")
    await officials_repository.delete(official_id)
    return {"message": "Official successfully deleted"}


@router.patch("/me/officials/{official_id}", response_model=CompanyOfficial)
async def patch_official(
        official_id: int,
        officials_repository: official_repository_dep,
        token_data: token_data_dep,
        company_service: company_service_dep,
        official_data: CompanyOfficialPartialUpdate,

):
    company = await company_service.get_company_by_user_id(user_id=token_data.user_id)
    official = await officials_repository.get_by_id(official_id)
    if not official or official.company_id != company.id:
        raise HTTPException(status_code=404, detail="Official not found")

    return await officials_repository.partial_update(official_id, official_data)


@router.get("/announcements/categories")
async def get_announcements_categories():
    return [
        {
            "id": "1",
            "name": "Товары",
            "description": "Объявления о товарах и продукции компании"
        },
        {
            "id": "2",
            "name": "Услуги",
            "description": "Объявления об услугах, предоставляемых компанией"
        },
        {
            "id": "3",
            "name": "Акции",
            "description": "Специальные предложения, скидки и акции"
        },
        {
            "id": "4",
            "name": "Партнерство",
            "description": "Предложения о сотрудничестве и партнерстве"
        },
        {
            "id": "5",
            "name": "События",
            "description": "Информация о мероприятиях, выставках и конференциях"
        },
        {
            "id": "6",
            "name": "Вакансии",
            "description": "Объявления о вакансиях и наборе персонала"
        },
        {
            "id": "7",
            "name": "Новости",
            "description": "Новости компании и отрасли"
        }
    ]


# Announcements routes
@router.post("/announcements", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    db: async_db_dep,
    announcement_data: AnnouncementCreate,
    current_user: current_user_dep
):
    """Создать новое объявление для компании"""
    announcement_repository = AnnouncementRepository(session=db)
    announcement_service = AnnouncementService(announcement_repository=announcement_repository)
    
    # Временные notifications (в реальном приложении они будут приходить из запроса)
    notifications = {
        "partners": True,
        "customers": True,
        "suppliers": True
    }
    
    return await announcement_service.create_announcement(current_user, announcement_data, notifications)


@router.get("/announcements", response_model=AnnouncementListResponse)
async def get_company_announcements(
    db: async_db_dep,
    current_user: current_user_dep,
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице")
):
    """Получить все объявления компании пользователя"""
    announcement_repository = AnnouncementRepository(session=db)
    announcement_service = AnnouncementService(announcement_repository=announcement_repository)
    
    return await announcement_service.get_company_announcements(current_user, page, per_page)


@router.get("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    db: async_db_dep,
    announcement_id: int,
    current_user: current_user_dep
):
    """Получить объявление по ID"""
    announcement_repository = AnnouncementRepository(session=db)
    announcement_service = AnnouncementService(announcement_repository=announcement_repository)
    
    return await announcement_service.get_announcement(current_user, announcement_id)


@router.put("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    db: async_db_dep,
    announcement_id: int,
    announcement_data: AnnouncementUpdate,
    current_user: current_user_dep
):
    """Обновить объявление"""
    announcement_repository = AnnouncementRepository(session=db)
    announcement_service = AnnouncementService(announcement_repository=announcement_repository)
    
    return await announcement_service.update_announcement(current_user, announcement_id, announcement_data)


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    db: async_db_dep,
    announcement_id: int,
    current_user: current_user_dep
):
    """Удалить объявление"""
    announcement_repository = AnnouncementRepository(session=db)
    announcement_service = AnnouncementService(announcement_repository=announcement_repository)
    
    success = await announcement_service.delete_announcement(current_user, announcement_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )


@router.post("/announcements/{announcement_id}/images", response_model=AnnouncementResponse)
async def upload_announcement_image(
    db: async_db_dep,
    current_user: current_user_dep,
    announcement_id: int,
    file: UploadFile = File(...),
):
    """Загрузить изображение для объявления"""
    announcement_repository = AnnouncementRepository(session=db)
    announcement_service = AnnouncementService(announcement_repository=announcement_repository)
    
    return await announcement_service.upload_announcement_image(current_user, announcement_id, file)


@router.put("/announcements/{announcement_id}/publish", response_model=AnnouncementResponse)
async def toggle_announcement_publish(
    db: async_db_dep,
    announcement_id: int,
    current_user: current_user_dep
):
    """Опубликовать или снять с публикации объявление"""
    announcement_repository = AnnouncementRepository(session=db)
    announcement_service = AnnouncementService(announcement_repository=announcement_repository)
    
    return await announcement_service.toggle_publish_status(current_user, announcement_id)


# Public routes for announcements
@router.get("/public/announcements/{company_id}", response_model=AnnouncementListResponse)
async def get_public_announcements(
    company_id: int,
    db: async_db_dep,
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице")
):
    """Получить опубликованные объявления компании (публичный доступ)"""
    announcement_repository = AnnouncementRepository(session=db)
    announcement_service = AnnouncementService(announcement_repository=announcement_repository)
    
    return await announcement_service.get_public_announcements(company_id, page, per_page)


@router.get("/public/announcements/{company_id}/{announcement_id}", response_model=AnnouncementResponse)
async def get_public_announcement(
    company_id: int,
    announcement_id: int,
    db: async_db_dep
):
    """Получить опубликованное объявление компании по ID (публичный доступ)"""
    announcement_repository = AnnouncementRepository(session=db)
    announcement_service = AnnouncementService(announcement_repository=announcement_repository)
    
    # Получаем объявление и проверяем, что оно принадлежит указанной компании и опубликовано
    announcement = await announcement_repository.get_by_id(announcement_id)
    if not announcement or announcement.company_id != company_id or not announcement.published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    return AnnouncementResponse.model_validate(announcement)
