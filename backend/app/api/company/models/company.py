import enum
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Enum, ForeignKey, Text, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class TradeActivity(str, enum.Enum):
    BUYER = "Покупатель"
    SELLER = "Продавец"
    BOTH = "Покупатель и продавец"


class BusinessType(str, enum.Enum):
    GOODS = "Производство товаров"
    SERVICES = "Оказание услуг"
    BOTH = "Производство товаров и оказание услуг"


if TYPE_CHECKING:
    from app.api.company.models.official import CompanyOfficial
    from app.api.authentication.models import User
    from app.api.products.models import Product
    from app.api.company.models.announcement import Announcement
    from app.api.chats.models.chat_participant import ChatParticipant
    from app.api.messages.models import Message


class Company(Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    logo: Mapped[Optional[str]] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    trade_activity: Mapped[TradeActivity] = mapped_column(Enum(TradeActivity), nullable=False)
    business_type: Mapped[BusinessType] = mapped_column(Enum(BusinessType), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Location
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    federal_district: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)

    # Legal information
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), unique=True, nullable=True)
    ogrn: Mapped[Optional[str]] = mapped_column(String(15), unique=True, nullable=True)
    kpp: Mapped[Optional[str]] = mapped_column(String(9), nullable=False)
    registration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    legal_address: Mapped[str] = mapped_column(String(255), nullable=False)
    production_address: Mapped[Optional[str]] = mapped_column(String(255))

    # Contact information
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255))

    # Statistics
    total_views: Mapped[int] = mapped_column(default=0)
    monthly_views: Mapped[int] = mapped_column(default=0)
    total_purchases: Mapped[int] = mapped_column(default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="company")
    officials: Mapped[List["CompanyOfficial"]] = relationship("CompanyOfficial", back_populates="company",
                                                              cascade="all, delete-orphan")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="company", cascade="all, delete-orphan")
    announcements: Mapped[List["Announcement"]] = relationship("Announcement", back_populates="company",
                                                               cascade="all, delete-orphan")
    # Chat relationships
    chat_participants: Mapped[List["ChatParticipant"]] = relationship("ChatParticipant", back_populates="company")
    sent_messages: Mapped[List["Message"]] = relationship("Message", foreign_keys="Message.sender_company_id",
                                                          back_populates="sender_company")

    def __str__(self):
        return self.name


class CompanyRelationType(str, enum.Enum):
    SUPPLIER = "supplier"
    BUYER = "buyer"
    PARTNER = "partner"


class CompanyRelation(Base):
    __tablename__ = "company_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)  # Владелец
    related_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)  # Другая компания
    relation_type: Mapped[CompanyRelationType] = mapped_column(Enum(CompanyRelationType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Опционально: связи для удобства
    company: Mapped["Company"] = relationship("Company", foreign_keys=[company_id], backref="relations_from")
    related_company: Mapped["Company"] = relationship("Company", foreign_keys=[related_company_id],
                                                      backref="relations_to")
