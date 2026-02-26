from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator
from enum import Enum


class DealStatus(str, Enum):
    ACTIVE = "Активная"
    COMPLETED = "Завершенная"


class ItemType(str, Enum):
    GOODS = "Товары"
    SERVICES = "Услуги"


class OrderItemBase(BaseModel):
    """Базовая схема для позиции заказа"""
    product_name: str = Field(..., description="Наименование товара/услуги")
    product_slug: Optional[str] = Field(None, description="Slug продукта")
    product_description: Optional[str] = Field(None, description="Описание продукта")
    product_article: Optional[str] = Field(None, description="Артикул")
    product_type: Optional[str] = Field(None, description="Тип продукта")
    logo_url: Optional[str] = Field(None, description="URL логотипа")
    quantity: float = Field(..., gt=0, description="Количество")
    unit_of_measurement: str = Field(..., description="Единица измерения")
    price: float = Field(..., gt=0, description="Цена за единицу")
    position: int = Field(..., ge=1, description="Позиция в заказе")

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    """Схема для создания позиции заказа
    
    Два варианта использования:
    1. С article: указывайте только article и quantity, остальные данные берутся из БД
    2. Без article: указывайте все поля вручную (product_name, price, unit_of_measurement обязательны)
    """
    article: Optional[str] = Field(
        None, 
        description="Артикул продукта из каталога. Если указан, остальные данные (название, цена, единица измерения) берутся из БД автоматически"
    )
    quantity: float = Field(..., gt=0, description="Количество")
    
    # Поля для ручного ввода (используются только если article не указан)
    product_name: Optional[str] = Field(
        None, 
        description="Наименование товара/услуги. Обязательно, если article не указан"
    )
    product_slug: Optional[str] = Field(None, description="Slug продукта")
    product_description: Optional[str] = Field(None, description="Описание продукта")
    product_article: Optional[str] = Field(None, description="Артикул")
    product_type: Optional[str] = Field(None, description="Тип продукта")
    logo_url: Optional[str] = Field(None, description="URL логотипа")
    unit_of_measurement: Optional[str] = Field(
        None, 
        description="Единица измерения. Обязательно, если article не указан"
    )
    price: Optional[float] = Field(
        None, 
        gt=0, 
        description="Цена за единицу. Обязательно, если article не указан"
    )
    position: Optional[int] = Field(
        None, 
        ge=1, 
        description="Позиция в заказе (автоматически, если не указана)"
    )
    
    @model_validator(mode='after')
    def validate_required_fields(self):
        """Валидация: если article не указан, обязательны product_name, price, unit_of_measurement"""
        if not self.article:
            if not self.product_name:
                raise ValueError("product_name is required when article is not specified")
            if not self.price:
                raise ValueError("price is required when article is not specified")
            if not self.unit_of_measurement:
                raise ValueError("unit_of_measurement is required when article is not specified")
        return self
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "examples": [
                {
                    "article": "ART-123",
                    "quantity": 2
                },
                {
                    "article": None,
                    "quantity": 1,
                    "product_name": "Кастомный товар",
                    "price": 100.0,
                    "unit_of_measurement": "шт"
                }
            ]
        }


class OrderItemUpdate(BaseModel):
    """Схема позиции заказа для обновления (допускает quantity/price >= 0)."""
    article: Optional[str] = Field(None, description="Артикул продукта из каталога")
    quantity: float = Field(..., ge=0, description="Количество")
    product_name: Optional[str] = Field(None, description="Наименование товара/услуги")
    product_slug: Optional[str] = Field(None, description="Slug продукта")
    product_description: Optional[str] = Field(None, description="Описание продукта")
    product_article: Optional[str] = Field(None, description="Артикул")
    product_type: Optional[str] = Field(None, description="Тип продукта")
    logo_url: Optional[str] = Field(None, description="URL логотипа")
    unit_of_measurement: Optional[str] = Field(None, description="Единица измерения")
    price: Optional[float] = Field(None, ge=0, description="Цена за единицу")

    @model_validator(mode='after')
    def validate_required_fields(self):
        """Если article не указан, обязательны product_name, price (может быть 0), unit_of_measurement."""
        if not self.article:
            if not self.product_name:
                raise ValueError("product_name is required when article is not specified")
            if self.price is None:
                raise ValueError("price is required when article is not specified")
            if not self.unit_of_measurement:
                raise ValueError("unit_of_measurement is required when article is not specified")
        return self

    class Config:
        from_attributes = True


class OrderItemResponse(OrderItemBase):
    """Схема для ответа с позицией заказа (price/quantity могут быть 0)."""
    id: int
    order_id: int
    amount: float = Field(..., description="Сумма (quantity * price)")
    created_at: datetime
    updated_at: datetime
    # В ответе допускаем 0 (в отличие от создания)
    quantity: float = Field(..., ge=0)
    price: float = Field(..., ge=0)

    class Config:
        from_attributes = True


