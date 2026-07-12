from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator, AliasChoices, ConfigDict
from enum import Enum


class DealStatus(str, Enum):
    ACTIVE = "Активная"
    COMPLETED = "Завершенная"


class OrderTypeSchema(str, Enum):
    """Тип заказа: товары или услуги (соответствует OrderType в БД)."""
    GOODS = "Товары"
    SERVICES = "Услуги"


class ContractTerms(str, Enum):
    """Условия договора в счёте (BillResponse.contract_terms_contract)."""
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
    deal_type: OrderTypeSchema = Field(
        default=OrderTypeSchema.GOODS,
        description="Тип заказа: товары или услуги",
    )
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


class SupplyContractNumberResponse(BaseModel):
	"""Номер договора поставки в ответе сделки (соответствует фронтенду SupplyContractNumberResponse)"""
	model_config = {"extra": "ignore", "from_attributes": True}

	supply_contract_number: str = Field("", description="Номер договора поставки")
	supply_contract_date: Optional[datetime] = Field(None, description="Дата договора поставки", validation_alias=AliasChoices("date", "supply_contract_date"))


class CompanyOfficialInDealResponse(BaseModel):
	"""Должностное лицо для договора поставки и счета (соответствует фронтенду CompanyOfficials)"""
	
	model_config = {"extra": "ignore", "from_attributes": True}

	id: Optional[int] = Field(None, description="ID сотрудника (в ответе — всегда, при создании — может отсутствовать)")
	company_id: int = Field(..., description="ID компании")
	full_name: str = Field(..., description="ФИО", validation_alias=AliasChoices("full_name", "name"))
	position: str = Field("", description="Должность")

	is_base: bool = Field(False, description="Есть ли основание для должностного лица")
	base_document: str = Field("", description="Основание для должностного лица")
	base_document_name: str = Field("", description="Наименование основания для должностного лица")


class 	SupplyContractInDealResponse(BaseModel):
	"""Договор поставки в ответе сделки (соответствует фронтенду SupplyContractResponse)"""
	model_config = {"extra": "ignore", "from_attributes": True}
	entity_id: Optional[int] = Field(None, description="ID сущности supply_contract")
	specification_entity_id: Optional[int] = Field(None, description="ID сущности спецификации")
	number: str = Field("", description="Номер договора поставки")
	officials: List[CompanyOfficialInDealResponse] = Field(default_factory=list, description="Должностные лица (id, full_name, position, is_base, base_document, base_document_name)")
	specification_number: str = Field("", description="Номер спецификации")
	specification_date: Optional[datetime] = Field(None, description="Дата спецификации")

	template_supply_contract: str = Field("", description="Шаблон договора (UI)")
	template_specification: str = Field("", description="Шаблон спецификации (UI)")

	supply_contract_text: str = Field("", description="Текст договора поставки")
	specification_text: str = Field("", description="Текст спецификации")

	supplier_details_check: bool = Field(False, description="Реквизиты продавца")
	buyer_details_check: bool = Field(False, description="Реквизиты покупателя")
	cover_letter_check: bool = Field(False, description="Колонтитул")


class BillUpdateInDeal(BaseModel):
    """Счёт для обновления (соответствует фронтенду BillResponse)"""
    model_config = ConfigDict(
        extra="ignore",
        from_attributes=True,
        json_schema_extra={
            "example": {
                "number": "СЧ-001",
                "reason": "Оплата по счёту",
                "payment_terms_contract": "Оплата в течение 5 рабочих дней",
                "delivery_terms_contract": "",
                "additional_info": "",
                "contract_terms_contract": "standard-delivery-supplier",
                "contract_terms_text_contract": "",
                "payment_terms_offer": "",
                "contract_terms_offer": "standard-delivery-supplier",
                "contract_terms_text_offer": "",
                "additional_info_offer": "",
                "officials": [],
            }
        },
    )
    number: str = Field("", description="Номер счёта")
    reason: Optional[str] = Field("", description="Основание")
    payment_terms: Optional[str] = Field(None, description="Срок оплаты (Счет на оплату), рабочих дней")
    payment_terms_contract: Optional[str] = Field(None, description="Условия оплаты")
    delivery_terms_contract: Optional[str] = Field(None, description="Условия / срок поставки")
    additional_info: Optional[str] = Field(None, description="Дополнительная информация")
    contract_terms_contract: Optional[ContractTerms] = Field(None, description="Вариант условий договора")
    contract_terms_text_contract: Optional[str] = Field(None, description="Текст условий договора")
    payment_terms_offer: Optional[str] = Field(None, description="Условия оплаты (оферта)")
    contract_terms_offer: Optional[ContractTerms] = Field(None, description="Вариант условий оферты")
    contract_terms_text_offer: Optional[str] = Field(None, description="Текст условий оферты")
    additional_info_offer: Optional[str] = Field(None, description="Дополнительная информация (оферта)")
    officials: List["CompanyOfficialInDealResponse"] = Field(default_factory=list, description="Должностные лица (id, full_name, position, is_base, base_document, base_document_name)")


class SupplyContractInUpdate(BaseModel):
	"""Договор поставки для обновления (соответствует фронтенду SupplyContractInDealResponse)"""
	model_config = ConfigDict(
		extra="ignore",
		from_attributes=True,
		populate_by_name=True,
		json_schema_extra={
			"example": {
				"number": "ДП-001",
				"officials": [{"id": 1, "full_name": "Иванов И.И.", "position": "Генеральный директор", "is_base": True, "base_document": "приказа", "base_document_name": "123456789фывафыв"}, {"id": 2, "full_name": "Петрова П.П.", "position": "Главный бухгалтер", "is_base": False, "base_document": "устава", "base_document_name": "1234567890фывафы"}]
			}
		}
	)

	number: str = Field("", description="Номер договора поставки")
	officials: List["CompanyOfficialInDealResponse"] = Field(
		default_factory=list,
		description="Должностные лица (id, full_name, position, is_base, base_document, base_document_name)",
		validation_alias=AliasChoices("officials", "officialsSeller", "officials_seller"),
	)
	specification_number: Optional[str] = Field(None, description="Номер спецификации (legacy на сделке)")
	specification_date: Optional[datetime] = Field(None, description="Дата спецификации (legacy на сделке)")
	template_supply_contract: Optional[str] = Field(None, description="Шаблон договора (UI)")
	template_specification: Optional[str] = Field(None, description="Шаблон спецификации (UI)")
	terms_text: Optional[str] = Field(
		None,
		description="Текст договора поставки",
		validation_alias=AliasChoices("terms_text", "supply_contract_text"),
	)
	specification_text: Optional[str] = Field(None, description="Текст спецификации")
	supplier_details_check: Optional[bool] = Field(None, description="Реквизиты продавца")
	buyer_details_check: Optional[bool] = Field(None, description="Реквизиты покупателя")
	cover_letter_check: Optional[bool] = Field(None, description="Колонтитул")

	@field_validator("specification_date", mode="before")
	@classmethod
	def empty_specification_date_to_none(cls, value):
		if value == "" or value is None:
			return None
		return value

	@field_validator("template_supply_contract", "template_specification", mode="before")
	@classmethod
	def coerce_template_id(cls, value):
		if value is None or value == "":
			return None
		return str(value)


