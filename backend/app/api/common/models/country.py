from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.api.common.models.federal_district import FederalDistrict
    from app.api.common.models.region import Region
    from app.api.common.models.city import City
    from app.api.company.models.company import Company


class Country(Base):
    """Модель для стран"""
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)  # ISO код страны (RU, BY, KZ)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    federal_districts: Mapped[list["FederalDistrict"]] = relationship("FederalDistrict", back_populates="country")
    regions: Mapped[list["Region"]] = relationship("Region", back_populates="country")
    cities: Mapped[list["City"]] = relationship("City", back_populates="country")

    def __repr__(self):
        return f"<Country(id={self.id}, code='{self.code}', name='{self.name}')>"
