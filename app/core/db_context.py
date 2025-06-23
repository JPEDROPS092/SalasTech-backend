"""
Simple database configuration for SalasTech API
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import CONFIG

# Create database engine
engine = create_engine(
    CONFIG.DB_CONNECTION_STRING,
    echo=False,  # Set to True for development debugging
    pool_pre_ping=True
)

# Session factory
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Base class for models
Base = declarative_base()

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)