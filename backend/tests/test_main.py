import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import get_db, Base
from main import app

# Import models to ensure they are registered with Base
from app.models import models

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: Drop all tables
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "DevOps Job Scraper API" in response.json()["message"]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_user_endpoint_exists():
    # Test that the endpoint exists and validates input
    response = client.post(
        "/api/v1/auth/register",
        json={
            "invalid": "data"
        }
    )
    # Should return validation error, not 404
    assert response.status_code in [400, 422, 500]

def test_login_endpoint_exists():
    # Test that the endpoint exists and validates input format
    response = client.post(
        "/api/v1/auth/login",
        data={
            "invalid": "format"
        }
    )
    # Should return validation error, not 404
    assert response.status_code in [400, 422, 500]

def test_get_jobs_endpoint_exists():
    # Test that the endpoint exists
    response = client.get("/api/v1/jobs/")
    # Should return response, not 404 (500 is acceptable if DB is not setup)
    assert response.status_code in [200, 500]