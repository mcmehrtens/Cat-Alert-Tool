"""The cat DB model."""

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from cat_alert_tool.cat import Gender


class Base(DeclarativeBase):
    """Boiler-plate ORM configuration for SQLAlchemy."""


class CatORM(Base):
    """An ORM mapping for Cat objects to the cat DB."""

    __tablename__ = "cats"
    id: Mapped[str] = mapped_column(String(7), primary_key=True)
    name: Mapped[str | None]
    gender: Mapped[Gender | None]
    color: Mapped[str | None]
    breed: Mapped[str | None]
    age: Mapped[int | None]
    url: Mapped[str | None]
    image: Mapped[str | None]
