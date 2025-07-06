from fastapi import APIRouter, Query, Path

from app.api.common.dependencies import public_announcement_service_dep
from app.api.common.schemas.announcements import PublicAnnouncementResponse, PublicAnnouncementListResponse

router = APIRouter(tags=["public-announcements"])


@router.get("", response_model=PublicAnnouncementListResponse)
async def get_all_announcements(
        announcement_service: public_announcement_service_dep,
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице")
):
    """Получить все опубликованные объявления (публичный доступ)"""
    return await announcement_service.get_all_announcements(page, per_page)


@router.get("/{announcement_id}", response_model=PublicAnnouncementResponse)
async def get_announcement(
        announcement_service: public_announcement_service_dep,
        announcement_id: int = Path(..., description="ID объявления")
):
    """Получить опубликованное объявление по ID (публичный доступ)"""
    return await announcement_service.get_announcement_by_id(announcement_id)


@router.get("/company/{company_id}", response_model=PublicAnnouncementListResponse)
async def get_company_announcements(
        announcement_service: public_announcement_service_dep,
        company_id: int = Path(..., description="ID компании"),
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице")
):
    """Получить опубликованные объявления конкретной компании (публичный доступ)"""
    return await announcement_service.get_company_announcements(company_id, page, per_page)


@router.get("/category/{category}", response_model=PublicAnnouncementListResponse)
async def get_announcements_by_category(
        announcement_service: public_announcement_service_dep,
        category: str = Path(..., description="Категория объявлений"),
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице")
):
    """Получить опубликованные объявления по категории (публичный доступ)"""
    return await announcement_service.get_announcements_by_category(category, page, per_page)


@router.get("/categories/list")
async def get_announcement_categories():
    """Получить список доступных категорий объявлений"""
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
