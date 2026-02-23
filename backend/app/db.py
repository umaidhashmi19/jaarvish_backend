from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

# Create the SQLAlchemy engine connected to Supabase PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # Checks connection health before each use
    pool_size=10,                # Number of persistent connections
    max_overflow=20,             # Extra connections beyond pool_size
    pool_recycle=1800,           # Recycle connections every 30 minutes
    echo=settings.DEBUG,         # Log SQL statements in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Declarative base for all ORM models
class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables that don't yet exist in the database."""
    # Import all models so SQLAlchemy registers them before creating tables
    # from app.models import user  # noqa: F401

    Base.metadata.create_all(bind=engine)