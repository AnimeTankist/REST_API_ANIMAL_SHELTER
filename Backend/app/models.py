import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Species(str, enum.Enum):
    """Вид животного."""
    dog = "dog"
    cat = "cat"
    rabbit = "rabbit"
    bird = "bird"
    rodent = "rodent"
    other = "other"


class Gender(str, enum.Enum):
    """Пол животного."""
    male = "male"
    female = "female"
    unknown = "unknown"


class Status(str, enum.Enum):
    """Статус животного в приюте."""
    available = "available"   # ищет хозяина
    reserved = "reserved"     # забронировано
    treatment = "treatment"   # на лечении
    adopted = "adopted"       # передано хозяину


class Animal(Base):
    """Основная сущность — животное в приюте."""

    __tablename__ = "animals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    species: Mapped[Species] = mapped_column(SAEnum(Species), index=True)
    breed: Mapped[str | None] = mapped_column(String(80))
    gender: Mapped[Gender] = mapped_column(SAEnum(Gender), default=Gender.unknown)
    age_months: Mapped[int] = mapped_column(Integer)
    status: Mapped[Status] = mapped_column(
        SAEnum(Status), default=Status.available, index=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    arrival_date: Mapped[date] = mapped_column(Date, default=date.today)
    adopted_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )