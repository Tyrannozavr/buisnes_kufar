from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ProductType(str, Enum):
    PRODUCT = "Товар"
    SERVICE = "Услуга"

class Characteristic(BaseModel):
    name: str
    value: str

class Product(BaseModel):
    id: str
    company_id: str = Field(..., alias="companyId")
    name: str
    description: str
    article: str
    type: ProductType
    price: float
    images: List[str]
    characteristics: List[Characteristic]
    is_hidden: bool = Field(..., alias="isHidden")
    is_deleted: bool = Field(..., alias="isDeleted")
    slug: str

class PaginationInfo(BaseModel):
    total: int
    page: int
    per_page: int = Field(..., alias="perPage")
    total_pages: int = Field(..., alias="totalPages")

class ProductsResponse(BaseModel):
    data: List[Product]
    pagination: PaginationInfo

class ProductCreate(BaseModel):
    name: str
    description: str
    article: str
    type: ProductType
    price: float
    images: List[str]
    characteristics: List[Characteristic]
    is_hidden: bool = Field(False, alias="isHidden")

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    article: Optional[str] = None
    type: Optional[ProductType] = None
    price: Optional[float] = None
    images: Optional[List[str]] = None
    characteristics: Optional[List[Characteristic]] = None
    is_hidden: Optional[bool] = Field(None, alias="isHidden")