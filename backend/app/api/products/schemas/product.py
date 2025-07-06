from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, computed_field, ConfigDict

from app.api.products.models.product import ProductType
from app.core.config import settings


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    article: str = Field(..., min_length=1, max_length=100)
    type: ProductType
    price: float = Field(..., gt=0)
    unit_of_measurement: Optional[str] = Field(None, max_length=100)
    is_hidden: bool = False


class ProductCreate(ProductBase):
    characteristics: List[dict] = []


class ProductCreateWithFiles(BaseModel):
    """Схема для создания продукта с файлами"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    article: str = Field(..., min_length=1, max_length=100)
    type: ProductType
    price: float = Field(..., gt=0)
    unit_of_measurement: Optional[str] = Field(None, max_length=100)
    is_hidden: bool = False
    characteristics: List[dict] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    article: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[ProductType] = None
    price: Optional[float] = Field(None, gt=0)
    unit_of_measurement: Optional[str] = Field(None, max_length=100)
    is_hidden: Optional[bool] = False
    is_deleted: Optional[bool] = False
    characteristics: Optional[List[dict]] = None


class ProductResponse(ProductBase):
    id: int
    slug: str
    raw_images: List[str] = Field(alias="images")
    characteristics: List[dict]
    is_deleted: bool
    company_id: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    def images(self) -> List[str]:
        return [f"{settings.BASE_IMAGE_URL}{image}" for image in self.raw_images]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class ProductPublicItemResponse(ProductBase):
    is_deleted: bool | None = Field(exclude=True)
    is_hidden: bool | None = Field(exclude=True)
    slug: str
    raw_images: List[str] = Field(alias="images", exclude=True)

    @computed_field
    @property
    def logo_url(self) -> Optional[str]:
        if hasattr(self, 'raw_images') and self.raw_images:
            return f"{settings.BASE_IMAGE_URL}{self.raw_images[0]}"
        else:
            return None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int


class ProductListPublicResponse(BaseModel):
    products: List[ProductPublicItemResponse]
    total: int
    page: int
    per_page: int
