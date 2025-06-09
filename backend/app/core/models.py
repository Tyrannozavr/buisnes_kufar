from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Enum, ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
# import aiohttp
import os
from pathlib import Path
import uuid
import mimetypes

from app.db.base_class import Base
from app.core.config import settings



class BaseUser(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
