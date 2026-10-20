"""Capa de sesión: soporta MySQL/MariaDB (pymysql) y PostgreSQL (psycopg)."""

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None

if settings.connect_database:
    connect_args = {}
    if settings.database_url.startswith("mysql"):
        connect_args = {"charset": "utf8mb4"}
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=1800,  # evita conexiones muertas en MySQL
        connect_args=connect_args,
    )
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def database_status() -> dict:
    dialect = settings.db_dialect
    return {
        "connect_database": settings.connect_database,
        "engine_created": engine is not None,
        "dialect": dialect,
        "host": settings.database_url.split("@")[-1] if "@" in settings.database_url else "localhost",
        "message": (
            "Conexión deshabilitada."
            if not settings.connect_database
            else f"Conexión habilitada ({dialect})."
        ),
    }


def get_db() -> Generator[Session | None, None, None]:
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ping_database() -> bool:
    if engine is None:
        return False
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
