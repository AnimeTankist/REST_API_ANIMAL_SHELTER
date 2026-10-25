"""Операции доступа к данным (CRUD) для животных приюта.

Pydantic-схемы запросов и ответов находятся в ``app/schemas.py``,
здесь — только работа с БД через SQLAlchemy.
"""

from datetime import date, timedelta
from typing import Any, Literal

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from . import models, schemas

#: Поля, по которым разрешена сортировка в GET /animals.
SORT_COLUMNS = {
    "id": models.Animal.id,
    "name": models.Animal.name,
    "age_months": models.Animal.age_months,
    "arrival_date": models.Animal.arrival_date,
    "created_at": models.Animal.created_at,
    "status": models.Animal.status,
}


def _escape_like(value: str) -> str:
    """Экранирует служебные символы LIKE (%, _ и обратный слэш)."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _apply_filters(
    stmt: Select,
    *,
    species: models.Species | None,
    status: models.Status | None,
    gender: models.Gender | None,
    search: str | None,
    min_age: int | None,
    max_age: int | None,
) -> Select:
    """Добавляет к запросу фильтры по виду/статусу/полу, поиск и диапазон возраста."""
    if species is not None:
        stmt = stmt.where(models.Animal.species == species)
    if status is not None:
        stmt = stmt.where(models.Animal.status == status)
    if gender is not None:
        stmt = stmt.where(models.Animal.gender == gender)
    if min_age is not None:
        stmt = stmt.where(models.Animal.age_months >= min_age)
    if max_age is not None:
        stmt = stmt.where(models.Animal.age_months <= max_age)
    if search:
        # py_lower() регистрируется в app.database: встроенный lower() SQLite
        # не работает с кириллицей, поэтому поиск регистронезависимый для любого текста.
        pattern = f"%{_escape_like(search.strip().lower())}%"
        stmt = stmt.where(
            or_(
                func.py_lower(models.Animal.name).like(pattern, escape="\\"),
                func.py_lower(models.Animal.breed).like(pattern, escape="\\"),
                func.py_lower(models.Animal.description).like(pattern, escape="\\"),
            )
        )
    return stmt


def list_animals(
    db: Session,
    *,
    species: models.Species | None = None,
    status: models.Status | None = None,
    gender: models.Gender | None = None,
    search: str | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    sort_by: str = "id",
    order: Literal["asc", "desc"] = "asc",
    limit: int = 10,
    offset: int = 0,
) -> tuple[int, list[models.Animal]]:
    """Возвращает кортеж ``(общее количество по фильтру, страница животных)``."""
    stmt = _apply_filters(
        select(models.Animal),
        species=species,
        status=status,
        gender=gender,
        search=search,
        min_age=min_age,
        max_age=max_age,
    )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    column = SORT_COLUMNS.get(sort_by, models.Animal.id)
    ordering = column.asc() if order == "asc" else column.desc()
    # id — второй ключ сортировки, чтобы пагинация была стабильной при равных значениях
    page = stmt.order_by(ordering, models.Animal.id).limit(limit).offset(offset)
    return total, list(db.scalars(page).all())


def get_animal(db: Session, animal_id: int) -> models.Animal | None:
    """Возвращает животное по id (или ``None``, если записи нет)."""
    return db.get(models.Animal, animal_id)


def create_animal(db: Session, payload: schemas.AnimalCreate) -> models.Animal:
    """Создаёт животное; незаполненные поля получают значения по умолчанию модели."""
    data = payload.model_dump(exclude_unset=True, exclude_none=True)
    animal = models.Animal(**data)
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal


def update_animal(db: Session, animal: models.Animal, data: dict[str, Any]) -> models.Animal:
    """Применяет переданные поля к животному и сохраняет изменения.

    ``None`` для NOT NULL колонок игнорируется: так PUT без ``arrival_date``
    не затирает дату поступления (у неё есть значение по умолчанию в модели),
    при этом PATCH по-прежнему может очищать nullable-поля.
    """
    columns = models.Animal.__table__.columns
    for field, value in data.items():
        column = columns.get(field)
        if column is None or (value is None and not column.nullable):
            continue
        setattr(animal, field, value)
    db.commit()
    db.refresh(animal)
    return animal


def delete_animal(db: Session, animal: models.Animal) -> None:
    """Удаляет животное из базы."""
    db.delete(animal)
    db.commit()


def get_stats(db: Session) -> dict[str, Any]:
    """Считает агрегированную статистику по приюту."""
    total = db.scalar(select(func.count()).select_from(models.Animal)) or 0

    by_species = {
        (species.value if species is not None else "unknown"): count
        for species, count in db.execute(
            select(models.Animal.species, func.count()).group_by(models.Animal.species)
        ).all()
    }
    by_status = {
        (status.value if status is not None else "unknown"): count
        for status, count in db.execute(
            select(models.Animal.status, func.count()).group_by(models.Animal.status)
        ).all()
    }

    avg_age = db.scalar(select(func.avg(models.Animal.age_months)))
    since = date.today() - timedelta(days=30)
    adopted_last_30_days = db.scalar(
        select(func.count())
        .select_from(models.Animal)
        .where(
            models.Animal.status == models.Status.adopted,
            models.Animal.adopted_date >= since,
        )
    ) or 0

    return {
        "total": total,
        "by_species": by_species,
        "by_status": by_status,
        "average_age_months": round(float(avg_age), 1) if avg_age is not None else None,
        "adopted_last_30_days": adopted_last_30_days,
    }
