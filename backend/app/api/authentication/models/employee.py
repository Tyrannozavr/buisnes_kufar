from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class EmployeeRole(str, enum.Enum):
    OWNER = "owner"  # Владелец компании
    ADMIN = "admin"  # Администратор
    USER = "user"    # Обычный пользователь


class EmployeeStatus(str, enum.Enum):
    PENDING = "pending"      # Ожидает регистрации
    ACTIVE = "active"        # Активный сотрудник
    INACTIVE = "inactive"    # Неактивный сотрудник
    DELETED = "deleted"      # Удаленный сотрудник


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    
    # Связь с пользователем
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Может быть null если еще не зарегистрирован
    
    # Связь с компанией
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Данные сотрудника
    email = Column(String, nullable=False, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    patronymic = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    position = Column(String, nullable=True)
    
    # Роль и статус
    role = Column(Enum(EmployeeRole), default=EmployeeRole.USER, nullable=False)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.PENDING, nullable=False)
    
    # Права доступа (JSON строка с правами)
    permissions = Column(Text, nullable=True)  # JSON строка с правами
    
    # Для удаления администраторов
    deletion_requested_at = Column(DateTime(timezone=True), nullable=True)
    deletion_requested_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deletion_rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    company = relationship("Company")
    deletion_requested_by_user = relationship("User", foreign_keys=[deletion_requested_by])
    created_by_user = relationship("User", foreign_keys=[created_by])


class EmployeePermission(Base):
    __tablename__ = "employee_permissions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    permission_key = Column(String, nullable=False)  # Например: "company_management", "documents", etc.
    granted = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employee = relationship("Employee")
