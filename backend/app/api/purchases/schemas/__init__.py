from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator, AliasChoices, ConfigDict
from enum import Enum


class DealStatus(str, Enum):
    ACTIVE = "Активная"
    COMPLETED = "Завершенная"


class ContractTerms(str, Enum):
    """Условия договора в счёте (как во фронтенде BillResponse.contract_terms)."""
    STANDARD_DELIVERY_SUPPLIER = "standard-delivery-supplier"
    STANDARD_DELIVERY_BUYER = "standard-delivery-buyer"
    CUSTOM = "custom"


class OrderItemBase(BaseModel):
    """Базовая схема для позиции заказа"""
    product_name: str = Field(..., description="Наименование товара/услуги")
    product_slug: Optional[str] = Field(None, description="Slug продукта")
    product_description: Optional[str] = Field(None, description="Описание продукта")
    product_article: Optional[str] = Field(None, description="Артикул")
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
    model_config = {"extra": "ignore", "from_attributes": True}
    article: Optional[str] = Field(None, description="Артикул продукта из каталога")
    quantity: float = Field(..., ge=0, description="Количество")
    product_name: Optional[str] = Field(None, description="Наименование товара/услуги", validation_alias=AliasChoices("product_name", "productName"))
    product_slug: Optional[str] = Field(None, description="Slug продукта", validation_alias=AliasChoices("product_slug", "productSlug"))
    product_description: Optional[str] = Field(None, description="Описание продукта", validation_alias=AliasChoices("product_description", "productDescription"))
    product_article: Optional[str] = Field(None, description="Артикул", validation_alias=AliasChoices("product_article", "productArticle"))
    logo_url: Optional[str] = Field(None, description="URL логотипа", validation_alias=AliasChoices("logo_url", "logoUrl"))
    unit_of_measurement: Optional[str] = Field(None, description="Единица измерения", validation_alias=AliasChoices("unit_of_measurement", "unitOfMeasurement"))
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
    """Схема для создания заказа между покупателем и продавцом."""
    seller_company_id: int = Field(..., description="ID компании-продавца")
    items: List[OrderItemCreate] = Field(..., min_items=1, description="Позиции заказа")
    comments: Optional[str] = Field(None, description="Комментарии к заказу")

    class Config:
        from_attributes = True


class DealIdsBody(BaseModel):
	"""Тело запроса для получения сделок по списку ID."""
	ids: List[int] = Field(..., min_length=1, description="Массив ID сделок")

	model_config = {"json_schema_extra": {"examples": [{"ids": [1, 2, 3]}]}}


class ContractItem(BaseModel):
	"""Элемент договора в массиве contract"""
	model_config = {"extra": "ignore", "from_attributes": True}
	number: Optional[str] = Field(None, description="Номер договора", validation_alias=AliasChoices("number", "contract_number"))
	date: Optional[datetime] = Field(None, description="Дата договора", validation_alias=AliasChoices("date", "contract_date"))


class SupplyContractItem(BaseModel):
	"""Элемент договора поставки в массиве supply_contracts"""
	model_config = {"extra": "ignore", "from_attributes": True}
	number: Optional[str] = Field(None, description="Номер договора поставки", validation_alias=AliasChoices("number", "supply_contracts_number"))
	date: Optional[datetime] = Field(None, description="Дата договора поставки", validation_alias=AliasChoices("date", "supply_contracts_date"))


class OfficialsInBillResponse(BaseModel):
    """Должностное лицо для счёта (соответствует фронтенду OfficialsResponse)"""
    model_config = {"extra": "ignore", "from_attributes": True}
    id: Optional[int] = Field(None, description="ID сотрудника (в ответе — всегда, при создании — может отсутствовать)")
    full_name: str = Field(..., description="ФИО", validation_alias=AliasChoices("full_name", "name"))
    position: str = Field("", description="Должность")


