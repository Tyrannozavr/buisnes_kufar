from typing import Optional, Any, List, Dict

from fastapi import APIRouter, Query, HTTPException, Body

from app.api.companies.dependencies import companies_repository_dep
from app.api.companies.schemas.companies import CompaniesResponse, PaginationInfo
from app.api.company.schemas.company import CompanyResponse, ShortCompanyResponse, CompanyStatisticsResponse
from app.api.company.schemas.filters import CompanyFilterRequest

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


@router.get("/", response_model=CompaniesResponse)
async def get_all_companies(
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
        search: Optional[str] = Query(None, description="Поиск по названию компании"),
        cities: Optional[str] = Query(None, description="Фильтр по городам (через запятую)"),
        companies_repository: companies_repository_dep = None
) -> CompaniesResponse:
    """
    Получить список всех активных компаний с фильтрацией
    
    Args:
        page: Номер страницы (начиная с 1)
        per_page: Количество элементов на странице (1-100)
        search: Поиск по названию компании
        cities: ID городов через запятую
        companies_repository: Репозиторий компаний
        
    Returns:
        CompaniesResponse: Список компаний с информацией о пагинации
    """
    # Parse cities parameter
    cities_list = None
    if cities:
        try:
            cities_list = [int(c.strip()) for c in cities.split(',')]
        except ValueError:
            pass

    companies, total_count = await companies_repository.get_companies_with_filters(
        page=page,
        per_page=per_page,
        search=search,
        cities=cities_list
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
        search: Optional[str] = Query(None, description="Поиск по названию компании"),
        cities: Optional[str] = Query(None, description="Фильтр по городам (через запятую)"),
        companies_repository: companies_repository_dep = None
) -> CompaniesResponse:
    """
    Получить список компаний, предоставляющих услуги (включая те, что делают оба)
    
    Args:
        page: Номер страницы (начиная с 1)
        per_page: Количество элементов на странице (1-100)
        search: Поиск по названию компании
        cities: ID городов через запятую
        companies_repository: Репозиторий компаний
        
    Returns:
        CompaniesResponse: Список компаний с информацией о пагинации
    """
    # Parse cities parameter
    cities_list = None
    if cities:
        try:
            cities_list = [int(c.strip()) for c in cities.split(',')]
        except ValueError:
            pass

    companies, total_count = await companies_repository.get_companies_with_filters(
        page=page,
        per_page=per_page,
        search=search,
        cities=cities_list
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
        cities: Optional[str] = Query(None, description="Фильтр по городам (через запятую)"),
        companies_repository: companies_repository_dep = None
) -> CompaniesResponse:
    """
    Получить список компаний, производящих товары (включая те, что делают оба)
    
    Args:
        page: Номер страницы (начиная с 1)
        per_page: Количество элементов на странице (1-100)
        search: Поиск по названию компании
        cities: ID городов через запятую
        companies_repository: Репозиторий компаний
        
    Returns:
        CompaniesResponse: Список компаний с информацией о пагинации
    """
    # Parse cities parameter
    cities_list = None
    if cities:
        try:
            cities_list = [int(c.strip()) for c in cities.split(',')]
        except ValueError:
            pass

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 Router: get_product_companies called with cities_list={cities_list}")
    
    companies, total_count = await companies_repository.get_product_companies(
        page=page,
        per_page=per_page,
        search=search,
        cities=cities_list
    )
    
    logger.info(f"✅ Found {total_count} companies")

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


