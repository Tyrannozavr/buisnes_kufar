from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.api.common.models.country import Country
    from app.api.common.models.federal_district import FederalDistrict
    from app.api.common.models.city import City
    from app.api.company.models.company import Company


class Region(Base):
    """Модель для регионов/областей"""
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id"), nullable=False)
    federal_district_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("federal_districts.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)  # Код региона
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    country: Mapped["Country"] = relationship("Country", back_populates="regions")
    federal_district: Mapped[Optional["FederalDistrict"]] = relationship("FederalDistrict", back_populates="regions")
    cities: Mapped[list["City"]] = relationship("City", back_populates="region")

    def __repr__(self):
        return f"<Region(id={self.id}, name='{self.name}', code='{self.code}')>"
