from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./devops_jobs.db")

logger.info(f"Database URL configured: {DATABASE_URL[:50]}...")

# Validate and fix database URL if needed
def validate_database_url(url: str) -> str:
    """Validate and fix common Cloud SQL URL format issues."""
    
    if not url.startswith("postgresql"):
        return url
    
    # Check for malformed connection string (common Cloud SQL issue)
    if ":southamerica-east1:" in url and "?host=" not in url:
        logger.warning("Detected malformed Cloud SQL URL format - attempting to fix")
        # This is the old format that causes the port parsing error
        # Transform it to the correct Unix socket format
        parts = url.split("@")
        if len(parts) == 2:
            user_pass = parts[0]  # postgresql://user:pass
            host_db = parts[1]    # host:region:instance/database
            
            if ":" in host_db and "/" in host_db:
                # Extract database name
                db_name = host_db.split("/")[-1]
                # Extract connection name (everything before the slash)
                connection_name = host_db.split("/")[0]
                
                # Build correct Unix socket URL
                fixed_url = f"{user_pass}@/{db_name}?host=/cloudsql/{connection_name}"
                logger.info(f"Fixed URL format for Cloud SQL Unix socket connection")
                return fixed_url
    
    return url

# Validate and fix URL
DATABASE_URL = validate_database_url(DATABASE_URL)

# Create engine with proper error handling
try:
    if DATABASE_URL.startswith("postgresql"):
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        logger.info("PostgreSQL engine created successfully")
except Exception as e:
    logger.error(f"Failed to create PostgreSQL engine: {e}")
    logger.info("Falling back to SQLite for development")
    DATABASE_URL = "sqlite:///./devops_jobs.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
if not DATABASE_URL.startswith("postgresql"):
    # SQLite for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )
    logger.info("SQLite engine created successfully")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()