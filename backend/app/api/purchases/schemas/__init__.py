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
    1. С product_id: указывайте только product_id и quantity, остальные данные берутся из БД
    2. Без product_id: указывайте все поля вручную (product_name, price, unit_of_measurement обязательны)
    """
    product_id: Optional[int] = Field(
        None, 
        description="ID продукта из каталога. Если указан, остальные данные (название, цена, единица измерения) берутся из БД автоматически"
    )
    quantity: float = Field(..., gt=0, description="Количество")
    
    # Поля для ручного ввода (используются только если product_id не указан или равен 0)
    product_name: Optional[str] = Field(
        None, 
        description="Наименование товара/услуги. Обязательно, если product_id не указан"
    )
    product_slug: Optional[str] = Field(None, description="Slug продукта")
    product_description: Optional[str] = Field(None, description="Описание продукта")
    product_article: Optional[str] = Field(None, description="Артикул")
    product_type: Optional[str] = Field(None, description="Тип продукта")
    logo_url: Optional[str] = Field(None, description="URL логотипа")
    unit_of_measurement: Optional[str] = Field(
        None, 
        description="Единица измерения. Обязательно, если product_id не указан"
    )
    price: Optional[float] = Field(
        None, 
        gt=0, 
        description="Цена за единицу. Обязательно, если product_id не указан"
    )
    position: Optional[int] = Field(
        None, 
        ge=1, 
        description="Позиция в заказе (автоматически, если не указана)"
    )
    
    @model_validator(mode='after')
    def validate_required_fields(self):
        """Валидация: если product_id не указан, обязательны product_name, price, unit_of_measurement"""
        if not self.product_id or self.product_id == 0:
            if not self.product_name:
                raise ValueError("product_name is required when product_id is not specified")
            if not self.price:
                raise ValueError("price is required when product_id is not specified")
            if not self.unit_of_measurement:
                raise ValueError("unit_of_measurement is required when product_id is not specified")
        return self
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "examples": [
                {
                    "product_id": 1,
                    "quantity": 2
                },
                {
                    "product_id": None,
                    "quantity": 1,
                    "product_name": "Кастомный товар",
                    "price": 100.0,
                    "unit_of_measurement": "шт"
                }
            ]
        }


class OrderItemResponse(OrderItemBase):
    """Схема для ответа с позицией заказа"""
    id: int
    order_id: int
    amount: float = Field(..., description="Сумма (quantity * price)")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DealCreate(BaseModel):
    """Схема для создания заказа
    
    Тип заказа (deal_type) определяется автоматически на основе типов продуктов:
    - Если указан явно, используется указанный тип (с проверкой соответствия продуктов)
    - Если не указан, определяется автоматически: если есть хотя бы одна услуга - "Услуги", иначе "Товары"
    """
    seller_company_id: int = Field(..., description="ID компании-продавца")
    deal_type: Optional[ItemType] = Field(None, description="Тип заказа (товары/услуги). Если не указан, определяется автоматически на основе продуктов")
    items: List[OrderItemCreate] = Field(..., min_items=1, description="Позиции заказа")
    comments: Optional[str] = Field(None, description="Комментарии к заказу")

    class Config:
        from_attributes = True


class DealUpdate(BaseModel):
    """Схема для обновления заказа"""
    status: Optional[DealStatus] = Field(None, description="Статус заказа")
    items: Optional[List[OrderItemCreate]] = Field(None, description="Обновленные позиции")
    comments: Optional[str] = Field(None, description="Комментарии")
    invoice_number: Optional[str] = Field(None, description="Номер счета")
    contract_number: Optional[str] = Field(None, description="Номер договора")

    class Config:
        from_attributes = True


class DealResponse(BaseModel):
    """Полная схема заказа для ответа"""
    id: int
    buyer_company_id: int
    seller_company_id: int
    buyer_order_number: str
    seller_order_number: str
    status: DealStatus
    deal_type: ItemType
    total_amount: float
    comments: Optional[str]
    invoice_number: Optional[str]
    contract_number: Optional[str]
    invoice_date: Optional[datetime]
    contract_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Связанные данные
    items: List[OrderItemResponse] = Field(default_factory=list)
    buyer_company: Optional[Dict[str, Any]] = Field(None)
    seller_company: Optional[Dict[str, Any]] = Field(None)

    class Config:
        from_attributes = True


class BuyerDealResponse(BaseModel):
    """Схема заказа для покупателя"""
    id: int
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


class DocumentUpload(BaseModel):
    """Схема для загрузки документа"""
    document_type: str = Field(..., description="Тип документа (invoice, contract, act, etc.)")
    document_number: Optional[str] = Field(None, description="Номер документа")
    document_date: Optional[datetime] = Field(None, description="Дата документа")
    description: Optional[str] = Field(None, description="Описание документа")

    class Config:
        from_attributes = True


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
    position: int
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
