from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./shelter.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Базовый класс для ORM-моделей."""


@event.listens_for(engine, "connect")
def _register_sqlite_functions(dbapi_connection, _connection_record):
    """
    Встроенный lower() в SQLite не работает с кириллицей,
    поэтому регистрируем Python-реализацию для регистронезависимого поиска.
    """
    dbapi_connection.create_function(
        "py_lower", 1, lambda value: value.lower() if isinstance(value, str) else value
    )


def get_db():
    """Зависимость FastAPI: сессия БД на время запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()