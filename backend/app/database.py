"""
Database Configuration and Session Management
SQLAlchemy setup for MySQL connection
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Test connection before using
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for models
Base = declarative_base()

def get_db() -> Session:
    """
    Dependency function to get database session
    Used in FastAPI endpoint dependencies
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Event listeners for connection management
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set MySQL-specific options on connection"""
    try:
        # Enable strict mode for MySQL
        cursor = dbapi_conn.cursor()
        cursor.execute("SET sql_mode='STRICT_TRANS_TABLES'")
        cursor.close()
    except Exception as e:
        logger.warning(f"Failed to set MySQL pragma: {e}")

@event.listens_for(engine, "engine_disposed")
def receive_engine_disposed(engine):
    """Log when engine is disposed"""
    logger.info("Database engine disposed")
