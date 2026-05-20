import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import ArgumentError

from backend.config import settings

logger = logging.getLogger("database")

db_url = settings.database_url

print(f"[startup] DATABASE_URL from env: '{db_url}'", flush=True)

# Render uses postgres:// but SQLAlchemy needs postgresql://
if isinstance(db_url, str) and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Handle empty or invalid database URL
if not db_url or not isinstance(db_url, str) or db_url.strip() in ("", "None"):
    print("[startup] DATABASE_URL is empty/invalid, falling back to SQLite", flush=True)
    db_url = "sqlite:///./crypto_hub.db"

is_sqlite = db_url.startswith("sqlite")

print(f"[startup] connecting to database: {'sqlite' if is_sqlite else 'postgresql'}", flush=True)

try:
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if is_sqlite else {},
        pool_pre_ping=True,
    )
except ArgumentError as e:
    print(f"[startup] Failed to parse database URL '{db_url}': {e}", flush=True)
    print("[startup] Falling back to SQLite", flush=True)
    db_url = "sqlite:///./crypto_hub.db"
    is_sqlite = True
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
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


def run_migrations():
    """Add missing columns to existing tables for schema evolution."""
    import sqlalchemy as sa
    inspector = sa.inspect(engine)
    conn = engine.connect()

    # users.theme
    if "theme" not in {c["name"] for c in inspector.get_columns("users")}:
        if is_sqlite:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN theme VARCHAR DEFAULT 'default'"))
        else:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS theme VARCHAR DEFAULT 'default'"))
        conn.commit()
        logger.info("Migration: added users.theme column")

    conn.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