@router.post("/search", tags=["search"])
async def search_companies_with_filters(
        filter_request: CompanyFilterRequest,
        companies_repository: companies_repository_dep = None
):
    """
    POST endpoint для поиска компаний с фильтрацией (аналог /products/search)
    
    Args:
        filter_request: Параметры фильтрации компаний
        
    Returns:
        CompaniesResponse: Список компаний с пагинацией
    """
    from sqlalchemy import select, func, and_, or_
    from app.api.company.models.company import Company, BusinessType, TradeActivity
    from sqlalchemy.orm import selectinload
    
    # Базовые условия
    conditions = [Company.is_active == True]
    
    # Фильтр по поиску: название, полное имя, ИНН, город (частичное совпадение)
    if filter_request.search:
        q = f"%{filter_request.search.strip()}%"
        conditions.append(
            or_(
                Company.name.ilike(q),
                Company.full_name.ilike(q),
                Company.inn.ilike(q),
                Company.city.ilike(q),
            )
        )
    
    # Фильтр по городам
    if filter_request.cities:
        from app.api.common.models.city import City
        cities_query = select(City.name).where(City.id.in_(filter_request.cities))
        cities_result = await companies_repository.session.execute(cities_query)
        city_names = [row[0] for row in cities_result]
        if city_names:
            conditions.append(Company.city.in_(city_names))
    
    # Фильтр по типу бизнеса (legacy)
    if filter_request.business_type == "goods":
        conditions.append(or_(
            Company.business_type == BusinessType.GOODS,
            Company.business_type == BusinessType.BOTH
        ))
    elif filter_request.business_type == "services":
        conditions.append(or_(
            Company.business_type == BusinessType.SERVICES,
            Company.business_type == BusinessType.BOTH
        ))
    
    # Фильтр по торговой деятельности (ТЗ_15 §5.2)
    ta = (filter_request.trade_activity or "").strip().lower()
    if ta in ("producer", "производитель"):
        conditions.append(Company.trade_activity == TradeActivity.PRODUCER)
    elif ta in ("seller", "продавец"):
        conditions.append(Company.trade_activity == TradeActivity.SELLER)
    elif ta in ("carrier", "перевозчик"):
        conditions.append(Company.trade_activity == TradeActivity.CARRIER)
    elif ta in ("forwarder", "экспедитор"):
        conditions.append(Company.trade_activity == TradeActivity.FORWARDER)
    elif ta in ("carriers", "перевозчики", "logistics"):
        conditions.append(
            Company.trade_activity.in_(
                [TradeActivity.CARRIER, TradeActivity.FORWARDER]
            )
        )
    
    # Базовый запрос
    base_query = select(Company).options(
        selectinload(Company.officials)
    ).where(and_(*conditions)).order_by(Company.registration_date.desc())
    
    # Подсчёт total
    count_query = select(func.count(Company.id)).where(and_(*conditions))
    count_result = await companies_repository.session.execute(count_query)
    total_count = count_result.scalar()
    
    # Применяем пагинацию
    offset = filter_request.skip
    paginated_query = base_query.offset(offset).limit(filter_request.limit)
    
    # Выполняем запрос
    result = await companies_repository.session.execute(paginated_query)
    companies = result.scalars().all()
    
    # Вычисляем общее количество страниц
    total_pages = (total_count + filter_request.limit - 1) // filter_request.limit
    
    return CompaniesResponse(
        data=list(companies),
        pagination=PaginationInfo(
            total=total_count,
            page=offset // filter_request.limit + 1,
            perPage=filter_request.limit,
            totalPages=total_pages
        )
    )


@router.post("/products/search", tags=["search"])
async def search_product_companies_with_filters(
        filter_request: CompanyFilterRequest,
        companies_repository: companies_repository_dep = None
):
    """
    POST: каталог «Производители» — компании с trade_activity = Производитель.
    """
    filter_request.trade_activity = filter_request.trade_activity or "producer"
    filter_request.business_type = None
    return await search_companies_with_filters(filter_request, companies_repository)


@router.post("/services/search", tags=["search"])
async def search_service_companies_with_filters(
        filter_request: CompanyFilterRequest,
        companies_repository: companies_repository_dep = None
):
    """
    POST: каталог «Перевозчики» — Перевозчик и Экспедитор.
    """
    filter_request.trade_activity = filter_request.trade_activity or "logistics"
    filter_request.business_type = None
    return await search_companies_with_filters(filter_request, companies_repository)


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
