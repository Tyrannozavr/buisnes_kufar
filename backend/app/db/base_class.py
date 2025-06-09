from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy import Column, Integer

class Base:
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)

Base = declarative_base(cls=Base)