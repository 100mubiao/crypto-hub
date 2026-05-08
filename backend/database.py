import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.config import settings

logger = logging.getLogger("database")

db_url = settings.database_url

# Render uses postgres:// but SQLAlchemy needs postgresql://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Handle empty or invalid database URL
if not db_url or db_url.strip() in ("", "None"):
    logger.warning("DATABASE_URL is empty, falling back to SQLite")
    db_url = "sqlite:///./crypto_hub.db"

is_sqlite = db_url.startswith("sqlite")

logger.info("connecting to database: %s", "sqlite" if is_sqlite else "postgresql")

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if is_sqlite:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
