from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.api.common.models.country import Country
    from app.api.common.models.region import Region
    from app.api.common.models.city import City
    from app.api.company.models.company import Company


class FederalDistrict(Base):
    """Модель для федеральных округов"""
    __tablename__ = "federal_districts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)  # Код округа (ЦФО, СЗФО, etc.)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    country: Mapped["Country"] = relationship("Country", back_populates="federal_districts")
    regions: Mapped[list["Region"]] = relationship("Region", back_populates="federal_district")
    cities: Mapped[list["City"]] = relationship("City", back_populates="federal_district")

    def __repr__(self):
        return f"<FederalDistrict(id={self.id}, name='{self.name}', code='{self.code}')>"
