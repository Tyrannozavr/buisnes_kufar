from typing import List

from pydantic import BaseModel, Field


class ProductListItem(BaseModel):
    id: int
    name: str
    description: str
    price: float
    # Добавьте другие необходимые поля продукта


class PaginationInfo(BaseModel):
    total: int
    page: int
    per_page: int = Field(..., alias="perPage")
    total_pages: int = Field(..., alias="totalPages")


class ProductsResponse(BaseModel):
    """Ответ с списком продуктов и пагинацией"""
    data: List[ProductListItem]
    pagination: PaginationInfo
