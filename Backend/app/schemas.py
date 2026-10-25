from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .models import Gender, Species, Status


class AnimalBase(BaseModel):
    """Общие поля животного + валидация."""

    name: str = Field(..., min_length=1, max_length=50, examples=["Барсик"])
    species: Species = Field(..., examples=["cat"])
    breed: str | None = Field(default=None, max_length=80, examples=["Домашняя короткошёрстная"])
    gender: Gender = Field(default=Gender.unknown)
    age_months: int = Field(..., ge=0, le=600, description="Возраст в месяцах", examples=[18])
    status: Status = Field(default=Status.available)
    description: str | None = Field(default=None, max_length=1000)
    arrival_date: date | None = Field(default=None, description="Дата поступления (по умолчанию — сегодня)")
    adopted_date: date | None = Field(default=None, description="Дата передачи новому хозяину")

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Кличка не может быть пустой")
        return value

    @field_validator("arrival_date", "adopted_date")
    @classmethod
    def _date_not_in_future(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Дата не может быть в будущем")
        return value

    @model_validator(mode="after")
    def _check_dates_order(self):
        if (
            self.arrival_date
            and self.adopted_date
            and self.adopted_date < self.arrival_date
        ):
            raise ValueError("Дата передачи не может быть раньше даты поступления")
        return self


class AnimalCreate(AnimalBase):
    """Тело запроса на создание животного."""


class AnimalUpdate(AnimalBase):
    """Тело запроса на полное обновление (PUT)."""


class AnimalPatch(BaseModel):
    """Тело запроса на частичное обновление (PATCH) — все поля опциональны."""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    species: Species | None = None
    breed: str | None = Field(default=None, max_length=80)
    gender: Gender | None = None
    age_months: int | None = Field(default=None, ge=0, le=600)
    status: Status | None = None
    description: str | None = Field(default=None, max_length=1000)
    arrival_date: date | None = None
    adopted_date: date | None = None

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Кличка не может быть пустой")
        return value

    @field_validator("arrival_date", "adopted_date")
    @classmethod
    def _date_not_in_future(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Дата не может быть в будущем")
        return value


class AnimalRead(AnimalBase):
    """Ответ API по одному животному."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AnimalPage(BaseModel):
    """Страница списка животных."""

    total: int = Field(..., description="Всего записей по фильтру")
    limit: int
    offset: int
    items: list[AnimalRead]


class ShelterStats(BaseModel):
    """Агрегированная статистика по приюту."""

    total: int = Field(..., description="Всего животных в базе")
    by_species: dict[str, int] = Field(..., description="Количество по видам")
    by_status: dict[str, int] = Field(..., description="Количество по статусам")
    average_age_months: float | None = Field(..., description="Средний возраст, мес.")
    adopted_last_30_days: int = Field(..., description="Передано хозяевам за 30 дней")