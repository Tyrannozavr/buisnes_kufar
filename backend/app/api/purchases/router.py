from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query

from app.db.dependencies import async_db_dep
from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.purchases.dependencies import deal_service_dep
from app.api.purchases.services import DealService
from app.api.purchases.schemas import (
    DealCreate, DealUpdate, DealResponse, DealListResponse, 
    BuyerDealResponse, SellerDealResponse, DocumentUpload,
    CheckoutRequest, CheckoutItem
)
from app.api.purchases.schemas import DealStatus, ItemType

router = APIRouter(
    tags=["purchases", "orders", "deals", "documents", "business"]
)


@router.post("/deals", response_model=DealResponse, tags=["deals", "orders", "create"])
async def create_deal(
    deal_data: DealCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: Annotated[DealService, Depends(deal_service_dep)]
):
    """
    Создание нового заказа
    
    Создает новую сделку между покупателем (текущий пользователь) и продавцом.
    Автоматически генерируются номера заказов для обеих сторон.
    """
    # Получаем компанию пользователя
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    
    deal = await deal_service.create_deal(deal_data, company.id)
    if not deal:
        raise HTTPException(status_code=400, detail="Failed to create deal")
    
    return deal


@router.get("/buyer/deals", response_model=List[BuyerDealResponse], tags=["buyer", "orders", "list"])
async def get_buyer_deals(
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: Annotated[DealService, Depends(deal_service_dep)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Получение заказов покупателя
    
    Возвращает список всех заказов, где текущий пользователь является покупателем.
    Включает информацию о поставщиках и статусах заказов.
    """
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    
    deals, total = await deal_service.get_buyer_deals(company.id, skip, limit)
    
    # Преобразуем в формат для покупателя
    buyer_deals = []
    for deal in deals:
        buyer_deals.append(BuyerDealResponse(
            id=deal.id,
            buyer_company_id=deal.buyer_company_id,
            seller_company_id=deal.seller_company_id,
            buyer_order_number=deal.buyer_order_number,
            seller_order_number=deal.seller_order_number,
            status=deal.status,
            deal_type=deal.deal_type,
            total_amount=deal.total_amount,
            created_at=deal.created_at,
            updated_at=deal.updated_at,
            supplier_name=deal.seller_company.short_name if deal.seller_company else "Unknown",
            supplier_inn=deal.seller_company.inn if deal.seller_company else None,
            supplier_phone=deal.seller_company.phone if deal.seller_company else None
        ))
    
    return buyer_deals


@router.get("/seller/deals", response_model=List[SellerDealResponse], tags=["seller", "orders", "list"])
async def get_seller_deals(
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: Annotated[DealService, Depends(deal_service_dep)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Получение заказов продавца
    
    Возвращает список всех заказов, где текущий пользователь является продавцом.
    Включает информацию о покупателях и статусах заказов.
    """
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    
    deals, total = await deal_service.get_seller_deals(company.id, skip, limit)
    
    # Преобразуем в формат для продавца
    seller_deals = []
    for deal in deals:
        seller_deals.append(SellerDealResponse(
            id=deal.id,
            buyer_company_id=deal.buyer_company_id,
            seller_company_id=deal.seller_company_id,
            buyer_order_number=deal.buyer_order_number,
            seller_order_number=deal.seller_order_number,
            status=deal.status,
            deal_type=deal.deal_type,
            total_amount=deal.total_amount,
            created_at=deal.created_at,
            updated_at=deal.updated_at,
            buyer_name=deal.buyer_company.short_name if deal.buyer_company else "Unknown",
            buyer_inn=deal.buyer_company.inn if deal.buyer_company else None,
            buyer_phone=deal.buyer_company.phone if deal.buyer_company else None
        ))
    
    return seller_deals


@router.get("/deals/{deal_id}", response_model=DealResponse, tags=["deals", "orders", "detail"])
async def get_deal(
    deal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: Annotated[DealService, Depends(deal_service_dep)]
):
    """
    Получение конкретного заказа
    
    Возвращает детальную информацию о заказе включая все позиции и документы.
    Доступ только для участников сделки (покупателя или продавца).
    """
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    
    deal = await deal_service.get_deal_by_id(deal_id, company.id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return deal


@router.put("/deals/{deal_id}", response_model=DealResponse, tags=["deals", "orders", "update"])
async def update_deal(
    deal_id: int,
    deal_data: DealUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: Annotated[DealService, Depends(deal_service_dep)]
):
    """
    Обновление заказа
    
    Позволяет изменить статус, комментарии или позиции заказа.
    Все изменения записываются в историю и уведомляют контрагента.
    """
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    
    deal = await deal_service.update_deal(deal_id, deal_data, company.id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found or access denied")
    
    return deal


@router.post("/deals/{deal_id}/documents", tags=["documents", "upload", "files"])
async def upload_document(
    deal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: Annotated[DealService, Depends(deal_service_dep)],
    document_type: str = Form(...),
    document_number: str = Form(None),
    document_date: str = Form(None),
    description: str = Form(None),
    file: UploadFile = File(...)
):
    """
    Загрузка документа к заказу
    
    Позволяет прикрепить документ (счет, договор, акт, счет-фактура и т.д.) к заказу.
    Поддерживает различные типы файлов и автоматически определяет размер.
    """
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    
    # Проверяем права доступа к заказу
    deal = await deal_service.get_deal_by_id(deal_id, company.id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found or access denied")
    
    # Сохраняем файл (здесь нужно реализовать логику сохранения файлов)
    # Пока заглушка
    file_path = f"uploads/deals/{deal_id}/{file.filename}"
    
    from app.api.purchases.schemas import DocumentUpload
    from datetime import datetime
    
    document_data = DocumentUpload(
        document_type=document_type,
        document_number=document_number,
        document_date=datetime.fromisoformat(document_date) if document_date else None,
        description=description
    )
    
    document = await deal_service.add_document(deal_id, document_data, file_path, company.id)
    if not document:
        raise HTTPException(status_code=400, detail="Failed to add document")
    
    return {"message": "Document uploaded successfully", "document_id": document.id}


@router.post("/checkout", response_model=DealResponse, tags=["checkout", "orders", "create"])
async def create_order_from_checkout(
    checkout_data: CheckoutRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: Annotated[DealService, Depends(deal_service_dep)]
):
    """
    Создание заказа из корзины
    
    Создает заказы на основе данных корзины. Автоматически группирует товары по продавцам
    и создает отдельные заказы для каждого продавца.
    """
    # Получаем компанию пользователя
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    
    # Преобразуем данные корзины в формат для сервиса
    checkout_dict = {
        "items": [item.dict() for item in checkout_data.items],
        "comments": checkout_data.comments
    }
    
    deal = await deal_service.create_deal_from_checkout(checkout_dict, company.id)
    if not deal:
        raise HTTPException(status_code=400, detail="Failed to create order from checkout")
    
    return deal


@router.get("/units", response_model=List[dict], tags=["units", "measurement"])
async def get_units_of_measurement(
    deal_service: Annotated[DealService, Depends(deal_service_dep)]
):
    """
    Получение единиц измерения с кодами ОКЕИ
    
    Возвращает список всех доступных единиц измерения с их кодами по ОКЕИ.
    """
    units = await deal_service.get_units_of_measurement()
    return [
        {
            "id": unit.id,
            "name": unit.name,
            "symbol": unit.symbol,
            "code": unit.code
        }
        for unit in units
    ]
