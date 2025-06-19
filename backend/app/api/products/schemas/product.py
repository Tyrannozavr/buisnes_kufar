from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.api.products.models.product import ProductType


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    article: str = Field(..., min_length=1, max_length=100)
    type: ProductType
    price: float = Field(..., gt=0)
    unit_of_measurement: Optional[str] = Field(None, max_length=100)
    is_hidden: bool = False


class ProductCreate(ProductBase):
    images: List[str] = []
    characteristics: List[dict] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    article: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[ProductType] = None
    price: Optional[float] = Field(None, gt=0)
    unit_of_measurement: Optional[str] = Field(None, max_length=100)
    is_hidden: Optional[bool] = None
    images: Optional[List[str]] = None
    characteristics: Optional[List[dict]] = None


class ProductResponse(ProductBase):
    id: int
    slug: str
    images: List[str]
    characteristics: List[dict]
    is_deleted: bool
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int 