class DealCreate(BaseModel):
    """Схема для создания заказа
    
    Тип заказа (deal_type) обязателен. Проверяется соответствие всех продуктов указанному типу.
    Запрещено смешивать товары и услуги в одном заказе.
    """
    seller_company_id: int = Field(..., description="ID компании-продавца")
    deal_type: ItemType = Field(..., description="Тип заказа (товары/услуги). Все продукты должны соответствовать этому типу")
    items: List[OrderItemCreate] = Field(..., min_items=1, description="Позиции заказа")
    comments: Optional[str] = Field(None, description="Комментарии к заказу")

    class Config:
        from_attributes = True


class DealUpdate(BaseModel):
    """Схема для обновления заказа (PUT /deals/{deal_id}). Все поля опциональны. items — в формате OrderItemUpdate (допускаются quantity, price >= 0)."""
    status: Optional[DealStatus] = Field(None, description="Статус заказа")
    items: Optional[List[OrderItemUpdate]] = Field(None, description="Обновлённые позиции (OrderItemUpdate: quantity >= 0, price >= 0)")
    comments: Optional[str] = Field(None, description="Комментарии")
    contract_number: Optional[str] = Field(None, description="Номер договора")
    bill_number: Optional[str] = Field(None, description="Номер счета на оплату")
    bill_date: Optional[datetime] = Field(None, description="Дата счета на оплату")
    supply_contracts_number: Optional[str] = Field(None, description="Номер договора поставки")
    supply_contracts_date: Optional[datetime] = Field(None, description="Дата договора поставки")
    buyer_order_date: Optional[datetime] = Field(None, description="Дата заказа покупателя")
    seller_order_date: Optional[datetime] = Field(None, description="Дата заказа продавца")

    class Config:
        from_attributes = True


class CompanyInDealResponse(BaseModel):
    """Схема компании в контексте сделки"""
    id: int = Field(..., description="ID компании")
    company_name: str = Field(..., description="Название компании")
    name: str = Field(..., description="Имя владельца компании")
    slug: str = Field(..., description="Slug компании")
    inn: Optional[str] = Field(None, description="ИНН компании")
    phone: str = Field(..., description="Телефон компании")
    email: str = Field(..., description="Email компании")
    legal_address: str = Field(..., description="Юридический адрес компании")

    class Config:
        from_attributes = True


class DealResponse(BaseModel):
    """Полная схема заказа для ответа"""
    id: int
    version: int = Field(..., description="Версия сделки (1..N), где N — последняя версия")
    buyer_company_id: int
    seller_company_id: int
    buyer_order_number: str
    seller_order_number: str
    status: DealStatus
    deal_type: ItemType
    total_amount: float
    comments: Optional[str]
    buyer_order_date: Optional[datetime] = None
    seller_order_date: Optional[datetime] = None
    contract_number: Optional[str] = None
    contract_date: Optional[datetime] = None
    bill_number: Optional[str] = None
    bill_date: Optional[datetime] = None
    supply_contracts_number: Optional[str] = None
    supply_contracts_date: Optional[datetime] = None
    closing_documents: List[Any] = Field(default_factory=list, description="Закрывающие документы (пока пустой список)")
    others_documents: List[Any] = Field(default_factory=list, description="Прочие документы (пока пустой список)")
    created_at: datetime
    updated_at: datetime

    # Согласование версии
    version_status: Optional[str] = Field(None, description="accepted | pending | rejected")
    proposed_by_company_id: Optional[int] = None
    buyer_accepted_at: Optional[datetime] = None
    seller_accepted_at: Optional[datetime] = None
    rejected_by_company_id: Optional[int] = None

    # Связанные данные
    items: List[OrderItemResponse] = Field(default_factory=list)
    buyer_company: Optional[CompanyInDealResponse] = Field(None, description="Информация о компании-покупателе")
    seller_company: Optional[CompanyInDealResponse] = Field(None, description="Информация о компании-продавце")

    class Config:
        from_attributes = True


class DealVersionItem(BaseModel):
    """Элемент списка версий заказа (для dropdown и сравнения)."""
    version: int
    version_status: str = Field(..., description="accepted | pending | rejected")
    proposed_by_company_id: Optional[int] = None
    buyer_accepted_at: Optional[datetime] = None
    seller_accepted_at: Optional[datetime] = None
    rejected_by_company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class BuyerDealResponse(BaseModel):
    """Схема заказа для покупателя"""
    id: int
    version: int = Field(..., description="Текущая версия сделки в списке")
    buyer_company_id: int
    seller_company_id: int
    buyer_order_number: str
    seller_order_number: str
    status: DealStatus
    deal_type: ItemType
    total_amount: float
    created_at: datetime
    updated_at: datetime
    
    # Информация о поставщике
    supplier_name: str
    supplier_inn: Optional[str]
    supplier_phone: Optional[str]

    class Config:
        from_attributes = True


