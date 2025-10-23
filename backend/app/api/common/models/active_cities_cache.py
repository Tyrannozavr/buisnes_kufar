from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ActiveCitiesCache(Base):
    """Модель для кэша активных городов"""
    __tablename__ = "active_cities_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Тип кэша (products, services)
    cache_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Список ID активных городов (города, где есть компании с продуктами/услугами)
    active_city_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False, default=list)
    
    # Статистика
    total_cities: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_companies: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_products: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Метаданные
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Время создания
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    def __repr__(self):
        return f"<ActiveCitiesCache(id={self.id}, type={self.cache_type}, cities={len(self.active_city_ids)})>"


class ProductCityMapping(Base):
    """Модель для связи продуктов с городами (для быстрого поиска)"""
    __tablename__ = "product_city_mapping"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # ID продукта
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # ID города компании
    city_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # ID компании
    company_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ProductCityMapping(product_id={self.product_id}, city_id={self.city_id})>"
