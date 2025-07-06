import asyncio
from typing import Optional, Any, Coroutine, List, Dict
from fastapi import APIRouter, Query, HTTPException, Body

from api.products.dependencies import company_products_repository_dep
from app.api.company.schemas.company import CompanyResponse, ShortCompanyResponse, CompanyStatisticsResponse
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


@router.get("/services", response_model=CompaniesResponse)
async def get_services_companies(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    filtration_parameters: List[Dict[str, Any]] = Body(default=[], description="Параметры фильтрации"),
    companies_repository: companies_repository_dep = None
) -> CompaniesResponse:
    """
    Получить список компаний, предоставляющих услуги (включая те, что делают оба)
    
    Args:
        page: Номер страницы (начиная с 1)
        per_page: Количество элементов на странице (1-100)
        filtration_parameters: Список словарей с параметрами фильтрации
        companies_repository: Репозиторий компаний
        
    Returns:
        CompaniesResponse: Список компаний с информацией о пагинации
    """
    print(f"Параметры фильтрации для услуг: {filtration_parameters}")
    
    companies, total_count = await companies_repository.get_services_companies(
        page=page,
        per_page=per_page,
        # filtration_parameters=filtration_parameters
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

@router.get("/products", response_model=CompaniesResponse)
async def get_product_companies(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    search: Optional[str] = Query(None, description="Поиск по названию компании"),
    filtration_parameters: List[Dict[str, Any]] = Body(default=[], description="Параметры фильтрации"),
    companies_repository: companies_repository_dep = None
) -> CompaniesResponse:
    """
    Получить список компаний, производящих товары (включая те, что делают оба)
    
    Args:
        page: Номер страницы (начиная с 1)
        per_page: Количество элементов на странице (1-100)
        search: Поиск по названию компании
        filtration_parameters: Список словарей с параметрами фильтрации
        companies_repository: Репозиторий компаний
        
    Returns:
        CompaniesResponse: Список компаний с информацией о пагинации
    """
    print(f"Параметры фильтрации для товаров: {filtration_parameters}")
    
    companies, total_count = await companies_repository.get_product_companies(
        page=page,
        per_page=per_page,
        search=search
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


@router.get("/slug/{company_slug}/statistics")
async def get_company_statistics(
        company_slug: str,
        companies_repository: companies_repository_dep
) -> CompanyStatisticsResponse:
    """
    Получить статистику компании по её slug

    Args:
        company_slug: Slug компании

    Returns:
        CompanyStatisticsResponse: Статистика компании
    """
    company = await companies_repository.get_company_by_slug(
        company_slug=company_slug, 
        include_products=True
    )

    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    
    return CompanyStatisticsResponse(
        total_products=len(company.products),
        total_views=company.total_views,
        monthly_views=company.monthly_views,
        total_purchases=company.total_purchases,
        registration_date=company.registration_date
    )
@router.get("/slug/{company_slug}")
async def get_company_by_id(
        company_slug: str,
        short: bool = Query(False, description="Возвращать только краткую информацию"),
        companies_repository: companies_repository_dep = None
) -> ShortCompanyResponse | CompanyResponse:
    """
    Получить информацию о компании по её slug

    Args:
        company_id: ID компании
        short: Если True, возвращает только название и логотип компании
        companies_repository: Репозиторий компаний

    Returns:
        CompanyResponse: Полная или краткая информация о компании
    """
    company = await companies_repository.get_company_by_slug(company_slug)

    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    if short:
        return ShortCompanyResponse.model_validate(company)
    else:
        return CompanyResponse.model_validate(company)


@router.get("/{company_id}")
async def get_company_by_id(
        company_id: int,
        short: bool = Query(False, description="Возвращать только краткую информацию"),
        companies_repository: companies_repository_dep = None
) -> ShortCompanyResponse | CompanyResponse:
    """
    Получить информацию о компании по её slug

    Args:
        company_id: ID компании
        short: Если True, возвращает только название и логотип компании
        companies_repository: Репозиторий компаний

    Returns:
        CompanyResponse: Полная или краткая информация о компании
    """
    company = await companies_repository.get_company_by_id(company_id=company_id)

    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    if short:
        return ShortCompanyResponse.model_validate(company)
    else:
        return CompanyResponse.model_validate(company)

