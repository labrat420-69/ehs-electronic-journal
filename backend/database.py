"""
Database configuration and setup
Supports PostgreSQL, MS SQL Server, and SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database type selection from environment variable
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()

# Database URL configuration based on type
if DATABASE_TYPE == "mssql" or DATABASE_TYPE == "sqlserver":
    # MS SQL Server configuration
    DB_SERVER = os.getenv("MSSQL_SERVER", "localhost")
    DB_PORT = os.getenv("MSSQL_PORT", "1433")
    DB_NAME = os.getenv("MSSQL_DATABASE", "ehs_electronic_journal")
    DB_USER = os.getenv("MSSQL_USER", "ehs_user")
    DB_PASSWORD = os.getenv("MSSQL_PASSWORD", "ehs_password")
    DB_DRIVER = os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")
    
    DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}?driver={DB_DRIVER.replace(' ', '+')}&TrustServerCertificate=yes"
    
elif DATABASE_TYPE == "postgresql" or DATABASE_TYPE == "postgres":
    # PostgreSQL configuration
    DB_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DATABASE", "ehs_electronic_journal")
    DB_USER = os.getenv("POSTGRES_USER", "ehs_user")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ehs_password")
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"
    
else:
    # SQLite configuration (default for development)
    # Use path that works both locally and in Docker
    import os
    if os.path.exists("/app"):
        # Running in Docker
        db_path = os.getenv("DATABASE_PATH", "/app/ehs_journal.db")
    else:
        # Running locally
        db_path = os.getenv("DATABASE_PATH", "./ehs_journal.db")
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")

# Override with direct DATABASE_URL if provided
DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_URL)

# SQLAlchemy engine configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
elif DATABASE_URL.startswith("mssql"):
    # MS SQL Server specific configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
else:
    # PostgreSQL and other databases
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )

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