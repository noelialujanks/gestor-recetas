from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.config import configuracion

engine = create_engine(
    configuracion.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Clase base para todos los modelos de SQLAlchemy."""


def obtener_db() -> Generator[Session, None, None]:
    """Provee una sesion de base de datos para cada peticion de la API."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