class BillUpdateInDeal(BaseModel):
    """Счёт для обновления (соответствует фронтенду BillResponse)"""
    model_config = ConfigDict(
        extra="ignore",
        from_attributes=True,
        json_schema_extra={
            "example": {
                "number": "СЧ-001",
                "reason": "Оплата по счёту",
                "payment_terms": "Оплата в течение 5 рабочих дней",
                "delivery_terms": "",
                "additional_info": "",
                "contract_terms": "standard-delivery-supplier",
                "contract_terms_text": "",
                "officials": [],
            }
        },
    )
    number: str = Field("", description="Номер счёта")
    reason: Optional[str] = Field("", description="Основание")
    payment_terms: Optional[str] = Field(None, description="Условия оплаты")
    delivery_terms: Optional[str] = Field(None, description="Условия / срок поставки")
    additional_info: Optional[str] = Field(None, description="Дополнительная информация")
    contract_terms: Optional[ContractTerms] = Field(None, description="Вариант условий договора")
    contract_terms_text: Optional[str] = Field(None, description="Текст условий договора")
    officials: List["OfficialsInBillResponse"] = Field(default_factory=list, description="Должностные лица")


class CompanyInDealUpdate(BaseModel):
    """Частичное обновление company-данных в контексте сделки."""
    model_config = {"extra": "ignore", "from_attributes": True, "populate_by_name": True}
    vat_rate: Optional[int] = Field(None, ge=0, le=25, validation_alias=AliasChoices("vat_rate", "vatRate"))


class DealUpdate(BaseModel):
    """Схема для обновления заказа (PUT /deals/{deal_id}, POST /deals/{id}/versions). Совместима с фронтендом DealUpdate."""
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "extra": "ignore",
        "json_schema_extra": {
            "examples": [
                {"comments": "Обновление", "amount_with_vat_rate": True},
                {"status": "Активная", "amount_with_vat_rate": False},
                {
                    "comments": "Патч счёта с условиями договора",
                    "bill": {
                        "number": "СЧ-001",
                        "contract_terms": "standard-delivery-supplier",
                        "contract_terms_text": "",
                    },
                },
            ]
        },
    }

    status: Optional[DealStatus] = Field(None, description="Статус заказа")
    items: Optional[List[OrderItemUpdate]] = Field(None, description="Обновлённые позиции (OrderItemUpdate: quantity >= 0, price >= 0)")
    comments: Optional[str] = Field(None, description="Комментарии")
    updated_at: Optional[str] = Field(None, description="Метка времени (игнорируется на сервере, для клиентского кэша)")
    total_amount: Optional[float] = Field(None, description="Общая сумма сделки")
    amount_vat_rate: Optional[float] = Field(None, description="Сумма НДС по сделке")
    amount_with_vat_rate: Optional[bool] = Field(None, description="Если true — total_amount пересчитывается с учётом НДС (seller_company.vat_rate). Меняется при POST /deals/{id}/versions.")

    # Плоские поля (snake_case) — даты обновляются только через POST /deals/{id}/versions
    contract_date: Optional[datetime] = Field(None, description="Дата договора")
    bill_date: Optional[datetime] = Field(None, description="Дата счета на оплату")
    supply_contracts_date: Optional[datetime] = Field(None, description="Дата договора поставки")

    # Объектные поля (формат фронтенда)
    contract: Optional[List[ContractItem]] = Field(None, description="Массив договоров [{number, date}]")
    bill: Optional["BillUpdateInDeal"] = Field(
        None,
        description=(
            "Счёт: number, reason, payment_terms, delivery_terms, additional_info, "
            "contract_terms, contract_terms_text, officials"
        ),
    )
    supply_contracts: Optional[List[SupplyContractItem]] = Field(None, description="Договоры поставки [{number, date}]")
    closing_documents: Optional[List[Any]] = Field(None, description="Закрывающие документы")
    others_documents: Optional[List[Any]] = Field(None, description="Прочие документы")
    seller_company: Optional["CompanyInDealUpdate"] = Field(None, description="Частичное обновление company-данных продавца в контексте сделки")


