from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from backend.config import settings

if settings.use_sqlite:
    DATABASE_URL = "sqlite:///./dev.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    # Enable WAL mode and foreign key enforcement for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()
else:
    DATABASE_URL = (
        f"mssql+pyodbc://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_server}/{settings.db_name}"
        f"?driver={settings.db_driver.replace(' ', '+')}"
        f"&TrustServerCertificate=yes"
        f"&Encrypt=yes"
    )
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        fast_executemany=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """FastAPI dependency — yields a database session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables defined via SQLAlchemy models. Used in dev / tests."""
    Base.metadata.create_all(bind=engine)
