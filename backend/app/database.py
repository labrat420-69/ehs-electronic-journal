"""
Database configuration and setup
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable or default for development
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://ehs_user:ehs_password@localhost:5432/ehs_electronic_journal"
)

# SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)