class BillInDealResponse(BaseModel):
    """Счёт в ответе сделки (соответствует фронтенду BillResponse)"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "number": "СЧ-001",
                "reason": "Оплата по счёту № СЧ-001",
                "payment_terms": "Оплата в течение 5 рабочих дней",
                "delivery_terms": "",
                "additional_info": "Счет действителен 3 банковских дня",
                "contract_terms": "standard-delivery-supplier",
                "contract_terms_text": "",
                "officials": [
                    {"id": 1, "full_name": "Иванов И.И.", "position": "Генеральный директор"},
                ],
            }
        },
    )
    number: str = Field("", description="Номер счёта")
    reason: str = Field("", description="Основание")
    payment_terms: str = Field("", description="Условия оплаты")
    delivery_terms: str = Field("", description="Условия / срок поставки")
    additional_info: str = Field("", description="Дополнительная информация")
    contract_terms: ContractTerms = Field(
        default=ContractTerms.STANDARD_DELIVERY_SUPPLIER,
        description=(
            "Пресет условий договора в счёте: standard-delivery-supplier | "
            "standard-delivery-buyer | custom"
        ),
    )
    contract_terms_text: str = Field(
        default="",
        description="Полный текст условий (для custom или сгенерированный для пресетов)",
    )
    officials: List["OfficialsInBillResponse"] = Field(default_factory=list, description="Должностные лица")


class CompanyInDealResponse(BaseModel):
    """Схема компании в контексте сделки (соответствует фронтенду CompanyInDealResponse: owner_name, company_id, account_number, correspondent_bank_account, bank_name)."""
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "company_id": 1,
                "company_name": "ООО Пример",
                "owner_name": "Иванов Иван Иванович",
                "slug": "ooo-primer",
                "inn": "7707083893",
                "phone": "+79990000000",
                "email": "info@example.ru",
                "legal_address": "г. Москва, ул. Примерная, д. 1",
                "index": "101000",
                "kpp": "770701001",
                "account_number": "40702810100000000000",
                "correspondent_bank_account": "30101810100000000593",
                "bank_name": "ПАО Сбербанк",
                "bic": "044525225",
                "vat_rate": 20,
            }
        },
    }

    id: int = Field(..., description="ID компании", serialization_alias="company_id")
    company_name: str = Field(..., description="Название компании")
    name: str = Field(..., description="Имя владельца компании", serialization_alias="owner_name")
    slug: str = Field(..., description="Slug компании")
    inn: Optional[str] = Field(None, description="ИНН компании")
    phone: str = Field("", description="Телефон компании")
    email: str = Field("", description="Email компании")
    legal_address: str = Field("", description="Юридический адрес компании")
    index: Optional[str] = Field(None, description="Почтовый индекс")
    kpp: Optional[str] = Field(None, description="КПП")
    current_account_number: Optional[str] = Field(None, description="Расчётный счёт", serialization_alias="account_number")
    correspondent_bank_account: Optional[str] = Field(None, description="Корреспондентский счёт")
    bank_name: Optional[str] = Field(None, description="Наименование банка")
    bic: Optional[str] = Field(None, description="БИК")
    vat_rate: Optional[int] = Field(None, description="Ставка НДС")


class DealRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"


class DealResponse(BaseModel):
    """Полная схема заказа для ответа. Реквизиты банка (account_number, correspondent_bank_account, bank_name, bic) — в объектах buyer_company и seller_company (см. CompanyInDealResponse)."""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "version": 1,
                "buyer_company_id": 10,
                "seller_company_id": 20,
                "buyer_order_number": "00001",
                "seller_order_number": "00001",
                "status": "Активная",
                "total_amount": 10000.0,
                "amount_vat_rate": 0.0,
                "amount_with_vat_rate": True,
                "comments": None,
                "contract_date": None,
                "bill_date": None,
                "supply_contracts_date": None,
                "closing_documents": [],
                "others_documents": [],
                "created_at": "2025-01-01T12:00:00",
                "updated_at": "2025-01-01T12:00:00",
                "role": "buyer",
                "contract": [],
                "bill": {
                    "number": "СЧ-001",
                    "reason": "Оплата по счёту",
                    "payment_terms": "Оплата в течение 5 рабочих дней",
                    "delivery_terms": "",
                    "additional_info": "",
                    "contract_terms": "standard-delivery-supplier",
                    "contract_terms_text": "",
                    "officials": [],
                },
                "supply_contracts": [],
                "items": [],
                "buyer_company": {
                    "company_id": 10,
                    "company_name": "ООО Покупатель",
                    "owner_name": "Иванов И.И.",
                    "slug": "buyer",
                    "inn": "7707083893",
                    "phone": "+79990000001",
                    "email": "info@buyer.ru",
                    "legal_address": "г. Москва",
                    "index": "101000",
                    "kpp": "770701001",
                    "account_number": "40702810100000000001",
                    "correspondent_bank_account": "30101810100000000593",
                    "bank_name": "ПАО Сбербанк",
                    "bic": "044525225",
                    "vat_rate": 20,
                },
                "seller_company": {
                    "company_id": 20,
                    "company_name": "ООО Продавец",
                    "owner_name": "Петров П.П.",
                    "slug": "seller",
                    "inn": "7707083894",
                    "phone": "+79990000002",
                    "email": "info@seller.ru",
                    "legal_address": "г. Санкт-Петербург",
                    "index": "190000",
                    "kpp": "770701002",
                    "account_number": "40702810100000000002",
                    "correspondent_bank_account": "30101810100000000594",
                    "bank_name": "АО Альфа-Банк",
                    "bic": "044525593",
                    "vat_rate": 20,
                },
            }
        },
    )

    id: int
    version: int = Field(..., description="Версия сделки (1..N), где N — последняя версия")
    buyer_company_id: int
    seller_company_id: int
    buyer_order_number: str
    seller_order_number: str
    status: DealStatus
    total_amount: float
    amount_vat_rate: float = Field(0, description="Сумма НДС по сделке")
    amount_with_vat_rate: bool = Field(True, description="Если true — total_amount включает НДС (seller_company.vat_rate)")
    comments: Optional[str]
    contract_date: Optional[datetime] = None
    bill_date: Optional[datetime] = None
    supply_contracts_date: Optional[datetime] = None
    closing_documents: List[Any] = Field(default_factory=list, description="Закрывающие документы (пока пустой список)")
    others_documents: List[Any] = Field(default_factory=list, description="Прочие документы (пока пустой список)")
    created_at: datetime
    updated_at: datetime

    role: Optional[DealRole] = Field(
        default=None,
        description="Роль текущей компании относительно сделки (buyer/seller)",
    )

    # Поля для совместимости с фронтендом (DealResponse)
    contract: List["ContractItem"] = Field(default_factory=list, description="Массив договоров [{number, date}]")
    bill: Optional["BillInDealResponse"] = Field(
        None,
        description=(
            "Счёт на оплату: number, reason, payment_terms, delivery_terms, additional_info, "
            "contract_terms, contract_terms_text, officials"
        ),
    )
    supply_contracts: List["SupplyContractItem"] = Field(default_factory=list, description="Договоры поставки [{number, date}]")

    # Связанные данные
    items: List[OrderItemResponse] = Field(default_factory=list)
    buyer_company: Optional[CompanyInDealResponse] = Field(
        None,
        description="Компания-покупатель: в т.ч. account_number, correspondent_bank_account, bank_name, bic",
    )
    seller_company: Optional[CompanyInDealResponse] = Field(
        None,
        description="Компания-продавец: в т.ч. account_number, correspondent_bank_account, bank_name, bic",
    )


class BuyerDealResponse(BaseModel):
    """Схема заказа для покупателя"""
    id: int
    version: int = Field(..., description="Текущая версия сделки в списке")
    buyer_company_id: int
    seller_company_id: int
    buyer_order_number: str
    seller_order_number: str
    status: DealStatus
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
