import enum
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Enum, ForeignKey, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.api.company.models.company import Company


class ProductType(str, enum.Enum):
    GOOD = "Товар"
    SERVICE = "Услуга"


class Product(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    article: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[ProductType] = mapped_column(Enum(ProductType), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    images: Mapped[List[str]] = mapped_column(JSON, default=list)
    characteristics: Mapped[List[dict]] = mapped_column(JSON, default=list)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    unit_of_measurement: Mapped[str] = mapped_column(String(100))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="products")
