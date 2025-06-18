from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)