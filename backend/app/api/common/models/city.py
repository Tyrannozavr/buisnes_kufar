from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.api.common.models.country import Country
    from app.api.common.models.federal_district import FederalDistrict
    from app.api.common.models.region import Region
    from app.api.company.models.company import Company


class City(Base):
    """Модель для городов"""
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id"), nullable=False)
    region_id: Mapped[int] = mapped_column(Integer, ForeignKey("regions.id"), nullable=False)
    federal_district_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("federal_districts.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Население для фильтрации
    is_million_city: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Город-миллионник
    is_regional_center: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Региональный центр
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    country: Mapped["Country"] = relationship("Country", back_populates="cities")
    region: Mapped["Region"] = relationship("Region", back_populates="cities")
    federal_district: Mapped[Optional["FederalDistrict"]] = relationship("FederalDistrict", back_populates="cities")

    def __repr__(self):
        return f"<City(id={self.id}, name='{self.name}', population={self.population})>"
