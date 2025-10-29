"""
Database connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from config.settings import Settings

# Base class for models
Base = declarative_base()

# Global variables
engine = None
SessionLocal = None


def init_database():
    """
    Initialize database engine and session factory.
    """
    global engine, SessionLocal
    
    settings = Settings()
    
    # Create engine
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
        echo=False
    )
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine


def get_db() -> Session:
    """
    Get database session.
    
    Yields:
        Database session
    """
    if SessionLocal is None:
        init_database()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.
    """
    from .models import Tender, TenderDetail, Document, ExtractedField, ScrapeLog
    
    if engine is None:
        init_database()
    
    Base.metadata.create_all(bind=engine)

