from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class CompanyOfficial(Base):
    __tablename__ = "company_officials"

    position: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Foreign keys
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="officials") 