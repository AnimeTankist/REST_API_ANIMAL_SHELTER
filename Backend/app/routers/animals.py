from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..models import Gender, Species, Status

router = APIRouter(prefix="/animals", tags=["Животные"])

DbSession = Annotated[Session, Depends(get_db)]

NOT_FOUND = {404: {"description": "Животное не найдено"}}


# ---------------------------------------------------------------- READ (list)
@router.get(
    "",
    response_model=schemas.AnimalPage,
    summary="Список животных (фильтрация, поиск, сортировка, пагинация)",
)
def list_animals(
    db: DbSession,
    species: Annotated[Species | None, Query(description="Фильтр по виду")] = None,
    status: Annotated[Status | None, Query(description="Фильтр по статусу")] = None,
    gender: Annotated[Gender | None, Query(description="Фильтр по полу")] = None,
    search: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=50,
            description="Поиск по кличке, породе или описанию (регистронезависимый)",
        ),
    ] = None,
    min_age: Annotated[int | None, Query(ge=0, le=600, description="Возраст от, мес.")] = None,
    max_age: Annotated[int | None, Query(ge=0, le=600, description="Возраст до, мес.")] = None,
    sort_by: Annotated[
        Literal["id", "name", "age_months", "arrival_date", "created_at", "status"],
        Query(description="Поле сортировки"),
    ] = "id",
    order: Annotated[Literal["asc", "desc"], Query(description="Направление сортировки")] = "asc",
    limit: Annotated[int, Query(ge=1, le=100, description="Размер страницы")] = 10,
    offset: Annotated[int, Query(ge=0, description="Смещение")] = 0,
) -> schemas.AnimalPage:
    if min_age is not None and max_age is not None and min_age > max_age:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_age не может быть больше max_age",
        )

    total, items = crud.list_animals(
        db,
        species=species,
        status=status,
        gender=gender,
        search=search,
        min_age=min_age,
        max_age=max_age,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
    )
    return schemas.AnimalPage(total=total, limit=limit, offset=offset, items=items)


# ------------------------------------------------------------- READ (stats)
# ВАЖНО: статический маршрут объявлен раньше /{animal_id}, иначе "stats" попадёт в path-параметр
@router.get(
    "/stats",
    response_model=schemas.ShelterStats,
    summary="Агрегированная статистика по приюту",
)
def get_stats(db: DbSession) -> schemas.ShelterStats:
    return schemas.ShelterStats(**crud.get_stats(db))


# ---------------------------------------------------------------- READ (one)
@router.get(
    "/{animal_id}",
    response_model=schemas.AnimalRead,
    summary="Получить животное по id",
    responses=NOT_FOUND,
)
def get_animal(animal_id: int, db: DbSession) -> schemas.AnimalRead:
    animal = crud.get_animal(db, animal_id)
    if animal is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Животное не найдено"
        )
    return animal


# ------------------------------------------------------------------- CREATE
@router.post(
    "",
    response_model=schemas.AnimalRead,
    status_code=http_status.HTTP_201_CREATED,
    summary="Добавить животное",
)
def create_animal(payload: schemas.AnimalCreate, db: DbSession) -> schemas.AnimalRead:
    return crud.create_animal(db, payload)


# ------------------------------------------------------------------- UPDATE
@router.put(
    "/{animal_id}",
    response_model=schemas.AnimalRead,
    summary="Полностью обновить животное",
    responses=NOT_FOUND,
)
def replace_animal(
    animal_id: int, payload: schemas.AnimalUpdate, db: DbSession
) -> schemas.AnimalRead:
    animal = crud.get_animal(db, animal_id)
    if animal is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Животное не найдено"
        )
    return crud.update_animal(db, animal, payload.model_dump())


@router.patch(
    "/{animal_id}",
    response_model=schemas.AnimalRead,
    summary="Частично обновить животное",
    responses=NOT_FOUND,
)
def patch_animal(
    animal_id: int, payload: schemas.AnimalPatch, db: DbSession
) -> schemas.AnimalRead:
    animal = crud.get_animal(db, animal_id)
    if animal is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Животное не найдено"
        )
    return crud.update_animal(db, animal, payload.model_dump(exclude_unset=True))


# ------------------------------------------------------------------- DELETE
@router.delete(
    "/{animal_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Удалить животное",
    responses=NOT_FOUND,
)
def delete_animal(animal_id: int, db: DbSession) -> None:
    animal = crud.get_animal(db, animal_id)
    if animal is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Животное не найдено"
        )
    crud.delete_animal(db, animal)


# -------------------------------------------------------------- BUSINESS OP
@router.post(
    "/{animal_id}/adopt",
    response_model=schemas.AnimalRead,
    summary="Передать животное новому хозяину",
    responses={**NOT_FOUND, 409: {"description": "Животное уже передано"}},
)
def adopt_animal(animal_id: int, db: DbSession) -> schemas.AnimalRead:
    animal = crud.get_animal(db, animal_id)
    if animal is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Животное не найдено"
        )
    if animal.status == Status.adopted:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Животное уже передано новому хозяину",
        )
    return crud.update_animal(
        db, animal, {"status": Status.adopted, "adopted_date": date.today()}
    )