class CompanyInDealUpdate(BaseModel):
    """Частичное обновление company-данных в контексте сделки (только ставка НДС)."""
    model_config = {"extra": "forbid", "from_attributes": True, "populate_by_name": True}
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
                        "contract_terms_contract": "standard-delivery-supplier",
                        "contract_terms_text_contract": "",
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
    supply_contract_date: Optional[datetime] = Field(
        None,
        description="Дата договора поставки",
        validation_alias=AliasChoices("supply_contract_date", "supply_contracts_date"),
    )

    # Объектные поля (формат фронтенда)
    contract: Optional[List[ContractItem]] = Field(None, description="Массив договоров [{number, date}]")
    bill: Optional["BillUpdateInDeal"] = Field(
        None,
        description=(
            "Счёт: number, reason, payment_terms, payment_terms_contract, delivery_terms_contract, additional_info, "
            "contract_terms_contract, contract_terms_text_contract, payment_terms_offer, "
            "contract_terms_offer, contract_terms_text_offer, additional_info_offer, officials"
        ),
    )
    supply_contract: Optional["SupplyContractInUpdate"] = Field(None, description="Договор поставки: number, officials")
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
                "payment_terms_contract": "Оплата в течение 5 рабочих дней",
                "delivery_terms_contract": "",
                "additional_info": "Счет действителен 3 банковских дня",
                "contract_terms_contract": "standard-delivery-supplier",
                "contract_terms_text_contract": "",
                "payment_terms_offer": "",
                "contract_terms_offer": "standard-delivery-supplier",
                "contract_terms_text_offer": "",
                "additional_info_offer": "",
                "officials": [
                    {"id": 1, "full_name": "Иванов И.И.", "position": "Генеральный директор"},
                ],
            }
        },
    )
    number: str = Field("", description="Номер счёта")
    reason: str = Field("", description="Основание")
    payment_terms: str = Field("", description="Срок оплаты (Счет на оплату), рабочих дней")
    payment_terms_contract: str = Field("", description="Условия оплаты")
    delivery_terms_contract: str = Field("", description="Условия / срок поставки")
    additional_info: str = Field("", description="Дополнительная информация")
    contract_terms_contract: ContractTerms = Field(
        default=ContractTerms.STANDARD_DELIVERY_SUPPLIER,
        description=(
            "Пресет условий договора в счёте: standard-delivery-supplier | "
            "standard-delivery-buyer | custom"
        ),
    )
    contract_terms_text_contract: str = Field(
        default="",
        description="Полный текст условий (для custom или сгенерированный для пресетов)",
    )
    payment_terms_offer: str = Field("", description="Условия оплаты (оферта)")
    contract_terms_offer: ContractTerms = Field(
        default=ContractTerms.STANDARD_DELIVERY_SUPPLIER,
        description="Пресет условий оферты (как contract_terms_contract)",
    )
    contract_terms_text_offer: str = Field(
        default="",
        description="Текст условий оферты",
    )
    additional_info_offer: str = Field("", description="Дополнительная информация (оферта)")
    officials: List["CompanyOfficialInDealResponse"] = Field(default_factory=list, description="Должностные лица")


