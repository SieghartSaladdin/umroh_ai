import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from ai_umroh.utils.logger import get_logger

logger = get_logger("database.connection")

# Use a local SQLite database file
DATABASE_URL = "sqlite:///database.db"

# Create Database Engine
logger.info(f"Initializing database engine with URL: {DATABASE_URL}")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Essential for multi-threaded/async contexts like WhatsApp bots
)

# Create scoped session factory
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

# Declarative Base for models
Base = declarative_base()

def get_db():
    """
    Dependency helper to provide a clean database session and close it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
