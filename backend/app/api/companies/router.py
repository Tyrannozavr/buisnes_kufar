from typing import Optional

from fastapi import APIRouter, Query

from app.api.companies.dependencies import companies_repository_dep
from app.api.companies.repositories.companies_repository import CompaniesRepository
from app.api.companies.schemas.companies import CompaniesResponse, PaginationInfo

router = APIRouter(tags=["companies"])


@router.get("/", response_model=CompaniesResponse)
async def get_companies(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    limit: Optional[int] = Query(None, ge=1, description="Ограничение общего количества"),
    companies_repository: companies_repository_dep = None
) -> CompaniesResponse:
    """
    Получить список компаний с пагинацией
    
    Args:
        page: Номер страницы (начиная с 1)
        per_page: Количество элементов на странице (1-100)
        limit: Ограничение общего количества (опционально)
        companies_repository: Репозиторий компаний
        
    Returns:
        CompaniesResponse: Список компаний с информацией о пагинации
    """
    companies, total_count = await companies_repository.get_companies_paginated(
        page=page,
        per_page=per_page,
        limit=limit
    )
    
    # Вычисляем общее количество страниц
    total_pages = (total_count + per_page - 1) // per_page
    
    return CompaniesResponse(
        data=companies,
        pagination=PaginationInfo(
            total=total_count,
            page=page,
            perPage=per_page,
            totalPages=total_pages
        )
    ) 