class SellerDealResponse(BaseModel):
    """Схема заказа для продавца"""
    id: int
    version: int = Field(..., description="Текущая версия сделки в списке")
    buyer_company_id: int
    seller_company_id: int
    buyer_order_number: str
    seller_order_number: str
    status: DealStatus
    deal_type: ItemType
    total_amount: float
    created_at: datetime
    updated_at: datetime
    
    # Информация о покупателе
    buyer_name: str
    buyer_inn: Optional[str]
    buyer_phone: Optional[str]

    class Config:
        from_attributes = True


class DealListResponse(BaseModel):
    """Схема для списка заказов"""
    deals: List[DealResponse]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class DocumentNumberDateRequest(BaseModel):
    """Опциональная дата для генерации номера документа."""
    date: Optional[datetime] = Field(None, description="Дата документа (если не указана — текущая дата)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "examples": [
                {},
                {"date": "2026-02-11T12:00:00"},
            ]
        }


class BillResponse(BaseModel):
    """Ответ: номер и дата счета."""
    bill_number: str
    bill_date: datetime

    class Config:
        from_attributes = True


class ContractResponse(BaseModel):
    """Ответ: номер и дата договора."""
    contract_number: str
    contract_date: datetime

    class Config:
        from_attributes = True


class SupplyContractResponse(BaseModel):
    """Ответ: номер и дата договора поставки."""
    supply_contracts_number: str
    supply_contracts_date: datetime

    class Config:
        from_attributes = True


class DocumentUpload(BaseModel):
    """Схема для загрузки документа"""
    document_type: str = Field(..., description="Тип документа (invoice, contract, act, etc.)")
    document_number: Optional[str] = Field(None, description="Номер документа")
    document_date: Optional[datetime] = Field(None, description="Дата документа")
    description: Optional[str] = Field(None, description="Описание документа")

    class Config:
        from_attributes = True


# Типы документов для форм (редактор): bill, supply_contract, order, contract, other
DOCUMENT_FORM_TYPES = ("order", "bill", "supply_contract", "contract", "other")


class DocumentFormSaveRequest(BaseModel):
    """Тело запроса на сохранение JSON-формы документа (Счет, Договор поставки и т.д.)."""
    document_type: str = Field(..., description="Тип документа: bill, supply_contract, contract, other")
    payload: Dict[str, Any] = Field(default_factory=dict, description="JSON с полями формы")
    version: Optional[str] = Field(None, description="Версия (v1, v1.1 и т.д.); если не указана — используется текущая/последняя")


class DocumentFormResponse(BaseModel):
    """Ответ API: форма документа (payload) + метаданные версии."""
    payload: Dict[str, Any] = Field(default_factory=dict)
    document_version: str = Field(default="v1", description="Версия (v1, v1.1, …)")
    updated_at: Optional[datetime] = None
    updated_by_company_id: Optional[int] = None

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Схема документа в ответе API (поля соответствуют DocumentApiItem на фронте)."""
    document_id: int
    deal_id: int
    document_type: str
    document_number: Optional[str] = None
    document_date: Optional[str] = None
    document_file_path: Optional[str] = None
    created_at: str
    updated_at: str

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Маппинг OrderDocument -> DocumentResponse."""
        if hasattr(obj, "id") and hasattr(obj, "order_row_id"):
            doc_num = obj.document_number if obj.document_number != "-" else None
            deal_id = obj.order.id if getattr(obj, "order", None) else obj.order_row_id
            return super().model_validate(
                {
                    "document_id": obj.id,
                    "deal_id": deal_id,
                    "document_type": obj.document_type,
                    "document_number": doc_num,
                    "document_date": obj.document_date.isoformat() if obj.document_date else None,
                    "document_file_path": obj.document_file_path,
                    "created_at": obj.created_at.isoformat() if obj.created_at else "",
                    "updated_at": obj.updated_at.isoformat() if obj.updated_at else "",
                },
                **kwargs,
            )
        return super().model_validate(obj, **kwargs)


class OrderHistoryResponse(BaseModel):
    """Схема для истории изменений заказа"""
    id: int
    order_id: int
    changed_by_company_id: int
    change_type: str
    change_description: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class UnitOfMeasurementResponse(BaseModel):
    """Схема для единиц измерения"""
    id: int
    name: str
    symbol: str
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CheckoutItem(BaseModel):
    """Схема для товара в корзине (соответствует фронтенду)"""
    slug: str
    description: Optional[str]
    logoUrl: Optional[str]
    type: str
    productName: str
    article: int
    quantity: float
    units: str
    price: float
    amount: float
    companyId: int
    companyName: str
    companySlug: str

    class Config:
        from_attributes = True


class CheckoutRequest(BaseModel):
    """Схема для создания заказа из корзины"""
    items: List[CheckoutItem] = Field(..., min_items=1)
    comments: Optional[str] = None

    class Config:
        from_attributes = True
