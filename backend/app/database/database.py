from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import os
import logging
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cloud SQL configuration
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME", "win-job-devops-scraper:southamerica-east1:devops-jobs-dev")
DB_USER = os.getenv("DB_USER", "app_user") 
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "devops_jobs")

logger.info(f"Cloud SQL Connection: {INSTANCE_CONNECTION_NAME}")
logger.info(f"Database: {DB_NAME}, User: {DB_USER}")

def getconn():
    """Create a connection to Cloud SQL using the Cloud SQL Python Connector."""
    connector = Connector()
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
    )
    return conn

# Create engine with Cloud SQL Connector or fallback to SQLite
try:
    # Check if we have Cloud SQL configuration
    if INSTANCE_CONNECTION_NAME and DB_PASSWORD and not DB_PASSWORD == "":
        logger.info("Using Cloud SQL Connector for PostgreSQL connection")
        engine = create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        logger.info("Cloud SQL PostgreSQL engine created successfully")
    else:
        raise Exception("Cloud SQL configuration incomplete - missing credentials")
        
except Exception as e:
    logger.error(f"Failed to create Cloud SQL engine: {e}")
    logger.info("Falling back to SQLite for development")
    
    # SQLite fallback for development
    engine = create_engine(
        "sqlite:///./devops_jobs.db",
        connect_args={"check_same_thread": False}
    )
    logger.info("SQLite engine created successfully")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()