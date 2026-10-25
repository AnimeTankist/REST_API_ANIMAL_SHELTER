from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401  — регистрирует таблицы в Base.metadata
from .database import Base, engine
from .routers import animals


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


tags_metadata = [
    {
        "name": "Животные",
        "description": "CRUD, фильтрация по виду и статусу, поиск, сортировка, пагинация, статистика.",
    },
    {"name": "Служебные", "description": "Проверка работоспособности сервиса."},
]

app = FastAPI(
    title="API приюта для животных",
    description=(
        "REST API для учёта животных в приюте (Вариант 10).\n\n"
        "**Возможности:**\n"
        "- CRUD по животным;\n"
        "- фильтрация по виду, статусу и полу;\n"
        "- регистронезависимый поиск по кличке, породе и описанию;\n"
        "- сортировка и пагинация;\n"
        "- агрегированная статистика по приюту."
    ),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

# Фронтенд (Vite dev server) обращается к API с другого origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(animals.router)


@app.get("/health", tags=["Служебные"], summary="Проверка работоспособности")
def health_check() -> dict[str, str]:
    return {"status": "ok"}