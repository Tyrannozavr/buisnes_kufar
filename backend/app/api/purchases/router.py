from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query, status, Path, Body
from pydantic import BaseModel, Field

from app.db.dependencies import async_db_dep
from app.api.authentication.dependencies import get_current_user
from app.api.authentication.models.user import User
from app.api.purchases.dependencies import deal_service_dep_annotated
from app.api.purchases.services import DealService
from app.api.purchases.schemas import (
    DealCreate, DealUpdate, DealResponse, DealListResponse,
    BuyerDealResponse, SellerDealResponse, DocumentUpload,
    CheckoutRequest, CheckoutItem,
    DocumentNumberDateRequest, BillResponse, ContractResponse, SupplyContractResponse
)
from app.api.purchases.schemas import DealStatus, ItemType

router = APIRouter(
    tags=["purchases", "orders", "deals", "documents", "business"]
)


@router.post("/deals", response_model=DealResponse, tags=["deals", "orders", "create"])
async def create_deal(
    deal_data: DealCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: deal_service_dep_annotated
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
    
    try:
        deal = await deal_service.create_deal(deal_data, company.id)
        if not deal:
            raise HTTPException(status_code=400, detail="Failed to create deal")
        return deal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/buyer/deals", response_model=List[BuyerDealResponse], tags=["buyer", "orders", "list"])
async def get_buyer_deals(
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: deal_service_dep_annotated,
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
            supplier_name=deal.seller_company.name if deal.seller_company else "Unknown",
            supplier_inn=deal.seller_company.inn if deal.seller_company else None,
            supplier_phone=deal.seller_company.phone if deal.seller_company else None
        ))
    
    return buyer_deals


@router.get("/seller/deals", response_model=List[SellerDealResponse], tags=["seller", "orders", "list"])
async def get_seller_deals(
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: deal_service_dep_annotated,
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
            buyer_name=deal.buyer_company.name if deal.buyer_company else "Unknown",
            buyer_inn=deal.buyer_company.inn if deal.buyer_company else None,
            buyer_phone=deal.buyer_company.phone if deal.buyer_company else None
        ))
    
    return seller_deals


@router.get("/deals/{deal_id}", response_model=DealResponse, tags=["deals", "orders", "detail"])
async def get_deal(
    deal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: deal_service_dep_annotated
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
    deal_service: deal_service_dep_annotated
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


class DeleteDealResponse(BaseModel):
    """Схема ответа при удалении сделки"""
    message: str = "Deal deleted successfully"
    deal_id: int


@router.delete(
    "/deals/{deal_id}",
    response_model=DeleteDealResponse,
    status_code=status.HTTP_200_OK,
    tags=["deals", "orders", "delete"],
    summary="Удаление заказа",
    description="""
    Удаление заказа по ID.
    
    **Доступ:** Только для участников сделки (покупателя или продавца)
    
    **Действия при удалении:**
    - Удаляется сам заказ
    - Каскадно удаляются все позиции заказа (order_items)
    - Каскадно удаляется история изменений заказа (order_history)
    
    **Ошибки:**
    - `404` - Заказ не найден или у пользователя нет доступа
    - `404` - Компания пользователя не найдена
    """,
    responses={
        200: {
            "description": "Заказ успешно удален",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Deal deleted successfully",
                        "deal_id": 123
                    }
                }
            }
        },
        404: {
            "description": "Заказ не найден или доступ запрещен",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Deal not found or access denied"
                    }
                }
            }
        }
    }
)
async def delete_deal(
    deal_id: int = Path(..., description="ID сделки для удаления", example=123, gt=0),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...
):
    """
    Удаление заказа
    
    Удаляет заказ по ID. Доступно только для участников сделки (покупателя или продавца).
    При удалении также удаляются все связанные позиции заказа и история изменений.
    """
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found for this user"
        )
    
    deleted = await deal_service.delete_deal(deal_id, company.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found or access denied"
        )
    
    return DeleteDealResponse(message="Deal deleted successfully", deal_id=deal_id)


@router.post("/deals/{deal_id}/documents", tags=["documents", "upload", "files"])
async def upload_document(
    deal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: deal_service_dep_annotated,
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


@router.post(
    "/deals/{deal_id}/bill",
    response_model=BillResponse,
    tags=["bill"],
    summary="Создать номер и дату счета",
    responses={
        200: {"description": "Номер и дата счета успешно присвоены заказу"},
        404: {"description": "Заказ не найден или доступ запрещен"},
    },
)
async def create_bill(
    deal_id: int,
    body: DocumentNumberDateRequest | None = Body(default=None),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...
):
    """
    Генерирует и присваивает номер счета и дату заказу.
    Номер: маска 00001, ежегодное обнуление. Дата — из body или текущая.
    """
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    result = await deal_service.assign_bill(deal_id, company.id, body.date if (body and body.date) else None)
    if not result:
        raise HTTPException(status_code=404, detail="Deal not found or access denied")
    return BillResponse(bill_number=result[0], bill_date=result[1])


@router.post(
    "/deals/{deal_id}/contract",
    response_model=ContractResponse,
    tags=["contract"],
    summary="Создать номер и дату договора",
    responses={
        200: {"description": "Номер и дата договора успешно присвоены заказу"},
        404: {"description": "Заказ не найден или доступ запрещен"},
    },
)
async def create_contract(
    deal_id: int,
    body: DocumentNumberDateRequest | None = Body(default=None),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...
):
    """
    Генерирует и присваивает номер договора и дату заказу.
    Номер: маска 00001, ежегодное обнуление. Дата — из body или текущая.
    """
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    result = await deal_service.assign_contract(deal_id, company.id, body.date if (body and body.date) else None)
    if not result:
        raise HTTPException(status_code=404, detail="Deal not found or access denied")
    return ContractResponse(contract_number=result[0], contract_date=result[1])


@router.post(
    "/deals/{deal_id}/supply-contract",
    response_model=SupplyContractResponse,
    tags=["supply-contract"],
    summary="Создать номер и дату договора поставки",
    responses={
        200: {"description": "Номер и дата договора поставки успешно присвоены заказу"},
        404: {"description": "Заказ не найден или доступ запрещен"},
    },
)
async def create_supply_contract(
    deal_id: int,
    body: DocumentNumberDateRequest | None = Body(default=None),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...
):
    """
    Генерирует и присваивает номер и дату договора поставки заказу.
    Номер: маска 00001, ежегодное обнуление. Дата — из body или текущая.
    """
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    result = await deal_service.assign_supply_contract(deal_id, company.id, body.date if (body and body.date) else None)
    if not result:
        raise HTTPException(status_code=404, detail="Deal not found or access denied")
    return SupplyContractResponse(supply_contracts_number=result[0], supply_contracts_date=result[1])


@router.post("/checkout", response_model=DealResponse, tags=["checkout", "orders", "create"])
async def create_order_from_checkout(
    checkout_data: CheckoutRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: deal_service_dep_annotated
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
    deal_service: deal_service_dep_annotated
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