class CompanyInDealResponse(BaseModel):
	"""Схема компании в контексте сделки (соответствует фронтенду CompanyInDealResponse: owner_name, company_id, production_address, account_number, correspondent_bank_account, bank_name)."""
	model_config = {
			"from_attributes": True,
			"populate_by_name": True,
			"json_schema_extra": {
					"example": {
							"company_id": 1,
							"company_name": "ООО Пример",
							"full_name": "Общество с ограниченной ответственностью Пример",
							"city": "Москва",
							"owner_name": "Иванов Иван Иванович",
							"slug": "ooo-primer",
							"inn": "7707083893",
							"ogrn": "1027700132195",
							"phone": "+79990000000",
							"email": "info@example.ru",
							"legal_address": "г. Москва, ул. Примерная, д. 1",
							"production_address": "г. Москва, ул. Заводская, д. 5",
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
	company_type: str = Field(..., description="Тип компании")
	full_name: str = Field("", description="Полное название компании")
	city: str = Field("", description="Город компании")
	name: str = Field(..., description="Имя владельца компании", serialization_alias="owner_name")
	slug: str = Field(..., description="Slug компании")
	inn: Optional[str] = Field(None, description="ИНН компании")
	ogrn: Optional[str] = Field(None, description="ОРГН компании")
	phone: str = Field("", description="Телефон компании")
	email: str = Field("", description="Email компании")
	legal_address: str = Field("", description="Юридический адрес компании")
	production_address: str = Field("", description="Адрес производства")
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
                "total_amount_word": "десять тысяч рублей, ноль копеек",
                "total_amount_excl_vat": 10000.0,
                "amount_vat_rate": 0.0,
                "amount_with_vat_rate": True,
                "comments": None,
                "contract_date": None,
                "bill_date": None,
                "supply_contract_date": None,
                "closing_documents": [],
                "others_documents": [],
                "created_at": "2025-01-01T12:00:00",
                "updated_at": "2025-01-01T12:00:00",
                "role": "buyer",
                "contract": [],
                "bill": {
                    "number": "СЧ-001",
                    "reason": "Оплата по счёту",
                    "payment_terms_contract": "Оплата в течение 5 рабочих дней",
                    "delivery_terms_contract": "",
                    "additional_info": "",
                    "contract_terms_contract": "standard-delivery-supplier",
                    "contract_terms_text_contract": "",
                    "payment_terms_offer": "",
                    "contract_terms_offer": "standard-delivery-supplier",
                    "contract_terms_text_offer": "",
                    "additional_info_offer": "",
                    "officials": [],
                },
                "supply_contract": {
                    "number": "ДП-001",
                    "officials": [
                        {"id": 1, "full_name": "Иванов И.И.", "position": "Генеральный директор", "is_base": True, "base_document": "приказа", "base_document_name": "123456789фывафыв"},
                        {"id": 2, "full_name": "Петрова П.П.", "position": "Главный бухгалтер", "is_base": False, "base_document": "устава", "base_document_name": "1234567890фывафы"}
                    ]
                },
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
                    "production_address": "",
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
                    "production_address": "",
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
    deal_type: OrderTypeSchema = Field(
        default=OrderTypeSchema.GOODS,
        description="Тип заказа: товары или услуги",
    )
    status: DealStatus
    total_amount: float
    total_amount_word: str = Field(
        "",
        description="Сумма total_amount прописью (рубли и копейки); заполняется на сервере, в запросах не передаётся",
    )
    total_amount_excl_vat: float = Field(
        0,
        description="Сумма позиций заказа (qty×price) без учёта НДС; при amount_with_vat_rate: total_amount ≈ total_amount_excl_vat + amount_vat_rate",
    )
    amount_vat_rate: float = Field(0, description="Сумма НДС по сделке")
    amount_with_vat_rate: bool = Field(True, description="Если true — total_amount включает НДС (seller_company.vat_rate)")
    comments: Optional[str]
    contract_date: Optional[datetime] = None
    bill_date: Optional[datetime] = None
    supply_contract_date: Optional[datetime] = None
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
            "Счёт на оплату: number, reason, payment_terms_contract, delivery_terms_contract, additional_info, "
            "contract_terms_contract, contract_terms_text_contract, payment_terms_offer, "
            "contract_terms_offer, contract_terms_text_offer, additional_info_offer, officials"
        ),
    )
    supply_contract: Optional["SupplyContractInDealResponse"] = Field(
        None,
        description="Договор поставки: number, officials (id, full_name, position, is_base, base_document, base_document_name)",
    )

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
    total_amount_excl_vat: float = Field(0, description="Сумма позиций без НДС")
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
    total_amount_excl_vat: float = Field(0, description="Сумма позиций без НДС")
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
    article: str
    productType: Optional[str] = Field(
        None,
        description="Тип позиции каталога: «Товар» или «Услуга»",
    )
    quantity: float
    units: str
    price: float
    amount: float
    companyId: Optional[int] = Field(
        None,
        description="ID продавца; если не передан — определяется по slug товара в каталоге",
    )
    companyName: Optional[str] = None
    companySlug: Optional[str] = None

    class Config:
        from_attributes = True


class CheckoutRequest(BaseModel):
    """Схема для создания заказа из корзины"""
    items: List[CheckoutItem] = Field(..., min_items=1)
    comments: Optional[str] = None

    class Config:
        from_attributes = True


class CheckoutResponse(BaseModel):
    """Ответ checkout: один или несколько заказов (по продавцу и типу товар/услуга)."""
    deals: List["DealResponse"] = Field(default_factory=list)


class SupplyContractCreate(BaseModel):
	"""Схема создания договра поставки"""

	seller_company_id: int = Field(..., description="id продавца")
	buyer_company_id: int = Field(..., description="id покупателя")

	@model_validator(mode="after")
	def companies_are_not_equal(self):
		if self.seller_company_id == self.buyer_company_id:
			raise ValueError("Companies ids are equal")

		return self


class SupplyContractUpdate(BaseModel):
	"""Схема для обновления договора поставки"""

	officials_json: Optional[list["CompanyOfficialInDealResponse"]] = Field(default=None, description="словарь подписавшихся лиц")
	terms_text: Optional[str] = Field(default=None, description="Текст договора поставки")
	supplier_details_check: Optional[bool] = None
	buyer_details_check: Optional[bool] = None
	cover_letter_check: Optional[bool] = None


class SupplyContractResponse(BaseModel):
	"""Схема ответа договора поставки"""

	id: int
	buyer_company_id: int
	seller_company_id: int

	number: str = Field(...,max_length=10)
	date: datetime
	officials_json: Optional[list["CompanyOfficialInDealResponse"]] = Field(default=None, description="словарь подписавшихся лиц")
	terms_text: Optional[str] = Field(default='', description="Текст договора поставки")

	specifications: list["SpecificationResponse"] = Field(default_factory=list)

	supplier_details_check: bool = Field(default=False, description="реквизиты продавца")
	buyer_details_check: bool = Field(default=False, description="реквизиты покупателя")
	cover_letter_check: bool = Field(default=False, description="колонтитул")

	model_config = {"from_attributes": True}


class SpecificationCreate(BaseModel):
	"""Схема создания спецификации(изначально создается пустая спецификация, которая потом заполняется через эндпоинт обновления)"""

	pass


class SpecificationUpdate(BaseModel):
	"""Схема обновления спецификации"""

	spec_text: Optional[str] = None
	spec_items: Optional[list["SpecificationItem"]] = None


class SpecificationResponse(BaseModel):
	"""Схема ответа для спецификации"""

	id: int
	supply_contract_id: int = Field(..., description="ID договора поставки, на который опирается спецификация")
	supply_contract_number: Optional[str] = Field(None, max_length=10, description="Номер договора поставки")
	spec_number: str = Field(..., max_length=10, description="номер спецификации")
	spec_date: datetime
	spec_text: Optional[str] = Field(default='', description="Текст спецификации")
	spec_items: list["SpecificationItem"] = Field(default_factory=list, description="товары в таблице, на которые оформлена спецификация")

	model_config = {"from_attributes": True, "extra": "ignore"}

class SpecificationItem(BaseModel):
	"""Товар в таблице сецификации"""

	name: str = Field(..., max_length=255)
	article: Optional[str] = Field(default=None, max_length=16)
	quantity: int = Field(..., ge=0)
	units: str = Field(..., max_length=32)
	price: float = Field(..., ge=0)
	amount: float = Field(..., ge=0)

	@model_validator(mode="after")
	def amount_matches_quantity_price(self):
		expected = round(float(self.quantity) * float(self.price), 2)
		actual = round(float(self.amount), 2)
		if abs(expected - actual) > 0.01:
			raise ValueError("amount must equal quantity * price")
		return self


class SupplyContractExistsResponse(BaseModel):
	is_exist: bool
	supply_contract: Optional[SupplyContractResponse] = None


class CompanyContractResponse(BaseModel):
	"""Договор из ЛК «Договоры» для выбора основания счёта."""

	id: int
	seller_company_id: int
	buyer_company_id: int
	number: str
	date: datetime
	counterparty_company_id: int = Field(..., description="ID контрагента относительно текущей компании")
	counterparty_name: str = Field("", description="Название контрагента")
	counterparty_role: str = Field(
		"",
		description="Роль контрагента: buyer | seller",
	)

	model_config = {"from_attributes": True}


class CompanyContractCreate(BaseModel):
	counterparty_company_id: int = Field(..., gt=0)
	number: Optional[str] = Field(
		None,
		min_length=1,
		max_length=20,
		description="Если не указан — присваивается автоматически (маска 00000)",
	)
	date: Optional[datetime] = Field(
		None,
		description="Если не указана — текущая дата",
	)
	relation: Literal["as_seller", "as_buyer"] = Field(
		default="as_seller",
		description="as_seller: текущая компания — поставщик; as_buyer: текущая компания — покупатель",
	)


class CompanyContractNextNumberResponse(BaseModel):
	number: str
	date: datetime


class CompanyContractUpdate(BaseModel):
	number: Optional[str] = Field(None, min_length=1, max_length=20)
	date: Optional[datetime] = None


class CompanyContractListResponse(BaseModel):
	contracts: list[CompanyContractResponse] = Field(default_factory=list)


class BindSupplyContractToDealRequest(BaseModel):
	contract_id: int = Field(..., gt=0, description="ID договора поставки")


class BindSupplySpecificationToDealRequest(BaseModel):
	spec_id: int = Field(..., gt=0, description="ID спецификации")


class SupplyContractTemplateCreate(BaseModel):
	model_config = ConfigDict(extra="ignore")

	type: str = Field(..., description="supply_contract | specification")
	name: str = Field(..., min_length=1, max_length=128)
	content_html: str = Field("", description="HTML содержимое шаблона")
	is_default: bool = Field(False, description="Использовать по умолчанию для данного типа")


class SupplyContractTemplateUpdate(BaseModel):
	model_config = ConfigDict(extra="ignore")

	name: Optional[str] = Field(None, min_length=1, max_length=128)
	content_html: Optional[str] = None
	is_default: Optional[bool] = None


class SupplyContractTemplateResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	company_id: int
	type: str
	name: str
	content_html: str
	is_default: bool


class DealChangeReviewResponse(BaseModel):
	"""Статус ожидания согласования изменений по последней версии сделки."""

	has_pending_changes: bool = Field(..., description="Есть неподтверждённая новая версия")
	can_respond: bool = Field(..., description="Текущая компания может принять или отклонить")
	is_proposer: bool = Field(..., description="Текущая компания предложила изменения")
	proposed_by_company_id: Optional[int] = Field(None, description="ID компании-инициатора изменений")
	version: int = Field(..., description="Номер последней версии сделки")
	diff: Optional["DealOrderChangeDiffResponse"] = Field(
		None, description="Сравнение с предыдущей версией (только при pending)"
	)


class OrderLineChangeResponse(BaseModel):
	status: str = Field(..., description="added | removed | modified")
	match_key: str = Field(..., description="Ключ сопоставления позиции")
	product_name: Optional[str] = None
	product_article: Optional[str] = None
	quantity: Optional[float] = None
	unit_of_measurement: Optional[str] = None
	price: Optional[float] = None
	amount: Optional[float] = None
	changed_fields: List[str] = Field(default_factory=list)


class DealOrderChangeDiffResponse(BaseModel):
	baseline_version: int
	proposed_version: int
	comments_changed: bool = False
	total_amount_changed: bool = False
	items: List[OrderLineChangeResponse] = Field(default_factory=list)