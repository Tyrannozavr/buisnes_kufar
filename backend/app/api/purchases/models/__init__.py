import enum
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Enum, ForeignKey, Text, DateTime, Boolean, Float, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class OrderStatus(str, enum.Enum):
    ACTIVE = "Активная"
    COMPLETED = "Завершенная"


class OrderType(str, enum.Enum):
    GOODS = "Товары"
    SERVICES = "Услуги"


class UnitOfMeasurement(Base):
    """Единицы измерения с кодами ОКЕИ"""
    __tablename__ = "units_of_measurement"

    name: Mapped[str] = mapped_column(String(100), nullable=False)  # Наименование
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)  # Условное обозначение
    code: Mapped[str] = mapped_column(String(10), nullable=False)  # Код ОКЕИ

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return f"{self.name} ({self.symbol})"


if TYPE_CHECKING:
    from app.api.company.models.company import Company
    from app.api.products.models.product import Product


class Order(Base):
    """Заказ - основная сущность для документооборота"""
    __tablename__ = "orders"

    # Основная информация
    buyer_order_number: Mapped[str] = mapped_column(String(20), nullable=False)  # Номер заказа покупателя (00000)
    seller_order_number: Mapped[str] = mapped_column(String(20), nullable=False)  # Номер заказа продавца (00000)
    deal_type: Mapped[OrderType] = mapped_column(Enum(OrderType), nullable=False)  # Тип заказа (товары/услуги)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.ACTIVE)
    
    # Стороны сделки
    buyer_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    seller_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    
    # Связанные документы (номера)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(20))  # Номер счета
    contract_number: Mapped[Optional[str]] = mapped_column(String(20))  # Номер договора
    invoice_date: Mapped[Optional[datetime]] = mapped_column(DateTime)  # Дата счета
    contract_date: Mapped[Optional[datetime]] = mapped_column(DateTime)  # Дата договора
    
    # Дополнительная информация
    comments: Mapped[Optional[str]] = mapped_column(Text)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)  # Общая сумма заказа
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    buyer_company: Mapped["Company"] = relationship("Company", foreign_keys=[buyer_company_id], backref="buyer_orders")
    seller_company: Mapped["Company"] = relationship("Company", foreign_keys=[seller_company_id], backref="seller_orders")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    order_history: Mapped[List["OrderHistory"]] = relationship("OrderHistory", back_populates="order", cascade="all, delete-orphan")

    def __str__(self):
        return f"Заказ {self.buyer_order_number}"


class OrderItem(Base):
    """Позиция в заказе"""
    __tablename__ = "order_items"

    # Связь с заказом
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    
    # Информация о продукте
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), nullable=True)  # Может быть null для ручного ввода
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Наименование товара/услуги
    product_slug: Mapped[Optional[str]] = mapped_column(String(255))  # Slug продукта
    product_description: Mapped[Optional[str]] = mapped_column(Text)  # Описание
    product_article: Mapped[Optional[str]] = mapped_column(String(100))  # Артикул
    product_type: Mapped[Optional[str]] = mapped_column(String(50))  # Тип продукта
    logo_url: Mapped[Optional[str]] = mapped_column(String(255))  # URL логотипа
    
    # Количественные характеристики
    quantity: Mapped[float] = mapped_column(Float, nullable=False)  # Количество
    unit_of_measurement: Mapped[str] = mapped_column(String(50), nullable=False)  # Единица измерения
    price: Mapped[float] = mapped_column(Float, nullable=False)  # Цена за единицу
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # Сумма (quantity * price)
    
    # Позиция в заказе
    position: Mapped[int] = mapped_column(Integer, nullable=False)  # Позиция в списке
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped[Optional["Product"]] = relationship("Product")

    def __str__(self):
        return f"{self.product_name} - {self.quantity} {self.unit_of_measurement}"


class OrderHistory(Base):
    """История изменений заказа для отслеживания изменений обеими сторонами"""
    __tablename__ = "order_history"

    # Связь с заказом
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    
    # Информация об изменении
    changed_by_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)  # Кто изменил
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Тип изменения (created, updated, etc.)
    change_description: Mapped[str] = mapped_column(Text, nullable=False)  # Описание изменения
    
    # Данные до и после изменения (JSON)
    old_data: Mapped[Optional[dict]] = mapped_column(JSON)  # Данные до изменения
    new_data: Mapped[Optional[dict]] = mapped_column(JSON)  # Данные после изменения
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_history")
    changed_by_company: Mapped["Company"] = relationship("Company")

    def __str__(self):
        return f"Изменение в заказе {self.order_id} от {self.changed_by_company_id}"


class OrderDocument(Base):
    """Документы, связанные с заказом (счета, договоры, акты и т.д.)"""
    __tablename__ = "order_documents"

    # Связь с заказом
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    
    # Информация о документе
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Тип документа (invoice, contract, act, etc.)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)  # Номер документа
    document_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # Дата документа
    
    # Содержимое документа
    document_content: Mapped[Optional[dict]] = mapped_column(JSON)  # Содержимое документа в JSON
    document_file_path: Mapped[Optional[str]] = mapped_column(String(500))  # Путь к файлу документа
    
    # Статус документа
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)  # Отправлен ли контрагенту
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)  # Дата отправки
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order: Mapped["Order"] = relationship("Order")

    def __str__(self):
        return f"{self.document_type} {self.document_number} от {self.document_date.strftime('%d.%m.%Y')}"
