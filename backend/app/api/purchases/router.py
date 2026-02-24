from typing import Annotated, List, Optional
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query, status, Path, Body
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, Field

from app.db.dependencies import async_db_dep
from app.core.config import settings
from app.api.authentication.dependencies import get_current_user
from app_logging.logger import logger
from app.api.authentication.models.user import User
from app.api.purchases.dependencies import deal_service_dep_annotated
from app.api.purchases.services import DealService
from app.api.purchases.schemas import (
    DealCreate, DealUpdate, DealResponse, DealListResponse,
    BuyerDealResponse, SellerDealResponse, DocumentUpload, DocumentResponse,
    CheckoutRequest, CheckoutItem,
    DocumentNumberDateRequest, BillResponse, ContractResponse, SupplyContractResponse,
    DocumentFormSaveRequest, DocumentFormResponse, DOCUMENT_FORM_TYPES,
    DealVersionItem,
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
            version=deal.version,
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
            version=deal.version,
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


@router.get(
    "/deals/{deal_id}",
    response_model=DealResponse,
    tags=["deals", "orders", "detail"],
    summary="Получение заказа по ID сделки",
    description="По умолчанию возвращается активная (согласованная обеими сторонами) версия. Параметр version — конкретная версия для просмотра/сравнения.",
    responses={
        200: {"description": "Возвращена версия сделки"},
        404: {"description": "Заказ не найден или компания пользователя не участвует в сделке"},
    },
)
async def get_deal(
    deal_id: int,
    version: Annotated[Optional[int], Query(description="Номер версии; если не указан — активная версия")] = None,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...,
):
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")

    deal = await deal_service.get_deal_by_id(deal_id, company.id, version=version)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return deal


@router.put(
    "/deals/{deal_id}",
    response_model=DealResponse,
    tags=["deals", "orders", "update"],
    summary="Обновление последней версии заказа",
    responses={
        200: {
            "description": "Последняя версия заказа успешно обновлена",
            "content": {
                "application/json": {
                    "example": {
                        "id": 321,
                        "version": 3,
                        "buyer_company_id": 10,
                        "seller_company_id": 20,
                        "buyer_order_number": "00042",
                        "seller_order_number": "00058",
                        "status": "Активная",
                        "deal_type": "Товары",
                        "total_amount": 246.9,
                        "comments": "updated latest version",
                        "items": [],
                        "created_at": "2026-02-19T10:00:00",
                        "updated_at": "2026-02-19T11:30:00"
                    }
                }
            }
        },
        403: {"description": "Доступ запрещён: компания пользователя не является покупателем или продавцом по этой сделке"},
        404: {"description": "Заказ не найден по указанному ID"},
        422: {"description": "Ошибка валидации тела запроса (DealUpdate)"},
    },
)
async def update_deal(
    deal_id: int,
    deal_data: DealUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: deal_service_dep_annotated
):
    """
    Обновление заказа по ID сделки.

    Обновляет только последнюю версию сделки (in-place), новую версию не создает.
    Позволяет изменить статус, комментарии или позиции заказа (поле **items** в формате **OrderItemUpdate**:
    допускаются `quantity >= 0`, `price >= 0`).
    Все изменения записываются в историю.
    """
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")

    order_exists = await deal_service.get_order_by_id_only(deal_id)
    if not order_exists:
        raise HTTPException(status_code=404, detail="Deal not found")

    try:
        deal = await deal_service.update_deal(deal_id, deal_data, company.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error updating deal %s: %s", deal_id, e)
        raise HTTPException(status_code=500, detail=str(e))

    if not deal:
        raise HTTPException(status_code=403, detail="Access denied: your company is not buyer or seller of this deal")
    return deal


class DeleteDealResponse(BaseModel):
    """Схема ответа при удалении сделки (все версии)."""
    message: str = "Deal versions deleted successfully"
    deal_id: int


@router.delete(
    "/deals/{deal_id}",
    response_model=DeleteDealResponse,
    status_code=status.HTTP_200_OK,
    tags=["deals", "orders", "delete"],
    summary="Удаление заказа (все версии)",
    description="""
    Удаление заказа по ID сделки (все версии).
    
    **Доступ:** Только для участников сделки (покупателя или продавца)
    
    **Действия при удалении:**
    - Удаляются все версии заказа
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
                        "message": "Deal versions deleted successfully",
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
    
    Удаляет все версии заказа по ID сделки. Доступно только для участников сделки
    (покупателя или продавца).
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
    
    return DeleteDealResponse(message="Deal versions deleted successfully", deal_id=deal_id)


@router.post(
    "/deals/{deal_id}/versions",
    response_model=DealResponse,
    tags=["deals", "orders", "versions", "create"],
    summary="Создание новой версии заказа",
    description="""
    Создает новую версию сделки на основе текущей последней версии.

    - `id` сделки остается неизменным
    - `version` увеличивается на 1
    - предыдущие версии сохраняются
    """,
    responses={
        200: {
            "description": "Новая версия сделки создана",
            "content": {
                "application/json": {
                    "example": {
                        "id": 321,
                        "version": 4,
                        "buyer_company_id": 10,
                        "seller_company_id": 20,
                        "buyer_order_number": "00042",
                        "seller_order_number": "00058",
                        "status": "Активная",
                        "deal_type": "Товары",
                        "total_amount": 246.9,
                        "comments": "copied from previous version",
                        "items": [],
                        "created_at": "2026-02-19T12:00:00",
                        "updated_at": "2026-02-19T12:00:00"
                    }
                }
            }
        },
        404: {"description": "Сделка не найдена или доступ запрещен"},
    },
)
async def create_new_deal_version(
    deal_id: int = Path(..., description="ID сделки", example=123, gt=0),
    deal_data: DealUpdate = Body(
        default_factory=DealUpdate,
        examples={
            "empty_body_copy_only": {
                "summary": "Создать новую версию без изменений",
                "value": {},
            },
            "copy_with_patch": {
                "summary": "Создать новую версию и обновить поля",
                "value": {
                    "comments": "Новая версия с изменениями",
                    "status": "Активная",
                },
            },
        },
    ),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...,
):
    """Создает новую версию сделки, не затрагивая предыдущие версии, и применяет поля из тела запроса."""
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")

    new_version_deal = await deal_service.create_new_deal_version(deal_id, company.id, deal_data)
    if not new_version_deal:
        raise HTTPException(status_code=404, detail="Deal not found or access denied")
    return new_version_deal


class DeleteLastVersionDealResponse(BaseModel):
    """Схема ответа при удалении последней версии сделки."""
    message: str = "Last deal version deleted successfully"
    deal_id: int
    deleted_version: int


@router.delete(
    "/deals/{deal_id}/versions/last",
    response_model=DeleteLastVersionDealResponse,
    status_code=status.HTTP_200_OK,
    tags=["deals", "orders", "versions", "delete"],
    summary="Удаление последней версии заказа",
    description="""
    Удаляет только последнюю версию сделки (`max(version)`).
    Другие версии с тем же `deal_id` сохраняются.
    """,
    responses={
        200: {
            "description": "Последняя версия сделки удалена",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Last deal version deleted successfully",
                        "deal_id": 321,
                        "deleted_version": 4
                    }
                }
            }
        },
        404: {"description": "Сделка не найдена или доступ запрещен"},
    },
)
async def delete_last_deal_version(
    deal_id: int = Path(..., description="ID сделки", example=123, gt=0),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...,
):
    """Удаляет только последнюю версию сделки."""
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")

    deleted_version = await deal_service.delete_last_deal_version(deal_id, company.id)
    if deleted_version is None:
        raise HTTPException(status_code=404, detail="Deal not found or access denied")

    return DeleteLastVersionDealResponse(
        deal_id=deal_id,
        deleted_version=deleted_version,
    )


@router.get(
    "/deals/{deal_id}/versions",
    response_model=List[DealVersionItem],
    tags=["deals", "orders", "versions", "list"],
    summary="Список всех версий заказа",
    description="Для выпадающего списка версий и сравнения. Версии не удаляются, только помечаются принятыми/отклонёнными.",
)
async def get_deal_versions(
    deal_id: int = Path(..., gt=0),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...,
):
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    versions = await deal_service.get_deal_versions(deal_id, company.id)
    if not versions and not await deal_service.has_deal_access(deal_id, company.id):
        raise HTTPException(status_code=404, detail="Deal not found or access denied")
    return versions


@router.post(
    "/deals/{deal_id}/versions/{version}/accept",
    response_model=DealResponse,
    tags=["deals", "orders", "versions"],
    summary="Принять версию заказа",
    description="Текущая сторона помечает версию как принятую. После принятия обеими сторонами версия становится активной.",
)
async def accept_deal_version(
    deal_id: int = Path(..., gt=0),
    version: int = Path(..., ge=1),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...,
):
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    deal = await deal_service.accept_deal_version(deal_id, version, company.id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal or version not found, or version already rejected")
    return deal


@router.post(
    "/deals/{deal_id}/versions/{version}/reject",
    response_model=DealResponse,
    tags=["deals", "orders", "versions"],
    summary="Отклонить версию заказа",
    description="Версия помечается как отклонённая текущей стороной. Версия не удаляется, остаётся в истории.",
)
async def reject_deal_version(
    deal_id: int = Path(..., gt=0),
    version: int = Path(..., ge=1),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...,
):
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    deal = await deal_service.reject_deal_version(deal_id, version, company.id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal or version not found")
    return deal


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
    Загрузка документа к заказу в S3.
    Требует настройки S3 (Cloudflare R2, MinIO или AWS S3).
    """
    if not settings.S3_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 storage is not configured. Set S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY (and optionally S3_ENDPOINT_URL for R2/MinIO).",
        )
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    deal = await deal_service.get_deal_by_id(deal_id, company.id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found or access denied")

    content = await file.read()
    from app.core.s3 import upload_document as s3_upload_document

    try:
        file_path = s3_upload_document(
            deal_id=deal_id,
            filename=file.filename or "document",
            content=content,
            content_type=file.content_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to upload file to storage: {e!s}",
        ) from e

    from app.api.purchases.schemas import DocumentUpload
    from datetime import datetime

    document_data = DocumentUpload(
        document_type=document_type,
        document_number=document_number if document_number and str(document_number).strip() else None,
        document_date=datetime.fromisoformat(document_date) if document_date else None,
        description=description,
    )
    try:
        document = await deal_service.add_document(deal_id, document_data, file_path, company.id)
    except Exception as e:
        logger.exception("Failed to add document to deal %s: %s", deal_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add document: {e!s}",
        ) from e
    if not document:
        raise HTTPException(status_code=400, detail="Failed to add document")
    return {"message": "Document uploaded successfully", "document_id": document.id}


@router.get(
    "/deals/{deal_id}/documents",
    response_model=List[DocumentResponse],
    tags=["documents", "list", "files"],
)
async def get_documents(
    deal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    deal_service: deal_service_dep_annotated,
):
    """Получить список документов заказа."""
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")

    has_access = await deal_service.has_deal_access(deal_id, company.id)
    if not has_access:
        raise HTTPException(status_code=404, detail="Deal not found or access denied")

    documents = await deal_service.get_documents(deal_id, company.id)

    # Возвращаем уже нормализованные DTO, чтобы избежать падений на сериализации ORM-объектов.
    return [
        DocumentResponse(
            document_id=doc.id,
            deal_id=deal_id,
            document_type=doc.document_type,
            document_number=doc.document_number if doc.document_number != "-" else None,
            document_date=doc.document_date.isoformat() if doc.document_date else None,
            document_file_path=doc.document_file_path,
            created_at=doc.created_at.isoformat() if doc.created_at else "",
            updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
        )
        for doc in documents
    ]


@router.get(
    "/deals/{deal_id}/documents/{document_id}/download",
    tags=["documents", "download", "files"],
    responses={
        200: {"description": "File content (stream=true) or JSON with url (stream=false)"},
        302: {"description": "Redirect to presigned URL (redirect=true)"},
        404: {"description": "Deal or document not found"},
        503: {"description": "S3 not configured"},
    },
)
async def download_document(
    deal_id: int,
    document_id: int,
    redirect: bool = Query(True, description="If true, redirect to URL"),
    stream: bool = Query(False, description="If true, stream file through backend (no presigned URL)"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...,
):
    """Скачать документ: stream=True — через backend, иначе presigned URL."""
    if not settings.S3_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 storage is not configured.",
        )
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    doc = await deal_service.get_document(deal_id, document_id, company.id)
    if not doc or not doc.document_file_path:
        raise HTTPException(status_code=404, detail="Document not found or has no file")

    if stream:
        import asyncio
        from app.core.s3 import get_document_content

        content, content_type = await asyncio.to_thread(
            get_document_content, doc.document_file_path
        )
        filename = doc.document_file_path.split("/")[-1] if "/" in doc.document_file_path else "document"
        return Response(
            content=content,
            media_type=content_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    from app.core.s3 import get_presigned_download_url

    url = get_presigned_download_url(doc.document_file_path)
    if redirect:
        return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
    return {"url": url}


@router.delete(
    "/deals/{deal_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["documents", "delete", "files"],
)
async def delete_document(
    deal_id: int,
    document_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...,
):
    """Удалить документ (файл в S3 и запись в БД)."""
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    doc = await deal_service.get_document(deal_id, document_id, company.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if settings.S3_ENABLED and doc.document_file_path:
        from app.core.s3 import delete_document as s3_delete_document

        try:
            s3_delete_document(doc.document_file_path)
        except Exception:
            pass
    deleted = await deal_service.delete_document(deal_id, document_id, company.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")


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


@router.get(
    "/deals/{deal_id}/documents/form",
    response_model=DocumentFormResponse,
    tags=["documents", "form", "editor"],
    summary="Получить JSON формы документа",
)
async def get_document_form(
    deal_id: int,
    document_type: str = Query(..., description="Тип документа: bill, supply_contract, contract, other"),
    version: str | None = Query(None, description="Версия (v1, v1.1); если не указана — последняя"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...,
):
    """Возвращает сохранённый payload формы документа для редактора (Счет, Договор поставки и т.д.)."""
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    if document_type not in DOCUMENT_FORM_TYPES:
        raise HTTPException(status_code=400, detail=f"document_type must be one of: {DOCUMENT_FORM_TYPES}")
    form = await deal_service.get_document_form(deal_id, company.id, document_type, version)
    if form is None:
        return DocumentFormResponse(payload={}, document_version="v1", updated_at=None, updated_by_company_id=None)
    return form


@router.put(
    "/deals/{deal_id}/documents/form",
    response_model=DocumentFormResponse,
    tags=["documents", "form", "editor"],
    summary="Сохранить JSON формы документа",
)
async def save_document_form(
    deal_id: int,
    body: DocumentFormSaveRequest,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    deal_service: deal_service_dep_annotated = ...,
):
    """Сохраняет payload формы документа (версионирование: v1, v1.1 и т.д.)."""
    company = await deal_service.get_company_by_user_id(current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for this user")
    if body.document_type not in DOCUMENT_FORM_TYPES:
        raise HTTPException(status_code=400, detail=f"document_type must be one of: {DOCUMENT_FORM_TYPES}")
    try:
        return await deal_service.save_document_form(
            deal_id, company.id, body.document_type, body.payload, body.version
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


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
